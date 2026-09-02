from flask import Flask, render_template
from my import obtener_usuarios, obtener_aplicaciones, obtener_registro_accesos

app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route("/aplicaciones")
@app.route("/aplicaciones.html")
def aplicaciones():
    data = obtener_aplicaciones()
    return render_template("aplicaciones.html", apps=data.data)

@app.route("/usuarios")
@app.route("/usuarios.html")
def usuarios():
    data = obtener_usuarios()
    return render_template("usuarios.html", usuarios=data.data)

@app.route("/accesos")
@app.route("/accesos.html")
def accesos():
    data = obtener_registro_accesos()
    return render_template("accesos.html", accesos=data.data)

if __name__ == "__main__":
    app.run(debug=True)