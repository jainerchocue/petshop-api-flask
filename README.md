# Petshop API

API REST sencilla para administrar mascotas. Es un proyecto educativo construido con Flask y pensado para practicar los fundamentos de un servicio web: rutas HTTP, JSON, códigos de estado y operaciones CRUD.

> Estado: prototipo funcional en desarrollo.
>
> El proyecto se puede publicar como código abierto, siempre que se presente claramente este estado y no se use todavía como servicio de producción.

## Objetivo

El servicio permite:

- consultar todas las mascotas;
- consultar una mascota por su identificador;
- registrar una mascota;
- actualizar los datos de una mascota;
- eliminar una mascota.

La API representa cada mascota con esta estructura:

```json
{
  "id": 1,
  "nombre": "max",
  "especie": "perro"
}
```

## Guía rápida para la exposición

Puedes explicar el proyecto con esta idea central:

> Es una API REST hecha con Flask que permite hacer operaciones CRUD sobre una lista de mascotas. Recibe solicitudes HTTP, modifica los datos en memoria y responde en formato JSON.

### 1. Importaciones y creación de la aplicación

En `app.py` se importan tres elementos de Flask:

```python
from flask import Flask, jsonify, request
```

- `Flask` crea la aplicación web.
- `jsonify` convierte datos de Python en una respuesta JSON.
- `request` permite leer la información enviada por el cliente.

Después se crea la aplicación:

```python
app = Flask(__name__)
```

`__name__` le indica a Flask dónde está ubicada la aplicación y ayuda a localizar sus recursos.

### 2. Datos iniciales

```python
mascotas = [
  {"id": 1, "nombre": "max", "especie": "perro"},
  {"id": 2, "nombre": "Roberto", "especie": "perro"},
]
```

La variable es una lista de diccionarios. Cada diccionario representa una mascota. Es una base de datos temporal: se puede consultar y modificar mientras el programa está encendido, pero se pierde al reiniciar.

### 3. Cómo funcionan las rutas

El decorador `@app.route` conecta una dirección y un método HTTP con una función de Python. Por ejemplo:

```python
@app.route("/mascotas", methods=["GET"])
def listar():
  return jsonify(mascotas)
```

Cuando un cliente hace `GET /mascotas`, Flask ejecuta `listar`, toma la lista `mascotas` y la devuelve como JSON.

En la ruta `/mascotas/<int:id>`, `<int:id>` es un parámetro dinámico. Flask convierte el valor de la URL a entero y lo entrega a la función:

```python
@app.route("/mascotas/<int:id>", methods=["GET"])
def buscar(id):
```

La función recorre la lista, compara cada identificador con el solicitado y devuelve la mascota encontrada. Si termina el recorrido sin encontrarla, devuelve un mensaje y el código `404`.

### 4. Crear una mascota

En la ruta `POST /mascotas`, el cliente envía un cuerpo JSON. Esta línea lo convierte en un diccionario de Python:

```python
nueva_mascota = request.get_json()
```

Luego se comprueba que existan `nombre` y `especie`. La aplicación asigna un `id`, agrega la mascota a la lista con `append` y devuelve la nueva información con el código `201`, que significa que se creó un recurso.

### 5. Actualizar una mascota

La ruta `PUT /mascotas/<id>` recibe nuevos datos, busca la mascota y actualiza los campos enviados. El método `.get("nombre", mascota["nombre"])` significa: usar el nuevo nombre si llegó en la solicitud; si no, conservar el nombre anterior.

### 6. Eliminar una mascota

La ruta `DELETE /mascotas/<id>` busca la mascota y usa `mascotas.remove(mascota)` para quitarla de la lista. `DELETE` no necesita un cuerpo JSON porque el identificador de la URL indica qué elemento se debe eliminar.

### 7. Códigos HTTP usados

| Código | Significado en este proyecto |
| --- | --- |
| `200` | La operación terminó correctamente. |
| `201` | Se creó una mascota. |
| `400` | La solicitud no tiene los datos obligatorios. |
| `404` | No se encontró la mascota solicitada. |

### 8. Inicio del servidor

```python
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
```

