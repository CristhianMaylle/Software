# Finance Control API

API RESTful para gestionar transacciones financieras (ingresos y egresos).
Sin frontend — toda la interacción se hace desde **Swagger UI**.

---

## Levantar con Docker (recomendado)

Copia `.env.example` a `.env` y luego levanta la API + PostgreSQL con un solo comando:

```bash
cp .env.example .env   # ajusta DB_PASSWORD
docker compose up --build
```

Swagger UI disponible en: **http://localhost:8000/docs**

> PostgreSQL 18 corre como servicio interno `db` (puerto `5432`, sin exponer al host).
> Usuario, contraseña y nombre de base se configuran en el archivo `.env`.

Para bajar todo y borrar datos:
```bash
docker compose down -v
```

---

## Desarrollo local (sin Docker)

### Requisitos
- Python 3.12+
- PostgreSQL accesible (local o en Docker). El driver `psycopg` se instala con pip;
  no necesitas paquetes del sistema.

### Setup

```bash
pip install -r requirements.txt
```

Edita `.env` con tus credenciales reales (usa `DB_SERVER=localhost` si Postgres corre localmente):

```env
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=finance_control
DB_USER=finance
DB_PASSWORD=tu_password_seguro
```

Inicia la API (la base de datos y las tablas se crean automáticamente al arrancar):

```bash
uvicorn app.main:app --reload
```

---

## Correr los tests

Los tests usan **SQLite en memoria** — no necesitas SQL Server:

```bash
pytest tests/ -v
```

---

## Endpoints

| Método | Ruta                    | Descripción                              |
|--------|-------------------------|------------------------------------------|
| POST   | `/api/v1/transactions`  | Registrar una transacción                |
| GET    | `/api/v1/transactions`  | Listar transacciones (`skip`, `limit`)   |
| GET    | `/api/v1/balance`       | Resumen financiero (ingresos/egresos)    |
| GET    | `/health`               | Health check                             |

> Los endpoints `/api/v1/*` requieren el header **`X-API-Key`** (ver Autenticación).
> `/health` y `/docs` quedan abiertos.

## Autenticación

Los endpoints de datos (`/api/v1/*`) están protegidos con una **API key**. Manda la
clave en el header `X-API-Key`:

```bash
curl -H "X-API-Key: TU_CLAVE" https://oswalbot.itelcore.org/api/v1/balance
```

En **Swagger UI** (`/docs`): clic en **Authorize** (arriba a la derecha), pega la clave
y ya puedes probar los endpoints. `/health` y `/docs` no requieren clave.

La clave se configura en el `.env` del servidor (`API_KEY=...`, ver `.env.example`).

### Ejemplo — Crear transacción

```json
POST /api/v1/transactions
{
  "amount": 1500.0,
  "type": "ingreso",
  "description": "Salario mensual"
}
```

`type` acepta `"ingreso"` o `"egreso"`. `date` es opcional.

### Ejemplo — Balance

```json
GET /api/v1/balance
{
  "total_ingresos": 3000.0,
  "total_egresos": 850.0,
  "balance": 2150.0
}
```

---

## Estructura del proyecto

```
finance-control-api/
├── app/
│   ├── main.py            # Entrypoint FastAPI + lifespan (crea tablas)
│   ├── database.py        # Engine SQLAlchemy (PostgreSQL/psycopg), get_db()
│   ├── models.py          # Modelo ORM Transaction
│   ├── schemas.py         # Schemas Pydantic
│   └── routers/
│       ├── transactions.py
│       └── balance.py
├── tests/
│   ├── conftest.py        # Fixture SQLite en memoria (tests unitarios)
│   ├── test_api.py
│   └── integration_pg.py  # Contract test contra la API live (PostgreSQL real)
├── docker-compose.yml     # API + PostgreSQL 18 + labels Traefik
├── Dockerfile
├── .env.example           # Plantilla de variables (copiar a .env, no versionado)
└── requirements.txt
```

---

## Despliegue en producción

Desplegado tras Traefik v3 + Cloudflare en **https://oswalbot.itelcore.org**
(Swagger UI en `https://oswalbot.itelcore.org/docs`). La base PostgreSQL corre
como contenedor interno sin puertos expuestos; solo Traefik alcanza la API por la
red `web`.
