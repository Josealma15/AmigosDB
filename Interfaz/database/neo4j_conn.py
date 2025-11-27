from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "admin123")

# Crear driver de conexión
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)


# ============================================================
# MIGRAR JSON → NEO4J
# ============================================================

def migrar_json_a_neo4j(datos):
    driver = get_driver()

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        # Usuarios
        for u in datos["usuarios"]:
            session.run("""
                MERGE (p:Persona {id_sql: $id})
                SET p.nombre = $nombre,
                    p.email = $email
            """, id=u["id"], nombre=u["nombre"], email=u["email"])

        # Amistades — solo aceptadas
        for a in datos["amistades"]:
            if a.get("estado", "ACEPTADA") == "ACEPTADA":
                session.run("""
                    MATCH (p1:Persona {id_sql: $id1})
                    MATCH (p2:Persona {id_sql: $id2})
                    MERGE (p1)-[:AMIGO_DE]->(p2)
                """, id1=a["id1"], id2=a["id2"])

        # Publicaciones
        for p in datos.get("publicaciones", []):
            session.run("""
                MERGE (po:Post {id_sql: $id})
                SET po.contenido = $contenido
            """, id=p["id"], contenido=p["texto"])

            session.run("""
                MATCH (u:Persona {id_sql: $autor})
                MATCH (po:Post {id_sql: $id})
                MERGE (u)-[:PUBLICO]->(po)
            """, autor=p["autor"], id=p["id"])

    driver.close()
    print("Migración JSON → Neo4j completada.")


# ============================================================
# MIGRAR POSTGRES → NEO4J
# ============================================================

from database.postgres import (
    obtener_usuarios,
    obtener_amistades,
    obtener_publicaciones
)

def migrar_desde_postgres():
    driver = get_driver()

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    # Usuarios
    usuarios = obtener_usuarios()
    with driver.session() as session:
        for u in usuarios:
            session.run("""
                MERGE (p:Persona {id_sql: $id})
                SET p.nombre = $nombre,
                    p.email = $email
            """, id=u[0], nombre=u[1], email=u[2])

    # Amistades aceptadas
    amistades = obtener_amistades()
    with driver.session() as session:
        for a in amistades:
            if a[3] == "ACEPTADA":
                session.run("""
                    MATCH (p1:Persona {id_sql: $id1})
                    MATCH (p2:Persona {id_sql: $id2})
                    MERGE (p1)-[:AMIGO_DE]->(p2)
                """, id1=a[4], id2=a[5])

    # Publicaciones
    posts = obtener_publicaciones()
    with driver.session() as session:
        for p in posts:
            session.run("""
                MERGE (po:Post {id_sql: $id})
                SET po.contenido = $texto
            """, id=p[0], texto=p[1])

            session.run("""
                MATCH (u:Persona {id_sql: $autor})
                MATCH (po:Post {id_sql: $id})
                MERGE (u)-[:PUBLICO]->(po)
            """, autor=p[2], id=p[0])

    driver.close()
    print("Migración completa PostgreSQL → Neo4j.")


# ============================================================
# MIGRAR NEO4J → POSTGRES
# ============================================================

from database.postgres import (
    crear_usuario,
    crear_publicacion,
    actualizar_estado_amistad,
    obtener_amistades,
    crear_amistad_procedure,
    obtener_usuario_por_email
)