La condición evita iniciar el servidor automáticamente cuando `app.py` se importa desde otro archivo. `host="0.0.0.0"` permite conexiones desde fuera del proceso, algo necesario dentro de Docker. `port=5000` define el puerto. `debug=True` ayuda durante el desarrollo porque muestra errores y recarga la aplicación, pero debe desactivarse en producción.

### 9. Cómo fluye una petición

Por ejemplo, al crear una mascota:

1. El cliente envía `POST /mascotas` con un JSON.
2. Flask encuentra la función asociada a esa ruta.
3. `request.get_json()` lee el cuerpo.
4. La aplicación valida los campos necesarios.
5. Se asigna un identificador y se modifica la lista.
6. `jsonify` prepara la respuesta.
7. Flask devuelve el JSON y el código `201`.

### 10. Preguntas que podrían hacerte

**¿Qué tipo de aplicación es?**

Es una API REST. No tiene una interfaz visual propia; recibe solicitudes HTTP y devuelve datos JSON.

**¿Qué significa CRUD?**

Significa `Create`, `Read`, `Update` y `Delete`: crear, consultar, actualizar y eliminar. En este proyecto corresponden a `POST`, `GET`, `PUT` y `DELETE`.

**¿Dónde se guardan los datos?**

En la lista `mascotas`, que vive en la memoria del proceso. Por eso los datos no sobreviven a un reinicio.

**¿Por qué se usa `jsonify`?**

Porque convierte objetos de Python a JSON y prepara correctamente la respuesta HTTP para que el cliente pueda interpretarla.

**¿Qué pasa si busco una mascota que no existe?**

La función termina sin encontrar coincidencias y devuelve un mensaje con código `404`.

**¿Por qué `POST` devuelve `201`?**

Porque la solicitud creó una nueva mascota. El código `201 Created` comunica explícitamente ese resultado.

**¿Este proyecto está listo para producción?**

No todavía. Es un prototipo educativo: necesita base de datos, pruebas, validaciones completas, autenticación y desactivar el modo debug.

**¿Qué mejorarías primero?**

Primero agregaría pruebas y validación de errores; después incorporaría una base de datos. Así se puede comprobar el comportamiento antes de cambiar el almacenamiento.

## `app.py` completo explicado

Este es el código actual de la aplicación. Conviene estudiar primero el código completo y después revisar la explicación de cada bloque.

```python
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
```

### Explicación línea por línea

#### Importaciones

```python
from flask import Flask, jsonify, request
```

- `from flask import`: indica que se van a traer elementos desde la biblioteca Flask.
- `Flask`: es la clase que permite crear la aplicación web.
- `jsonify`: transforma listas y diccionarios de Python en respuestas JSON.
- `request`: representa la solicitud que llega desde el cliente y permite leer su información.

#### Creación de la aplicación

```python
app = Flask(__name__)
```

- `app`: variable que guarda la aplicación Flask.
- `Flask(...)`: crea una instancia de la aplicación.
- `__name__`: variable especial de Python que identifica el módulo actual. Flask la usa para saber dónde está el proyecto.

#### Lista de mascotas

```python
mascotas = [
  {"id": 1, "nombre": "max", "especie": "perro"},
  {"id": 2, "nombre": "Roberto", "especie": "perro"},
]
```

- `mascotas`: lista que funciona como almacenamiento temporal.
- `[]`: representa una lista de Python.
- Cada `{}` es un diccionario con tres claves: `id`, `nombre` y `especie`.
- `id` identifica a la mascota; `nombre` y `especie` contienen sus datos.
- No es una base de datos. Todo vive en la memoria y se pierde cuando se apaga o reinicia el programa.

#### Endpoint para listar

```python
@app.route("/mascotas", methods=["GET"])
def listar():
  return jsonify(mascotas)
```

- `@app.route(...)`: decorador de Flask que conecta una URL con una función.
- `"/mascotas"`: dirección del endpoint.
- `methods=["GET"]`: permite solicitudes `GET`, que se usan para consultar información.
- `def listar():`: define la función que se ejecutará cuando llegue esa solicitud.
- `return jsonify(mascotas)`: devuelve toda la lista convertida a JSON.
- Si se visita `http://localhost:5000/mascotas`, se ejecuta esta función.

