import os
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from my import (
    supabase,
    obtener_usuarios,
    obtener_aplicaciones,
    obtener_registro_accesos,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)


# ---------- Decoradores ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("es_admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ---------- Rutas públicas ----------
@app.route("/")
@app.route("/index.html")
def home():
    apps_data = obtener_aplicaciones() or []
    users_data = obtener_usuarios() or []
    accesos_data = obtener_registro_accesos() or []

    sectores_unicos = {a.get("sector") for a in apps_data if a.get("sector")}

    return render_template(
        "index.html",
        num_apps=len(apps_data),
        num_usuarios=len(users_data),
        num_accesos=len(accesos_data),
        num_sectores=len(sectores_unicos),
    )


@app.route("/aplicaciones")
def aplicaciones():
    apps_list = obtener_aplicaciones() or []
    return render_template("aplicaciones.html", apps=apps_list)


@app.route("/usar_app", methods=["POST"])
@login_required
def usar_app():
    """Registra un nuevo acceso en Supabase y redirige a la lista de accesos."""
    id_app = request.form.get("id_aplicacion")
    usuario_id = session.get("usuario_id")

    print(f"--- INTENTANDO REGISTRAR ACCESO --- Usuario: {usuario_id} | App: {id_app}")

    if id_app and usuario_id:
        try:
            # Convertimos ambos IDs a enteros explícitamente
            datos_insert = {
                "id_usuario": int(usuario_id),
                "id_aplicacion": int(id_app),
                "fecha_acceso": datetime.now().isoformat(),
                "tipo_servicio": "Web"
            }
            
            respuesta = supabase.table("Acceso").insert(datos_insert).execute()
            print("RESPUESTA DE SUPABASE AL INSERTAR --->", respuesta.data)

        except Exception as e:
            print("⚠️ ERROR AL REGISTRAR ACCESO EN SUPABASE:", e)

    return redirect(url_for("accesos"))


# ---------- Rutas para Usuarios / Admins ----------
@app.route("/usuarios")
@app.route("/usuarios.html")
@admin_required
def usuarios():
    users_list = obtener_usuarios() or []
    return render_template("usuarios.html", usuarios=users_list)


@app.route("/accesos")
@app.route("/accesos.html")
@login_required
def accesos():
    # Si es Administrador, trae el historial completo de accesos
    if session.get("es_admin"):
        accesos_list = obtener_registro_accesos() or []
    else:
        # Si es Empleado, trae únicamente sus propios accesos desde Supabase
        usuario_id = session.get("usuario_id")
        respuesta = (
            supabase.table("Acceso")
            .select(
                "id_usuario, id_aplicacion, fecha_acceso, tipo_servicio, "
                "Usuario(nombre, email, rol), "
                "aplicacion(nombre, sector)"
            )
            .eq("id_usuario", usuario_id)
            .execute()
        )
        accesos_list = respuesta.data or []

    return render_template("accesos.html", accesos=accesos_list)


# ---------- Autenticación ----------
@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        # Buscamos al usuario únicamente por su email en Supabase
        respuesta = (
            supabase.table("Usuario")
            .select("*")
            .eq("email", email)
            .execute()
        )

        if respuesta and respuesta.data and len(respuesta.data) > 0:
            usuario = respuesta.data[0]
            
            # Verificación de contraseña
            contraseña_correcta = (
                usuario.get("contraseña") == password 
                or check_password_hash(usuario.get("contraseña", ""), password)
            )

            if contraseña_correcta:
                session.clear()
                session["usuario_id"] = usuario.get("id_usuario") or usuario.get("id")
                session["usuario_nombre"] = usuario.get("nombre", "Usuario")
                
                # Leemos el rol real desde la base de datos ('admin' o 'empleado')
                rol = usuario.get("rol", "empleado").lower()
                session["rol"] = rol
                session["es_admin"] = (rol == "admin")

                return redirect(url_for("home"))

        return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)