def migrar_neo4j_a_postgres():
    driver = get_driver()

    with driver.session() as session:

        # ============================================================
        # 1. Migrar usuarios desde Neo4j → PostgreSQL
        # ============================================================
        usuarios_neo = session.run("""
            MATCH (p:Persona)
            RETURN p.id_sql AS id_neo, p.nombre AS nombre, p.email AS email
        """)

        # Crear usuarios y construir mapeo de IDs Neo4j → PostgreSQL
        id_mapping = {}  # {id_neo: id_postgres}
        
        for u in usuarios_neo:
            id_neo = u["id_neo"]
            email = u["email"]
            nombre = u["nombre"]
            
            try:
                # Intentar crear el usuario
                crear_usuario(nombre, email, "Desconocido")
                print(f"Usuario creado: {nombre} ({email})")
            except Exception as e:
                if "duplicate key" not in str(e).lower():
                    print(f"Error inesperado en usuario {nombre}:", e)
            
            # Obtener el ID real de PostgreSQL usando el email
            usuario_pg = obtener_usuario_por_email(email)
            if usuario_pg:
                id_postgres = usuario_pg[0]
                id_mapping[id_neo] = id_postgres
                print(f"Mapeo ID: Neo4j {id_neo} → PostgreSQL {id_postgres} ({email})")
            else:
                print(f"ADVERTENCIA: No se pudo mapear usuario con email {email}")

        # ============================================================
        # 2. Migrar amistades usando IDs mapeados
        # ============================================================
        amistades_neo = session.run("""
            MATCH (a:Persona)-[:AMIGO_DE]->(b:Persona)
            RETURN a.id_sql AS id1_neo, b.id_sql AS id2_neo, a.email AS email1, b.email AS email2
        """)

        amistades_pg = obtener_amistades()

        def existe_amistad_pg(id1, id2):
            """Verifica si ya existe una amistad entre dos usuarios en PostgreSQL"""
            for am in amistades_pg:
                if (am[4] == id1 and am[5] == id2) or (am[4] == id2 and am[5] == id1):
                    return am[0]  # retorna id_amistad
            return None

        for a in amistades_neo:
            id1_neo = a["id1_neo"]
            id2_neo = a["id2_neo"]
            email1 = a["email1"]
            email2 = a["email2"]

            # Mapear IDs de Neo4j a PostgreSQL
            id1_pg = id_mapping.get(id1_neo)
            id2_pg = id_mapping.get(id2_neo)

            # Verificar que ambos usuarios existan en el mapeo
            if id1_pg is None or id2_pg is None:
                print(f"Amistad ignorada: {email1} ↔ {email2} (usuarios no mapeados)")
                continue

            # Verificar si la amistad ya existe
            existente = existe_amistad_pg(id1_pg, id2_pg)
            if existente:
                actualizar_estado_amistad(existente, "ACEPTADA")
                print(f"Amistad actualizada: {email1} ↔ {email2}")
            else:
                # Crear nueva amistad con IDs correctos de PostgreSQL
                try:
                    crear_amistad_procedure(id1_pg, id2_pg)
                    print(f"Amistad creada: {email1} ↔ {email2} (PG IDs: {id1_pg} ↔ {id2_pg})")
                except Exception as e:
                    print(f"Error creando amistad {email1} ↔ {email2}:", e)

        # ============================================================
        # 3. Migrar publicaciones usando IDs mapeados
        # ============================================================
        publicaciones = session.run("""
            MATCH (u:Persona)-[:PUBLICO]->(p:Post)
            RETURN p.contenido AS texto, u.id_sql AS autor_neo, u.email AS autor_email
        """)

        for p in publicaciones:
            autor_neo = p["autor_neo"]
            autor_email = p["autor_email"]
            texto = p["texto"]

            # Mapear ID del autor de Neo4j a PostgreSQL
            autor_pg = id_mapping.get(autor_neo)

            if autor_pg is None:
                print(f"Publicación ignorada (autor {autor_email} no mapeado)")
                continue

            try:
                crear_publicacion(texto, autor_pg)
                print(f"Publicación creada para {autor_email} (PG ID: {autor_pg})")
            except Exception as e:
                if "duplicate key" not in str(e).lower():
                    print(f"Error inesperado en publicación de {autor_email}:", e)

    driver.close()

    print("✅ Migración Neo4j → PostgreSQL completada con mapeo de IDs.")






# ============================================================
# RECOMENDACIONES DE AMIGOS (FRIENDS OF FRIENDS)
# ============================================================

def obtener_recomendaciones_amigos(id_usuario):
    """
    Obtiene recomendaciones de amigos basadas en amigos de amigos.
    Retorna personas que son amigas de mis amigos pero no son mis amigos directos.
    """
    driver = get_driver()
    recomendaciones = []
    
    with driver.session() as session:
        resultado = session.run("""
            MATCH (yo:Persona {id_sql: $id_usuario})-[:AMIGO_DE]-(amigo:Persona)-[:AMIGO_DE]-(recomendado:Persona)
            WHERE NOT (yo)-[:AMIGO_DE]-(recomendado)
              AND yo <> recomendado
            RETURN DISTINCT recomendado.id_sql AS id, 
                   recomendado.nombre AS nombre, 
                   recomendado.email AS email,
                   COUNT(DISTINCT amigo) AS amigos_en_comun
            ORDER BY amigos_en_comun DESC
        """, id_usuario=id_usuario)
        
        for record in resultado:
            recomendaciones.append({
                'id': record['id'],
                'nombre': record['nombre'],
                'email': record['email'],
                'amigos_en_comun': record['amigos_en_comun']
            })
    
    driver.close()
    return recomendaciones

