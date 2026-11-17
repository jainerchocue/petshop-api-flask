
import mysql.connector
import os #para obtener las variables de entorno
import time #para manejar el tiempo de espera

def conectar():
    for intento in range(10):
        try:
            conexion = mysql.connector.connect(
                host=os.getenv("PETSHOP_DB_HOST"),
                port=int(os.getenv("PETSHOP_DB_PORT")),
                user=os.getenv("PETSHOP_DB_USER"),
                password=os.getenv("PETSHOP_DB_PASSWORD"),
                database=os.getenv("PETSHOP_DB_NAME")
            )
            return conexion

        except mysql.connector.Error as error:
            print(f":a base de datos apenas esta cargando: {error}")
            intento += 1
            time.sleep(5)
