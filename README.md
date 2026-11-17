# PetShop Taller – Guía de Aprendizaje

## 📖 Introducción
Este repositorio es un proyecto de ejemplo para gestionar una tienda de mascotas (PetShop). El objetivo de este **README** es servir como material de estudio: explicar los conceptos básicos del proyecto, describir cómo está estructurado y proporcionar ejemplos claros de cómo se definen y utilizan los diferentes componentes.

---

## 🛠️ Definiciones clave
| Término | Qué es | Ejemplo de uso |
|---------|--------|----------------|
| **Modelo** | Representa la entidad del dominio (por ejemplo, `Pet`, `Customer`). Se suele definir como una clase o una tabla en la base de datos. | ```python\nclass Pet(models.Model):\n    name = models.CharField(max_length=100)\n    age = models.IntegerField()\n``` |
| **Controlador / Route** | Punto de entrada HTTP que recibe la petición del cliente y delega la lógica al servicio o al modelo. | ```javascript\napp.get('/api/pets', petController.list)\n``` |
| **Servicio** | Contiene la lógica de negocio (validaciones, cálculos, etc.) y se mantiene separado de la capa de presentación. | ```go\nfunc (s *PetService) CreatePet(p Pet) error {\n    // validar datos\n    return s.repo.Save(p)\n}\n``` |
| **Repositorio** | Abstracción sobre la persistencia (base de datos, API externa). Permite cambiar la implementación sin tocar la lógica de negocio. | ```typescript\ninterface PetRepository {\n  findAll(): Promise<Pet[]>;\n}\n``` |
| **Migración** | Script que define cómo crear o modificar la estructura de la base de datos. | ```sql\nCREATE TABLE pets (\n  id SERIAL PRIMARY KEY,\n  name VARCHAR(100) NOT NULL,\n  age INTEGER NOT NULL\n);\n``` |
| **DTO (Data Transfer Object)** | Objeto que transporta datos entre capas, normalmente usado para validar la entrada del API. | ```java\npublic class PetDto {\n    @NotBlank private String name;\n    @Min(0) private int age;\n}\n``` |

---

## 🛡️ Circuit Breaker
El patrón **Circuit Breaker** protege a un servicio frente a fallos de otro servicio externo evitando que se acumulen solicitudes fallidas y permitiendo una recuperación automática.

### Definiciones
| Concepto | Qué es |
|----------|--------|
| **Closed** | El circuito está cerrado y todas las peticiones se envían al servicio destino. |
| **Open** | Después de superar el umbral de fallos, el circuito se abre y todas las peticiones son rechazadas inmediatamente. |
| **Half‑Open** | Estado intermedio donde se permite un número limitado de peticiones para probar si el servicio destino se recuperó. |
| **Timeout** | Tiempo máximo que una petición puede tardar antes de considerarse fallida. |
| **Umbral de fallos** | Número de fallos consecutivos que disparan la apertura del circuito (por ejemplo, 3). |

### Implementación típica (pseudocódigo)

```go
type CircuitBreaker struct {
    state          string        // "closed", "open", "half-open"
    failureCount   int
    failureThresh  int
    timeout        time.Duration
    lastFailure    time.Time
}

func (cb *CircuitBreaker) Call(req func() error) error {
    now := time.Now()
    // Si está abierto y el timeout no expiró, rechazar
    if cb.state == "open" && now.Sub(cb.lastFailure) < cb.timeout {
        return errors.New("circuit open")
    }
    // Si está abierto pero pasó el timeout, pasar a half‑open
    if cb.state == "open" && now.Sub(cb.lastFailure) >= cb.timeout {
        cb.state = "half-open"
    }

    err := req()
    if err != nil {
        cb.failureCount++
        if cb.failureCount >= cb.failureThresh {
            cb.state = "open"
            cb.lastFailure = now
        }
        return err
    }

    // petición exitosa, resetear contador y cerrar circuito
    cb.failureCount = 0
    cb.state = "closed"
    return nil
}
```

### Aplicación en el proyecto PetShop
Supongamos que el servicio **OrderService** llama al **InventoryService** para reservar un producto.

1. **Crear el breaker** en `src/services/order_service.py` (ejemplo en Python con `pybreaker`).

