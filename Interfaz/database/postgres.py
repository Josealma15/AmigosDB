import psycopg2

# Configuración de PostgreSQL
PG_CONFIG = {
    'dbname': 'red_social_db',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost'
}

def get_connection():
    return psycopg2.connect(**PG_CONFIG)

# USUARIOS
def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre, email, pais FROM usuarios ORDER BY id_usuario")
    datos = cursor.fetchall()
    conn.close()
    return datos

def crear_usuario(nombre, email, pais):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, pais) VALUES (%s, %s, %s)",
        (nombre, email, pais)
    )
    conn.commit()
    conn.close()

def actualizar_usuario(id_usuario, nombre, email, pais):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nombre=%s, email=%s, pais=%s WHERE id_usuario=%s",
        (nombre, email, pais, id_usuario)
    )
    conn.commit()
    conn.close()

def eliminar_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    conn.commit()
    conn.close()

def obtener_usuario_por_email(email):
    """Obtener usuario por email (para mapeo de IDs desde Neo4j)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre, email, pais FROM usuarios WHERE email=%s", (email,))
    datos = cursor.fetchone()
    conn.close()
    return datos

# AMISTADES
def obtener_amistades():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id_amistad,
               u1.nombre AS solicitante,
               u2.nombre AS receptor,
               a.estado,
               a.usuario_solicitante_id,
               a.usuario_receptor_id
        FROM amistades a
        JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
        JOIN usuarios u2 ON a.usuario_receptor_id = u2.id_usuario
        ORDER BY a.id_amistad
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos

# Procedimiento almacenado para crear amistad
def crear_amistad_procedure(id1, id2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT crear_amistad(%s, %s)", (id1, id2))
    mensaje = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return mensaje

# Actualizar estado de amistad (ACEPTADA, RECHAZADA, BLOQUEADA, ELIMINADA, etc.)
def actualizar_estado_amistad(id_amistad, estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE amistades
        SET estado = %s
        WHERE id_amistad = %s
    """, (estado, id_amistad))
    conn.commit()
    conn.close()

# Eliminar amistad (NO borra, solamente la marca como eliminada)
def eliminar_amistad(id_amistad):
    actualizar_estado_amistad(id_amistad, "ELIMINADA")

# Obtener amistades de un usuario específico
def obtener_amistades_por_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id_amistad,
            CASE 
                WHEN a.usuario_solicitante_id = %s THEN u2.nombre
                ELSE u1.nombre
            END AS amigo_nombre,
            CASE 
                WHEN a.usuario_solicitante_id = %s THEN u2.email
                ELSE u1.email
            END AS amigo_email,
            a.estado,
            a.fecha_amistad,
            a.usuario_solicitante_id
        FROM amistades a
        JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
        JOIN usuarios u2 ON a.usuario_receptor_id = u2.id_usuario
        WHERE 
            a.usuario_solicitante_id = %s
            OR 
            a.usuario_receptor_id = %s
        ORDER BY a.id_amistad;
    """, (id_usuario, id_usuario, id_usuario, id_usuario))

    datos = cursor.fetchall()
    conn.close()
    return datos

# PUBLICACIONES
def obtener_feed():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, contenido, fecha, total_comentarios FROM feed_noticias")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_publicaciones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_publicacion, texto_contenido, autor_id
        FROM publicaciones
        ORDER BY id_publicacion
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos

def crear_publicacion(texto, autor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publicaciones (texto_contenido, autor_id)
        VALUES (%s, %s)
    """, (texto, autor_id))
    conn.commit()
    conn.close()

def actualizar_publicacion(id_publicacion, texto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE publicaciones
        SET texto_contenido = %s
        WHERE id_publicacion = %s
    """, (texto, id_publicacion))
    conn.commit()
    conn.close()

def eliminar_publicacion(id_publicacion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM publicaciones WHERE id_publicacion = %s", (id_publicacion,))
    conn.commit()
    conn.close()

