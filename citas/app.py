from flask import Flask, request, jsonify
import requests, os, pybreaker
import dotenv
from databasescitas import conectar_citas

dotenv.load_dotenv()

MASCOTAS_URL = os.getenv("MASCOTAS_URL", "http://mascotas:5001")
MASCOTAS_TIMEOUT = int(os.getenv("MASCOTAS_TIMEOUT", "2"))

app = Flask(__name__)

circuito_mascotas = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FAILS", "3")),
    reset_timeout=int(os.getenv("CB_TIMEOUT", "30")),
    throw_new_error_on_trip=True
)


@app.route("/citas", methods=["GET"])
def obtener_citas():

    try:
        conexion = conectar_citas()
    except Exception:
        return jsonify({"mensaje": "Servicio despierto, pero la base de datos no esta disponible"}), 503

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM citas")
    citas = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    for cita in citas:
        cita["hora"] = str(cita["hora"])
        cita["fecha"] = str(cita["fecha"])
    return jsonify(citas), 200


@app.route("/citas", methods=["POST"])
def registrar_cita():
    
    datos_nuevos = request.get_json()
    campos = ["mascota_id", "fecha", "hora", "motivo"]
    for campo in campos:
        if campo not in datos_nuevos or not datos_nuevos[campo]:
            return jsonify({"mensaje": f"El campo '{campo}' es obligatorio"}), 400

    mascota_id = datos_nuevos["mascota_id"]

    
    try:
        with circuito_mascotas.calling():
            respuesta = requests.get(
                f"{MASCOTAS_URL}/mascotas/{mascota_id}",
                timeout=MASCOTAS_TIMEOUT
            )

            if respuesta.status_code >= 500:
                respuesta.raise_for_status()

    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "Servicio de Mascotas no disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servidor de Mascotas no respondio a tiempo"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "No se pudo conectar con el servicio de Mascotas"}), 503
    except requests.exceptions.HTTPError as error:
        return jsonify({"mensaje": f"Presento error en el servidor de Mascotas: {str(error)}"}), 502

    
    if respuesta.status_code == 404:
        return jsonify({"mensaje": "El servicio de mascota no encontrada"}), 404

    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error al consultar el servicio de Mascotas"}), 502

    try:
        conexion = conectar_citas()

    except Exception:
        return jsonify({"mensaje": "Servicio despierto, pero la base de datos no esta disponible"}), 503

    cursor = conexion.cursor(dictionary=True)
    sql = """INSERT INTO citas (mascota_id, fecha, hora, motivo) VALUES (%s, %s, %s, %s)"""
    valores = (mascota_id, datos_nuevos["fecha"], datos_nuevos["hora"], datos_nuevos["motivo"])
    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Cita registrada", "id": nuevo_id}), 201





@app.route("/citas/circuito", methods=["GET"])
def estado_circuito():
    return jsonify({
        "estado": circuito_mascotas.current_state,
        "contador_fallos": circuito_mascotas.fail_counter,
        "max_fallos": circuito_mascotas.fail_max,
        "tiempo_recuperacion": circuito_mascotas.reset_timeout
    }), 200



if __name__ == "__main__":
    app.run(debug=True, port=5004, host="0.0.0.0")
