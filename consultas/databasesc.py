import mysql.connector
import os
import time


def conectar_consulta():
    for intento in range(10):
        try:
            conexion = mysql.connector.connect(
                host=os.getenv("CONSULTAS_DB_HOST"),
                port=int(os.getenv("CONSULTAS_DB_PORT")),
                user=os.getenv("CONSULTAS_DB_USER"),
                password=os.getenv("CONSULTAS_DB_PASSWORD"),
                database=os.getenv("CONSULTAS_DB_NAME")
            )
            return conexion
        except mysql.connector.Error as error:
            print(f":a base de datos apenas esta cargando: {error}")
            time.sleep(5)

