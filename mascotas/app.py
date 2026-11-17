import json
from socket import timeout
from warnings import resetwarnings
from flask import Flask, jsonify, request
import requests, os, pybreaker
import time
import dotenv 
from database import conectar


dotenv.load_dotenv()



URL_USUARIOS = os.getenv("USUARIOS_URL")
USUARIO_TIMEOUT = int(os.getenv("USUARIOS_TIMEOUT", "2"))

app = Flask(__name__)

circuito_usuarios = pybreaker.CircuitBreaker(
    fail_max = int(os.getenv("CB_MAX_FAILS", "3")),
    reset_timeout = int(os.getenv("CB_TIMEOUT", "10")),
    throw_new_error_on_trip = True
)




@app.route("/mascotas", methods=["GET"])
def listar():
    conexion = conectar()
    cursor  = conexion.cursor(dictionary=True) # diccionary =True para que retorne un diccionario
    cursor.execute("SELECT * FROM mascotas")
    mascotas = cursor.fetchall() # fetchall() para que retorne todas las filas de la consulta
    cursor.close()
    return jsonify(mascotas)


@app.route("/mascotas/<int:id>", methods=["GET"])
def buscar(id):
    #time.sleep(5)
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
            SELECT * from  mascotas 
            where id = %s 
            """

    cursor.execute(sql, (id,))
    mascota = cursor.fetchone()
    cursor.close()
    if mascota is None:
        return jsonify({"mensaje":"Mascota no encontrado"}), 404
    return jsonify(mascota),200


@app.route("/mascotas", methods=["POST"])
def registrar():

    nueva_mascota = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        INSERT INTO mascotas (nombre, especie, usuario_id) VALUES (%s, %s, %s)
    
    """
    valores = (nueva_mascota["nombre"], nueva_mascota["especie"], nueva_mascota["usuario_id"])

    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    return jsonify({"mensaje":"mascota creada", "id": nuevo_id}), 201


@app.route("/mascotas/<int:id>", methods=["DELETE"])
def eliminar_mascota(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        DELETE FROM mascotas WHERE id = %s
    """
    cursor.execute(sql, (id,))
    filas = cursor.rowcount
    conexion.commit()
    cursor.close()
    if filas == 0:
        return jsonify({"mensaje": "Mascota no encontrada"}), 404
    return jsonify({"mensaje": "Mascota eliminada"}), 200


@app.route("/mascotas/<int:id>", methods=["PUT"])
def actualizar_mascota(id):
    nuevos_datos = request.get_json()
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        UPDATE mascotas SET nombre = %s, especie = %s WHERE id = %s
    """
    valores = (nuevos_datos.get("nombre"), nuevos_datos.get("especie"), id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    return jsonify({"mensaje":"Mascota actualizada"}), 200


@app.route("/mascotas/<int:id>", methods=["PATCH"])
def actualizacion_parcial(id):
    nuevos_datos = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True) 

    sql = """
        UPDATE mascotas SET nombre = %s, especie = %s WHERE id = %s
    """
    valores = (nuevos_datos.get("nombre"), nuevos_datos.get("especie"), id)
    cursor.execute(sql, valores)
    filas = cursor.rowcount
    conexion.commit()
    cursor.close()
    if filas == 0:
        return jsonify({"mensaje":"Mascota no encontrada"}), 404
    return jsonify({"mensaje":"Mascota actualizada"}), 200


@app.route("/mascotas/<int:id>/detalle")
def detalle_mascota(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mascotas WHERE id = %s", (id,))
    mascota = cursor.fetchone()
    cursor.close()
    conexion.close()

    if mascota is None:
        return jsonify({"mensaje": "Mascota no encontrada"}), 404

    try:
        with circuito_usuarios.calling():
            respuesta = requests.get(
                f"{URL_USUARIOS}/usuarios/{mascota['usuario_id']}",
                timeout=USUARIO_TIMEOUT
            )

            if respuesta.status_code >= 500:
                respuesta.raise_for_status()

    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "El servidor de usuarios no está disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servidor de usuarios no respondió a tiempo"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "El servidor de usuarios no está disponible"}), 503
    except requests.exceptions.HTTPError as error:
        return jsonify({
            "mensaje": f"Error en la solicitud al servidor de usuarios: {str(error)}"}), 502

    if respuesta.status_code == 404:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error en la solicitud al servidor de usuarios"}), 502

    usuario = respuesta.json()
    return jsonify({
        "mascota": mascota["nombre"],
        "especie": mascota["especie"],
        "usuario": usuario["nombre"]
    }), 200


@app.route("/circuito/usuarios", methods=["GET"])
def estado_circuito_usuarios():
    return jsonify({
        "estado": circuito_usuarios.current_state,
        "contador_fallos": circuito_usuarios.fail_counter,
        "contador_exitos": circuito_usuarios.fail_max,
        "tiempo_restante": circuito_usuarios.reset_timeout
    }), 200

# cita
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