#### Endpoint para buscar una mascota

```python
@app.route("/mascotas/<int:id>", methods=["GET"])
def buscar(id):
  for mascota in mascotas:
    if mascota["id"] == id:
      return jsonify(mascota)
  return jsonify({"mensaje": "mascota no encontrada"}), 404
```

- `/<int:id>` es una parte dinámica de la URL. Por ejemplo, en `/mascotas/2`, el valor de `id` es `2`.
- `<int:id>` también obliga a que ese valor sea un número entero.
- `def buscar(id)`: recibe el identificador enviado en la URL.
- `for mascota in mascotas`: recorre una mascota a la vez.
- `mascota["id"]`: obtiene el identificador del elemento actual.
- `==`: compara el identificador de la lista con el solicitado.
- Si coinciden, se devuelve esa mascota y la función termina inmediatamente.
- Si el ciclo termina sin encontrarla, se devuelve un mensaje y `404 Not Found`.

#### Endpoint para registrar

```python
@app.route("/mascotas", methods=["POST"])
def registrar():
  nueva_mascota = request.get_json()
  if "nombre" not in nueva_mascota or "especie" not in nueva_mascota:
    return jsonify({"mensaje":"El campo del nombre es obligatorio"}), 400

  nueva_mascota["id"] = len(mascotas) + 1
  mascotas.append(nueva_mascota)

  return jsonify(nueva_mascota), 201
```

- Usa la misma URL `/mascotas`, pero con método `POST`, porque se está creando un recurso.
- `request.get_json()`: lee el cuerpo JSON enviado por el cliente y lo convierte en un diccionario.
- `if`: inicia una condición.
- `"nombre" not in nueva_mascota`: comprueba si falta la clave `nombre`.
- `or`: significa “o”; la condición también se cumple si falta `especie`.
- Si falta algún campo, se devuelve un mensaje con código `400 Bad Request`.
- `len(mascotas)`: cuenta cuántas mascotas hay actualmente.
- `+ 1`: genera el siguiente identificador según el tamaño de la lista.
- `mascotas.append(...)`: agrega el nuevo diccionario al final de la lista.
- `201 Created`: indica que la mascota fue creada correctamente.

#### Endpoint para eliminar

```python
@app.route("/mascotas/<int:id>", methods=["DELETE"])
def eliminar_mascota(id):
  for mascota in mascotas:
    if mascota["id"] == id:
      mascotas.remove(mascota)
      return jsonify({"mensaje":"Mascota eliminado "})
  return jsonify({"mensaje":"Mascota no encotrado"})
```

- Usa un identificador en la URL porque hay que indicar qué mascota eliminar.
- `DELETE` representa la eliminación de un recurso.
- El `for` busca la mascota cuyo `id` coincide.
- `mascotas.remove(mascota)`: elimina ese elemento de la lista.
- Después de eliminarla, devuelve un mensaje y termina la función.
- Si no encuentra coincidencia, devuelve el mensaje final.
- En el código actual, ese caso no tiene explícitamente el código `404`; Flask devuelve `200` por defecto. Es una mejora pendiente.

#### Endpoint para actualizar

```python
@app.route("/mascotas/<int:id>", methods=["PUT"])
def actualizar_mascota(id):
  nuevos_datos = request.get_json()
  for mascota in mascotas:
    if mascota["id"] == id:
      mascota["nombre"] = nuevos_datos.get("nombre", mascota["nombre"])
      mascota["especie"] = nuevos_datos.get("especie", mascota["especie"])
      return jsonify(mascota) 
  return jsonify({"mensaje":"N se pudo actualizar"})
```

- `PUT` representa la actualización de un recurso.
- `nuevos_datos` guarda el JSON recibido.
- Se recorre la lista hasta encontrar el `id` indicado.
- `.get("nombre", mascota["nombre"])` busca un nuevo nombre; si no llega, conserva el nombre anterior.
- Se aplica la misma lógica a `especie`.
- Se devuelve la mascota ya modificada.
- Si no se encuentra el `id`, se devuelve un mensaje. Igual que en `DELETE`, el código actual debería mejorarse para devolver `404`.