```python
import pybreaker
from inventory_client import InventoryClient

breaker = pybreaker.CircuitBreaker(
    fail_max=3,               # umbral de tres fallas
    reset_timeout=30,        # 30 segundos de timeout antes de intentar cerrar
)

class OrderService:
    def __init__(self):
        self.inventory = InventoryClient()

    @breaker
    def reserve_product(self, product_id, qty):
        return self.inventory.reserve(product_id, qty)
```

2. **Comportamiento esperado**
   - Las primeras tres peticiones fallidas (por ejemplo, Inventario no disponible) se contabilizan.
   - La cuarta petición se rechaza inmediatamente con `CircuitOpenError`.
   - Después de `reset_timeout` segundos, el breaker pasa a *half‑open* y permite una petición de prueba.
   - Si esa petición tiene éxito, el circuito vuelve a *closed*; si falla, vuelve a *open*.

### Explicación línea por línea

**Pseudocódigo Go**
- `type CircuitBreaker struct { ... }` – Define la estructura que mantiene el estado del breaker.
- `state string` – Indica el estado actual: *closed*, *open* o *half‑open*.
- `failureCount int` – Contador de fallos consecutivos.
- `failureThresh int` – Umbral que, al alcanzarse, abre el circuito.
- `timeout time.Duration` – Tiempo que debe esperar antes de pasar a *half‑open*.
- `lastFailure time.Time` – Marca de tiempo del último fallo registrado.
- `func (cb *CircuitBreaker) Call(req func() error) error { ... }` – Método que envuelve la llamada al servicio externo.
- `now := time.Now()` – Obtiene la hora actual para comparaciones.
- `if cb.state == "open" && now.Sub(cb.lastFailure) < cb.timeout { ... }` – Si el circuito está abierto y el timeout no expiró, rechaza la petición.
- `if cb.state == "open" && now.Sub(cb.lastFailure) >= cb.timeout { cb.state = "half-open" }` – Cuando el timeout expira, se pasa a *half‑open*.
- `err := req()` – Ejecuta la llamada real al servicio.
- `if err != nil { ... }` – Si hay error, incrementa `failureCount` y, si supera el umbral, abre el circuito.
- `cb.failureCount = 0; cb.state = "closed"` – En caso de éxito, reinicia contador y cierra el circuito.

**Código Python (pybreaker)**
- `breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)` – Configura el breaker con umbral de 3 fallas y timeout de 30 s.
- `@breaker` decorador en `reserve_product` – Aplica el patrón al método.
- Dentro de `reserve_product`, se delega a `InventoryClient.reserve`. Si este lanza excepción, el breaker registra el fallo.
- Tras 3 fallos consecutivos, `pybreaker` lanza `CircuitOpenError` y bloquea nuevas llamadas hasta que pasen 30 s.
- Cuando el timeout expira, se prueba una llamada; si funciona, el breaker vuelve a *closed*.

**Código Python Notificaciones**
- `email_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)` – Configura otro breaker para el envío de correos.
- `@email_breaker` en `send_email` protege la llamada HTTP.
- `timeout=5` en `requests.post` define el tiempo máximo de espera para la respuesta del proveedor.
- Si el proveedor falla tres veces, el breaker abre el circuito y evita más intentos hasta que transcurran 60 s.


### Otro ejemplo de servicio con Circuit Breaker
**Servicio de Notificaciones** que envía correos vía un proveedor externo.

```python
import pybreaker
import requests

email_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

class NotificationService:
    @email_breaker
    def send_email(self, to, subject, body):
        response = requests.post(
            "https://api.mailprovider.com/send",
            json={"to": to, "subject": subject, "body": body},
            timeout=5  # timeout de 5 segundos
        )
        response.raise_for_status()
        return response.json()
```

- Si el proveedor de correo responde con error o supera el timeout tres veces, el breaker abre el circuito y las siguientes peticiones son rechazadas rápidamente, evitando bloquear el hilo de la aplicación.

---

### Flujo de estado según la tarea

