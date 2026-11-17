from flask import Flask, jsonify, request

app = Flask(__name__)

mascotas = [
    {"id": 1, "nombre": "max", "especie": "perro"},
    {"id": 2, "nombre": "Roberto", "especie": "perro"},
]


@app.route("/mascotas", methods=["GET"])
def listar():
    return jsonify(mascotas)


@app.route("/mascotas/<int:id>", methods=["GET"])
def buscar(id):
    for mascota in mascotas:
        if mascota["id"] == id:
            return jsonify(mascota)
    return jsonify({"mensaje": "mascota no encontrada"}), 404

@app.route("/mascotas", methods=["POST"])
def registrar():
    nueva_mascota = request.json()

    nueva_mascota["id"] = len(mascotas) + 1
    mascotas.append(nueva_mascota)

    return jsonify(nueva_mascota)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

