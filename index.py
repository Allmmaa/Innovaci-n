from flask import Flask, render_template, request, session, redirect, url_for
from my import (
    supabase,
    obtener_usuarios,
    obtener_aplicaciones,
    obtener_registro_accesos
)

app = Flask(__name__)
app.secret_key = "innovasoft"


@app.route("/")
@app.route("/index.html")
def home():
    # Obtener los datos desde Supabase
    apps_res = obtener_aplicaciones()
    users_res = obtener_usuarios()
    accesos_res = obtener_registro_accesos()

    # Extraer las listas de resultados (o lista vacía si hay error/None)
    apps_data = apps_res.data if apps_res and apps_res.data else []
    users_data = users_res.data if users_res and users_res.data else []
    accesos_data = accesos_res.data if accesos_res and accesos_res.data else []

    # Calcular las métricas
    num_apps = len(apps_data)
    num_usuarios = len(users_data)
    num_accesos = len(accesos_data)

    # Calcular sectores únicos a partir del campo 'sector' en aplicaciones
    sectores_unicos = {
        app.get("sector") for app in apps_data if app.get("sector")
    }
    num_sectores = len(sectores_unicos)

    return render_template(
        "index.html",
        num_apps=num_apps,
        num_usuarios=num_usuarios,
        num_accesos=num_accesos,
        num_sectores=num_sectores
    )


@app.route("/aplicaciones")
@app.route("/aplicaciones.html")
def aplicaciones():
    data = obtener_aplicaciones()
    apps_list = data.data if data else []
    return render_template("aplicaciones.html", apps=apps_list)


@app.route("/usuarios")
@app.route("/usuarios.html")
def usuarios():
    data = obtener_usuarios()
    users_list = data.data if data else []
    return render_template("usuarios.html", usuarios=users_list)


@app.route("/accesos")
@app.route("/accesos.html")
def accesos():
    data = obtener_registro_accesos()
    accesos_list = data.data if data else []
    return render_template("accesos.html", accesos=accesos_list)


@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_ingresado = request.form["email"]
        password_ingresada = request.form["password"]

        # Consultar la tabla Usuario en Supabase
        respuesta = supabase.table("Usuario") \
            .select("*") \
            .eq("email", email_ingresado) \
            .eq("contraseña", password_ingresada) \
            .execute()

        # Si coincide, crea la sesión y redirige al panel de inicio
        if respuesta and respuesta.data and len(respuesta.data) > 0:
            usuario = respuesta.data[0]
            session["admin"] = True
            session["usuario_nombre"] = usuario.get("nombre")
            return redirect(url_for("home"))

        # Si las credenciales fallan, envía el mensaje de error a login.html
        return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")
@app.route("/registro", methods=["GET", "POST"])
@app.route("/registro.html", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        contraseña = request.form["password"]

        # Comprobar si el correo ya está registrado
        usuario_existente = supabase.table("Usuario") \
            .select("*") \
            .eq("email", email) \
            .execute()

        if usuario_existente.data:
            return render_template(
                "registro.html",
                error="Ese correo ya está registrado"
            )

        # Crear el nuevo usuario
        supabase.table("Usuario").insert({
            "nombre": nombre,
            "email": email,
            "contraseña": contraseña
        }).execute()

        # Una vez registrado, volver al login
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    session.pop("usuario_nombre", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)