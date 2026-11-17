from flask import Flask, request, jsonify
import requests, dotenv, os, pybreaker
from databasesc import conectar_consulta


dotenv.load_dotenv()

URL_MASCOTA = os.getenv("MASCOTAS_URL")
MASCOTAS_TIMEOUT = int(os.getenv("MASCOTAS_TIMEOUT", "2"))

app = Flask(__name__)

circuito_macotas = pybreaker.CircuitBreaker(
    
    fail_max = int(os.getenv("CB_MAX_FAILS", "3")),
    reset_timeout = int(os.getenv("CB_TIMEOUT", "10")),
    throw_new_error_on_trip = True
)


@app.route("/consultas", methods=["GET"])
def get_consultar():
   
    conexion = conectar_consulta()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM consultas")
    consultas = cursor.fetchall()
    cursor.close()
    return jsonify(consultas)



@app.route("/consultas", methods=["POST"])
def create_consulta():
    nueva_consulta = request.get_json()
    conexion = conectar_consulta()
    cursor = conexion.cursor(dictionary=True)
    
    sql = """INSERT INTO consultas(id, mascota_id, fecha, motivo, diagnostico, tratamiento, estado) values (%s, %s, %s, %s, %s, %s, %s)"""

    valores = (nueva_consulta["id"], nueva_consulta["mascota_id"], nueva_consulta["fecha"], nueva_consulta["motivo"], nueva_consulta["diagnostico"], nueva_consulta["tratamiento"], nueva_consulta["estado"])
    cursor.execute(sql,valores )
    cursor.commit()
    cursor.close()

    id_nuevo = cursor.lastrowid
    return jsonify({"mensaje": "Consulta creada", "id": id_nuevo}), 201


@app.route("/consultas/<int:id>", methods=["PUT"])
def update_consulta(id):
    nuevos_datos = request.get_json()
    conexion = conectar_consulta()
    cursor = conexion.cursor(dictionary=True)
    sql = """UPDATE consultas SET fecha = %s, motivo = %s, diagnostico = %s, tratamiento = %s, estado = %s WHERE id = %s"""
    valores = (nuevos_datos["fecha"], nuevos_datos["motivo"], nuevos_datos["diagnostico"], nuevos_datos["tratamiento"], nuevos_datos["estado"], id)

    cursor.execute(sql, valores)
    cursor.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje":"Consulta actualizada"}), 200


@app.route("/consultas/<int:id>", methods=["DELETE"])
def delete_consulta(id):
    conexion = conectar_consulta()
    cursor = conexion.cursor(dictionary=True)
    sql = """DELETE FROM consultas WHERE id = %s"""
    valores = (id,)
    cursor.execute(sql, valores)
    cursor.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje":"Consulta eliminada"}), 200



@app.route("/consultas/<int:id>/detalle", methods=["GET"])
def get_consultas_detalle(id):
    conexion = conectar_consulta()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM consultas WHERE id = %s", (id,))
    consulta = cursor.fetchone()
    cursor.close()
    conexion.close()

    if consulta is None:
        return jsonify({"mensaje": "Consulta no encontrada"}), 404

    try:
        with circuito_macotas.calling():
            respuesta = requests.get(
                f"{URL_MASCOTA}/mascotas/{consulta["mascota_id"]}", 
                timeout=MASCOTAS_TIMEOUT
            )

            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
                
    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "El servidor de mascotas no está disponible"}), 503

    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servidor de mascotas no respondió a tiempo"}), 504

    except  requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "El servidor de mascotas no está disponible"}), 503

    except requests.exceptions.HTTPError as error:
        return jsonify({"mensaje": f"Error en la solicitud al servidor de mascotas: {str(error)}"}), 502


    if respuesta.status_code == 404:
        return jsonify({"mensaje": "mascota no encontrado"}), 404
    
    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error en la solicitud al servidor de mascotas"}), 502
    
    mascotas_consulta = respuesta.json()

    return jsonify({
        "mascotas": mascotas_consulta["nombre"],
        "consulta": consulta
    }), 200


@app.route('/circuito/consulta', methods=["GET"])
def obtener_circuito():
    return jsonify(
        {
            "estado": circuito_macotas.current_state,
            "fallas_consecutivas": circuito_macotas.fail_counter,
            "maximo_de_fallas": circuito_macotas.fail_max,
            "espera_configurada_segundos": circuito_macotas.reset_timeout
        }), 200


   
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
