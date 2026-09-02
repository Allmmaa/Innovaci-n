import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yczqvokerabfhuihreju.supabase.co")
# PEGA AQUÍ LA CLAVE CORRECTA QUE COPIASTE DE SUPABASE:
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_--MAkN6lsNqrfIJABtCV8w_zvTyUQ9e")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def obtener_usuarios():
    """Obtiene la lista de usuarios."""
    return supabase.table("Usuario").select("*").execute()


def obtener_aplicaciones():
    """Obtiene la lista de aplicaciones."""
    return supabase.table("aplicacion").select("*").execute()


def obtener_registro_accesos():
    """Obtiene el historial de accesos uniendo Usuario y aplicacion."""
    return supabase.table("Acceso").select(
        "id_usuario, id_aplicacion, fecha_acceso, tipo_servicio, "
        "Usuario(nombre, email), "
        "aplicacion(nombre, sector)"
    ).execute()