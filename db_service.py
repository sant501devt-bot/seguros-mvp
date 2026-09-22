import os
from supabase import create_client, Client

# 1. Cargar las credenciales desde el archivo .env
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Inicializar cliente de Supabase
supabase: Client = create_client(url, key)

def guardar_auditoria(proyecto_nombre: str, datos_json: dict):
    # Paso A: Crear o recuperar el proyecto
    res_proyecto = supabase.table("proyectos").insert({"nombre": proyecto_nombre}).execute()
    proyecto_id = res_proyecto.data[0]["id"]

    # Paso B: Insertar el análisis en la tabla 'auditorias'
    auditoria_data = {
        "proyecto_id": proyecto_id,
        "numero_poliza": datos_json.get("numero_poliza", "S/N"),
        "aseguradora": datos_json.get("aseguradora", "Desconocida"),
        "score_salud": datos_json.get("score_salud", 0),
        "resultado_completo": datos_json # Guarda todo el JSON estructurado
    }

    res_auditoria = supabase.table("auditorias").insert(auditoria_data).execute()
    print("¡Auditoría guardada exitosamente en Supabase!")
    return res_auditoria.data