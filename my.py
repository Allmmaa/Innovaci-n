import os
from flask import Flask, render_template, session, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"  # Necesaria para manejar las sesiones de usuario

# 1. Configuración de conexión a Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yczqvokerabfhuihreju.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_--MAkN6lsNqrfIJABtCV8w_zvTyUQ9e")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Funciones de Base de Datos
def obtener_aplicaciones():
    try:
        respuesta = supabase.table("aplicacion").select("*").execute()
        return respuesta.data or []
    except Exception as e:
        print("Error al consultar aplicaciones:", e)
        return []

def obtener_usuarios():
    """Obtiene la lista completa de usuarios registrados desde Supabase."""
    try:
        respuesta = supabase.table("Usuario").select("*").execute()
        return respuesta.data or []
    except Exception as e:
        print("Error al consultar usuarios:", e)
        return []

def obtener_registro_accesos():
    """Obtiene el historial completo de accesos uniendo las tablas Usuario y Aplicacion."""
    try:
        response = supabase.table("Acceso").select(
            "id_usuario, id_aplicacion, fecha_acceso, tipo_servicio, "
            "Usuario(nombre, email, rol), "
            "aplicacion(nombre, sector)"
        ).execute()
        return response.data or []
    except Exception as e:
        print("Error al consultar accesos:", e)
        return []

# 3. Rutas de la Aplicación Web (Flask)

@app.route('/')
def home():
    """Página principal de la plataforma."""
    return render_template('index.html')

@app.route('/aplicaciones')
def aplicaciones():
    """Página que muestra el catálogo de aplicaciones traídas de Supabase."""
    apps = obtener_aplicaciones()
    print("DATOS DE SUPABASE --->", apps)
    return render_template('aplicaciones.html', apps=apps)

@app.route('/usar_app', methods=['POST'])
def usar_app():
    """Procesa la solicitud cuando un usuario hace clic en 'Usar aplicación'."""
    id_app = request.form.get('id_aplicacion')
    nombre_app = request.form.get('nombre_app')
    
    # Redirecciona a la lista de accesos o aplicaciones tras enviar el formulario
    return redirect(url_for('accesos'))

@app.route('/accesos')
def accesos():
    """Muestra los accesos globales (para Admin) o los accesos propios (para Empleado)."""
    lista_accesos = obtener_registro_accesos()
    
    usuario_actual = session.get('user_id')
    rol_actual = session.get('rol')
    
    # Si el usuario logueado es empleado, filtra para mostrar solo sus registros
    if rol_actual == 'empleado':
        lista_accesos = [a for a in lista_accesos if a.get('id_usuario') == usuario_actual]

    return render_template('accesos.html', accesos=lista_accesos, rol=rol_actual)

@app.route('/usuarios')
def usuarios():
    """Página para administración de usuarios (Exclusiva de Admin)."""
    lista_usuarios = obtener_usuarios()
    return render_template('usuarios.html', usuarios=lista_usuarios)

# 4. Inicialización del Servidor
if __name__ == '__main__':
    app.run(debug=True)