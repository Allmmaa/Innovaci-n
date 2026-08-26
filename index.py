from my import supabase

try:
    # Intenta consultar la tabla Usuario
    respuesta = supabase.table("Usuario").select("*").execute()
    print("¡Conexión exitosa a la base de datos!")
    print("Datos actuales de usuarios:", respuesta.data)
except Exception as e:
    print("Error al conectar con Supabase:", e)