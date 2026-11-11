import os
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from my import (
    supabase,
    obtener_usuarios,
    obtener_aplicaciones,
    obtener_registro_accesos,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)


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


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")

        password_hashed = generate_password_hash(password)

        try:
            # Apuntamos a 'Usuario'
            respuesta = supabase.table("Usuario").insert({
                "nombre": nombre,
                "email": email,
                "password": password_hashed,
                "rol": "empleado" 
            }).execute()

            flash("¡Registro exitoso! Ya podés iniciar sesión.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            print(f"Error detallado de Supabase: {e}")
            flash("Ocurrió un error al registrar el usuario o el email ya existe.", "danger")
            return render_template("registro.html")

    return render_template("registro.html")


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
    if session.get("es_admin"):
        accesos_list = obtener_registro_accesos() or []
    else:
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Corregido a 'Usuario'
        respuesta = supabase.table("Usuario").select("*").eq("email", email).execute()
        usuarios = respuesta.data

        if not usuarios:
            flash("El correo no está registrado. Por favor, crea una cuenta.", "warning")
            return redirect(url_for("registro"))

        usuario = usuarios[0]

        if check_password_hash(usuario.get("password", ""), password):
            session["usuario_id"] = usuario["id_usuario"]
            session["nombre"] = usuario["nombre"]
            session["es_admin"] = (usuario.get("rol") == "admin")
            
            flash("¡Bienvenido/a!", "success")
            return redirect(url_for("home"))
        else:
            flash("Contraseña incorrecta.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)