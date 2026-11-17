import mysql.connector
import os
import time


def conectar_citas():
    for intento in range(10):
        try:
            conexion = mysql.connector.connect(
                host=os.getenv("CITA_DB_HOST"),
                port=int(os.getenv("CITA_DB_PORT")),
                user=os.getenv("CITA_DB_USER"),
                password=os.getenv("CITA_DB_PASSWORD"),
                database=os.getenv("CITA_DB_NAME")
            )
            return conexion
        except mysql.connector.Error as error:
            print(f"Base de datos de citas aun no disponible: {error}")
            time.sleep(5)
        
    raise Exception("No se pudo conectar a la base de datos de citas despues de 10 intentos")