1. **Comunicación funcionando** – El circuito está en *Closed* y todas las peticiones llegan al servicio destino.
2. **Umbral de tres fallas** – Después de tres respuestas de error consecutivas, el breaker cambia a *Open*.
3. **Apertura del circuito** – Las siguientes peticiones son rechazadas rápidamente (error de circuito abierto).
4. **Recuperación del servicio destino** – Cuando el timeout configurado expira, el breaker pasa a *Half‑Open* y permite una petición de prueba.
5. **Éxito de la prueba** – Si la petición de prueba tiene éxito, el circuito vuelve a *Closed*.
6. **Configuración del timeout** – Tiempo que el breaker espera antes de intentar cerrar (ej. 30 s).
7. **Rechazo rápido de la cuarta solicitud** – La cuarta petición después del umbral es rechazada sin intentar el servicio.
8. **Retorno a CLOSED** – Tras una petición exitosa en *Half‑Open*, el estado vuelve a *Closed*.

---

## 📂 Estructura del proyecto
```
petshop_taller/          # Raíz del proyecto
├─ src/                 # Código fuente
│  ├─ models/           # Definición de modelos/entidades
│  ├─ controllers/      # Rutas y controladores HTTP
│  ├─ services/         # Lógica de negocio
│  ├─ repositories/     # Acceso a datos
│  └─ migrations/       # Scripts de base de datos
├─ tests/                # Tests unitarios e integrales
└─ README.md             # Este documento
```

---

## ✍️ Cómo definir un nuevo recurso (ejemplo: "Producto")
1. **Modelo** – `src/models/product.py`
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=0)
```
2. **Repositorio** – `src/repositories/product_repo.py`
```python
class ProductRepository:
    def get_all(self):
        return Product.objects.all()
    def create(self, data):
        return Product.objects.create(**data)
```
3. **Servicio** – `src/services/product_service.py`
```python
class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
    def add_product(self, dto):
        # Aquí podrías validar el precio, stock, etc.
        return self.repo.create(dto)
```
4. **Controlador / Ruta** – `src/controllers/product_controller.py`
```python
from fastapi import APIRouter, Body
router = APIRouter()
service = ProductService(ProductRepository())

@router.post('/products')
async def create_product(payload: dict = Body(...)):
    return service.add_product(payload)
```
5. **Migración** – `src/migrations/20231104_create_products.sql`
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(8,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);
```

---

## 🚀 Ejecutar el proyecto (paso a paso)
1. **Instalar dependencias** (asumiendo que usamos `npm` o `pip`).
   ```bash\n# Python\npython -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\n\n# Node.js\nnpm install\n```
2. **Aplicar migraciones**
   ```bash\n# ejemplo con Flask-Migrate\nflask db upgrade\n```
3. **Iniciar el servidor**
   ```bash\n# Python (FastAPI)\nuvicorn src.main:app --reload\n\n# Node (Express)\nnpm run dev\n```
4. **Probar la API** con `curl` o Postman:
   ```bash\ncurl -X POST http://localhost:8000/pets -H "Content-Type: application/json" -d '{"name":"Firulais","age":3}'\n```

---

## 🧪 Tests
Los tests están en la carpeta `tests/`. Ejecuta:
```bash\n# Python\npytest\n\n# Node\nnpm test\n```
Asegúrate de que todos pasen antes de subir cambios.

---

## 🤝 Contribuir
1. **Fork** el repositorio.
2. Crea una rama descriptiva: `git checkout -b feature/nueva-funcionalidad`.
3. Implementa los cambios siguiendo la arquitectura mostrada arriba.
4. Ejecuta los tests y asegura que el **README** quede actualizado.
5. Abre un **Pull Request** describiendo qué hiciste y por qué.

---

## 📚 Recursos de aprendizaje recomendados
- **FastAPI** – <https://fastapi.tiangolo.com/>
- **SQLAlchemy** – <https://www.sqlalchemy.org/>
- **Docker** – <https://docs.docker.com/get-started/>
- **Testing con PyTest** – <https://docs.pytest.org/en/latest/>

---

¡Listo! Con este documento puedes ir leyendo cada sección, copiar los ejemplos en tu editor y experimentar. Cada bloque de código está pensado para ser funcional dentro del proyecto, de modo que al probarlo aprenderás tanto la teoría como la práctica.
