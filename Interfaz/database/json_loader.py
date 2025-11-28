import json

from database.postgres import (
    crear_usuario,
    crear_publicacion,
    crear_amistad_procedure
)

# Cargar JSON desde archivo
def cargar_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Migrar JSON → PostgreSQL
def migrar_json_a_postgres(data):

    # Usuarios
    for u in data.get("usuarios", []):
        try:
            crear_usuario(u["nombre"], u["email"], u.get("pais", "Desconocido"))
        except Exception as e:
            if "duplicate key" not in str(e).lower():
                print("Error usuario:", e)

    # Amistades (siempre crear usando procedure)
    for a in data.get("amistades", []):
        id1 = a["id1"]
        id2 = a["id2"]
        try:
            crear_amistad_procedure(id1, id2)
        except Exception as e:
            if "duplicate key" not in str(e).lower():
                print("Error amistad:", e)

    # Publicaciones
    for p in data.get("publicaciones", []):
        try:
            crear_publicacion(p["texto"], p["autor"])
        except Exception as e:
            if "duplicate key" not in str(e).lower():
                print("Error publicacion:", e)

    print("Migración JSON → PostgreSQL completada.")
