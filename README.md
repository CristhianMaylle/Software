# Finance Control API

API RESTful para gestionar transacciones financieras (ingresos y egresos).
Sin frontend — toda la interacción se hace desde **Swagger UI**.

---

## Levantar con Docker (recomendado)

Levanta la API + SQL Server con un solo comando:

```bash
docker compose up --build
```

Swagger UI disponible en: **http://localhost:8000/docs**

> SQL Server arranca en el puerto `1433` con usuario `sa` y contraseña `YourPassword!123`
> (configurables en el archivo `.env`).

Para bajar todo y borrar datos:
```bash
docker compose down -v
```

---

## Desarrollo local (sin Docker)

### Requisitos
- Python 3.12+
- SQL Server accesible (local o en Docker)
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Setup

```bash
pip install -r requirements.txt
```

Edita `.env` con tus credenciales reales (cambia `DB_SERVER=localhost` si SQL Server corre localmente):

```env
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=FinanceControl
DB_USER=sa
DB_PASSWORD=YourPassword!123
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
FinanceControl/
├── app/
│   ├── main.py            # Entrypoint FastAPI + lifespan (crea BD y tablas)
│   ├── database.py        # Engine SQLAlchemy, ensure_database(), get_db()
│   ├── models.py          # Modelo ORM Transaction
│   ├── schemas.py         # Schemas Pydantic
│   └── routers/
│       ├── transactions.py
│       └── balance.py
├── tests/
│   ├── conftest.py        # Fixture SQLite en memoria
│   └── test_api.py
├── docker-compose.yml     # API + SQL Server
├── Dockerfile
├── .env                   # Variables de conexión (no subir a git)
└── requirements.txt
```
