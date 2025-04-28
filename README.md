# Conversations API 

**Conversations API** es un servicio RESTful diseñado para gestionar conversaciones, mensajes y usuarios de manera eficiente. Este backend puede ser utilizado para integrar funcionalidades de chat, sistemas de soporte, o motores de conversación en diversas plataformas.

## AUTOR: Isaac Reyes

### SoftConsulting S.A.

## Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Variables de Entorno](#variables-de-entorno)
- [Comandos útiles](#comandos-útiles)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Endpoints principales](#endpoints-principales)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

---

## Características

- Crear, actualizar y listar conversaciones.
- Enviar y recibir mensajes dentro de una conversación.
- Soporte para usuarios múltiples.
- Integración sencilla con servicios de frontend o chatbots.
- Arquitectura limpia y modular.

---

## Tecnologías

- **Python** `>=3.8`
- **FastAPI** para la construcción del API.
- **Uvicorn** como servidor ASGI.
- **SQLAlchemy / Tortoise ORM** (según configuración) para la gestión de base de datos.
- **Docker** (opcional) para despliegues locales y productivos.
- **Cloudant** o **SQLite** o **PostgreSQL** como bases de datos predeterminadas.

NOTA: por el momento estara tal cual, simple
---

## Instalación

```bash
# Clona el repositorio
git clone https://github.com/IGRASoft/conversations-api-cloudant.git
cd conversations-api/

# Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt

# Corre el servidor de desarrollo SOLO SI ES NECESARIO, USAREMOS CLOUD ENGINE
uvicorn app.main:app --reload
```

---

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
CLOUDANT_URL=
CLOUDANT_API_KEY=tu_clave_secreta
CLOUDANT_DB_NAME=
```

(O usa configuración para la base en producción).

---

## Comandos útiles

- Ejecutar servidor local:

  ```bash
  uvicorn app.main:app --reload
  ```

- Formatear el código:

  ```bash
  black .
  ```

- Verificar estilo de código:

  ```bash
  flake8 .
  ```

- Crear migraciones (si usas Alembic):

  ```bash
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```

---

## Estructura del proyecto

```bash
conversations-api/
├── app/
│   ├── main.py          # Punto de entrada de la aplicación FastAPI
│   
│   ├── cloudant_client.py        #IBM CLOUDANT - en vez de MONGODB
├── Dockerfile           # Imagen Docker para producción
├── requirements.txt     # Dependencias
├── README.md            # Este archivo
```

---

## Endpoints principales

Una vez levantado el servidor, puedes acceder a la documentación automática:

- **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Redoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

Ejemplos de endpoints (NO ESTARAN TODOS):

| Método  | Ruta                        | Descripción                    |
|---------|------------------------------|---------------------------------|
| GET     | `/api/conversations`         | Listar todas las conversaciones |
| POST    | `/api/conversations`         | Crear una nueva conversación    |
| GET     | `/api/conversations/{id}`    | Obtener detalles de conversación |
| POST    | `/api/conversations/{id}/messages` | Enviar un mensaje           |
| GET     | `/api/conversations/{id}/messages` | Listar mensajes             |

---

## Contribuciones
Consultar con el dueño del repo

## Licencia
Privado y a los que corresponde