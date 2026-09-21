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
    nueva_mascota = request.get_json()
    if "nombre" not in nueva_mascota or "especie" not in nueva_mascota:
        return jsonify({"mensaje":"El campo del nombre es obligatorio"}), 400

    nueva_mascota["id"] = len(mascotas) + 1
    mascotas.append(nueva_mascota)

    return jsonify(nueva_mascota), 201


@app.route("/mascotas/<int:id>", methods=["DELETE"])
def eliminar_mascota(id):
    for mascota in mascotas:
        if mascota["id"] == id:
            mascotas.remove(mascota)
            return jsonify({"mensaje":"Mascota eliminado "})
    return jsonify({"mensaje":"Mascota no encotrado"})


@app.route("/mascotas/<int:id>", methods=["PUT"])
def actualizar_mascota(id):
    nuevos_datos = request.get_json()
    for mascota in mascotas:
        if mascota["id"] == id:
            mascota["nombre"] = nuevos_datos.get("nombre", mascota["nombre"])
            mascota["especie"] = nuevos_datos.get("especie", mascota["especie"])
            return jsonify(mascota) 
    return jsonify({"mensaje":"N se pudo actualizar"})

# cita 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


