from flask import Flask, request, jsonify
import requests, os, pybreaker
import dotenv
import time
dotenv.load_dotenv()

URL_MASCOTA = os.getenv("MASCOTAS_URL")

app = Flask(__name__)


usuarios = [
    {
        "id":1,
        "nombre":"martin",
        "mascota_id":1
    },
    {
        "id":2,
        "nombre":"carmen",
        "mascota_id":2
    }
]


@app.route("/usuarios/<int:id>", methods=["GET"])
def buscar(id):
    #time.sleep(5)
    for usuario in usuarios:
        if usuario["id"] == id:
            return jsonify(usuario),200

    return jsonify({"mensaje":f"No esta el recuros con el id {id}"}),400

@app.route("/usuarios/<int:id>/detalle", methods=["GET"] )
def obtener_detalle_mascota_usuario(id):
    for usuario in usuarios:
        if usuario["id"] == id:
            respuesta = requests.get(
                f"{URL_MASCOTA}/mascotas/{usuario['mascota_id']}"
            )
            mascotas = respuesta.json()
            return jsonify({
                "usuario": usuario["nombre"],
                "mascota": mascotas["nombre"],
                "especie": mascotas["especie"]
            }),200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)