#### Arranque del programa

```python
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
```

- `if __name__ == "__main__"`: comprueba si el archivo se está ejecutando directamente.
- Si otro archivo importa `app.py`, el servidor no se inicia automáticamente.
- `app.run(...)`: inicia el servidor de desarrollo de Flask.
- `host="0.0.0.0"`: permite recibir conexiones desde cualquier interfaz de red; es útil en Docker.
- `port=5000`: hace que el servicio escuche en el puerto `5000`.
- `debug=True`: activa mensajes detallados de error y recarga automática. Es útil para estudiar, pero no debe dejarse activo en producción.

### Detalles importantes que podrían preguntarte

1. **¿Por qué se usa `return` dentro del `for`?** Porque cuando se encuentra la mascota ya se tiene la respuesta y no es necesario seguir recorriendo la lista.
2. **¿Qué ocurre si `request.get_json()` no recibe JSON?** En el estado actual puede producir un error al intentar comprobar las claves. Se debe validar que el cuerpo exista antes de usarlo.
3. **¿Por qué `len(mascotas) + 1` no es suficiente para una aplicación real?** Si se elimina una mascota, el tamaño de la lista puede coincidir con un identificador que ya existe. Una base de datos debe generar identificadores de forma segura.
4. **¿Qué diferencia hay entre la URL y el método HTTP?** La URL indica el recurso, por ejemplo `/mascotas`; el método indica la acción: consultar, crear, actualizar o eliminar.
5. **¿Qué parte conecta el cliente con Python?** El decorador `@app.route`, porque relaciona una solicitud HTTP con una función concreta.

## Tecnologías

- Python 3.12
- Flask
- Docker
- JSON para las solicitudes y respuestas

## Estructura del proyecto

```text
petshop_taller/
├── app.py            # Aplicación Flask y endpoints de la API
├── requirements.txt  # Dependencias de Python
├── Dockerfile        # Imagen para ejecutar el servicio con Docker
├── .dockerignore     # Archivos excluidos de la imagen
└── README.md         # Documentación del proyecto
```

## Cómo funciona internamente

La aplicación se crea en `app.py` mediante Flask. La variable `mascotas` funciona actualmente como almacenamiento temporal en memoria.

Cada ruta recibe una solicitud HTTP, ejecuta una operación sobre esa lista y devuelve una respuesta JSON. Por eso:

- los datos iniciales están definidos en el código;
- los cambios solo viven mientras el proceso está ejecutándose;
- al reiniciar la aplicación, se pierden las mascotas creadas, editadas o eliminadas;
- no existe todavía una base de datos ni autenticación.

Esta implementación es adecuada para aprendizaje y pruebas locales, pero necesita persistencia, validaciones y controles de seguridad antes de producción.

## Endpoints

### Listar mascotas

```http
GET /mascotas
```

Respuesta actual:

```json
[
  {"id": 1, "nombre": "max", "especie": "perro"},
  {"id": 2, "nombre": "Roberto", "especie": "perro"}
]
```

### Buscar una mascota

```http
GET /mascotas/<id>
```

Ejemplo:

```text
GET /mascotas/1
```

Devuelve la mascota si existe. Si no existe, responde con `404` y un mensaje indicando que no fue encontrada.

### Registrar una mascota

```http
POST /mascotas
Content-Type: application/json
```

Cuerpo esperado:

```json
{
  "nombre": "Luna",
  "especie": "gato"
}
```

Cuando la solicitud es válida, el servicio asigna un identificador y responde con `201 Created`.

### Actualizar una mascota

```http
PUT /mascotas/<id>
Content-Type: application/json
```

Ejemplo:

```json
{
  "nombre": "Luna adulta"
}
```

La implementación actual actualiza `nombre` y `especie` solo cuando esos campos aparecen en la solicitud. Los campos que no se envían conservan su valor.

### Eliminar una mascota

```http
DELETE /mascotas/<id>
```

Si encuentra la mascota, la elimina de la lista en memoria. En el estado actual, algunas respuestas de error todavía necesitan normalizarse para usar códigos HTTP consistentes.

## Instalación local

Requiere Python 3.12 o una versión compatible.

En PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

El servicio queda disponible en:

```text
http://localhost:5000
```

La aplicación se inicia escuchando en `0.0.0.0`, por lo que también puede recibir conexiones desde un contenedor.

## Ejemplos de uso

Listar mascotas:

```powershell
curl http://localhost:5000/mascotas
```

Crear una mascota:

```powershell
curl -Method Post http://localhost:5000/mascotas `
  -ContentType "application/json" `
  -Body '{"nombre":"Luna","especie":"gato"}'
```

Actualizar una mascota:

```powershell
curl -Method Put http://localhost:5000/mascotas/1 `
  -ContentType "application/json" `
  -Body '{"nombre":"Max actualizado"}'
```

Eliminar una mascota:

```powershell
curl -Method Delete http://localhost:5000/mascotas/1
```

## Ejecución con Docker

Construir la imagen:

```powershell
docker build -t petshop-api .
```

Ejecutar el contenedor:

```powershell
docker run --rm -p 5000:5000 petshop-api
```

Después, consultar la API en `http://localhost:5000/mascotas`.

## Decisiones actuales y limitaciones

Estas decisiones son intencionales para mantener el proyecto pequeño y didáctico, pero deben quedar visibles para cualquier persona que lo use:

- **Almacenamiento en memoria:** simplifica el aprendizaje, pero no conserva información.
- **Sin autenticación:** cualquier cliente que alcance el servicio puede usar las rutas.
- **Validación mínima:** actualmente se validan principalmente la presencia de `nombre` y `especie` al crear una mascota.
- **Identificadores simples:** el identificador se calcula con base en el tamaño de la lista y no es seguro para un sistema persistente.
- **Modo debug:** el archivo inicia Flask con `debug=True`; debe desactivarse antes de desplegar el servicio públicamente.
- **Sin pruebas automatizadas:** todavía no hay una suite que proteja el comportamiento de los endpoints.

## Próximos pasos recomendados

Orden sugerido para continuar el proyecto:

1. Corregir y normalizar los mensajes y códigos `404` de actualización y eliminación.
2. Validar JSON ausente, tipos incorrectos, nombres vacíos y especies vacías.
3. Crear pruebas automatizadas para cada endpoint y sus casos de error.
4. Separar rutas, lógica de negocio y configuración en módulos pequeños.
5. Añadir una base de datos, por ejemplo SQLite para desarrollo y PostgreSQL para despliegues más serios.
6. Usar variables de entorno para la configuración.
7. Desactivar `debug=True` y ejecutar con un servidor WSGI en producción.
8. Añadir autenticación, manejo de errores y registro de eventos si el servicio será usado por terceros.
9. Incorporar integración continua para ejecutar pruebas antes de aceptar cambios.
10. Publicar versiones o etiquetas cuando cada etapa esté estable.

## Cómo presentar el repositorio en GitHub

Una descripción honesta puede ser:

> API REST educativa para gestionar mascotas con Flask. Incluye operaciones CRUD y ejecución local o mediante Docker. Actualmente usa almacenamiento en memoria y se encuentra en desarrollo.

Es una buena práctica publicar proyectos en proceso si cada repositorio tiene un objetivo claro, instrucciones para ejecutarlo y una sección de estado conocida. No hace falta esperar a que sea perfecto: lo importante es que quien lo visite pueda entender qué funciona, qué falta y cómo aportar.

Antes de subirlo, verifica que el repositorio no incluya:

- la carpeta `venv/`;
- contraseñas, tokens o claves privadas;
- archivos temporales;
- datos personales;
- configuraciones locales que no deban compartirse.

## Licencia

Antes de publicar el repositorio, elige una licencia en GitHub. Para un proyecto educativo que quieres reutilizar y permitir que otras personas modifiquen, una licencia permisiva como MIT suele ser una opción sencilla. La elección final depende de las condiciones con las que quieras compartir el código.
