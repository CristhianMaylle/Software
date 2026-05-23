"""Contract / integration test contra la API *real* respaldada por PostgreSQL.

A diferencia de tests/test_api.py (que corre sobre SQLite en memoria), este test
golpea una instancia desplegada por HTTP y verifica el contrato literal de las
respuestas (nombres de keys + tipos) contra Postgres real. Es la defensa contra
drift del boundary HTTP <-> PostgreSQL (doctrina de integración del equipo).

Uso:
    FINANCE_BASE_URL=https://oswalbot.itelcore.org pytest tests/integration_pg.py -v

Se *salta* automáticamente si FINANCE_BASE_URL no está seteada, para no romper el
CI unitario sobre SQLite.

Teardown: borra las filas de prueba (namespace TEST_QA_pg_) vía SQL directo. Toma
el DSN de FINANCE_DB_DSN o lo arma desde las vars DB_* (las mismas que usa la app),
de modo que corra dentro del contenedor api. Si no hay acceso a la BD, avisa.
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

BASE_URL = os.getenv("FINANCE_BASE_URL", "").rstrip("/")

pytestmark = pytest.mark.skipif(
    not BASE_URL,
    reason="set FINANCE_BASE_URL to run the live PostgreSQL contract test",
)

# Namespace único por corrida -> cleanup seguro por LIKE, sin tocar datos reales.
NS = f"TEST_QA_pg_{uuid.uuid4().hex[:8]}"

TX_KEYS = {"id", "amount", "type", "description", "date"}
BALANCE_KEYS = {"total_ingresos", "total_egresos", "balance"}
PAGE_KEYS = {"total", "skip", "limit", "data"}


def _dsn() -> str | None:
    dsn = os.getenv("FINANCE_DB_DSN")
    if dsn:
        return dsn
    host = os.getenv("DB_SERVER")
    if not host:
        return None
    return (
        f"host={host} port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'finance_control')} "
        f"user={os.getenv('DB_USER', 'finance')} "
        f"password={os.getenv('DB_PASSWORD', '')}"
    )


API_KEY = os.getenv("FINANCE_API_KEY", "")


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    with httpx.Client(base_url=BASE_URL, timeout=15.0, headers=headers) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def _teardown():
    yield
    dsn = _dsn()
    if not dsn:
        print(f"\n[integration_pg] sin acceso a BD; borra filas {NS}% a mano")
        return
    try:
        import psycopg

        with psycopg.connect(dsn, autocommit=True) as conn:
            conn.execute(
                "DELETE FROM transactions WHERE description LIKE %s",
                (f"{NS}%",),
            )
    except Exception as exc:  # noqa: BLE001
        print(f"\n[integration_pg] teardown falló ({exc}); borra {NS}% a mano")


def test_health(client: httpx.Client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_transaction_contract(client: httpx.Client) -> None:
    r = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1234.56,
            "type": "ingreso",
            "description": f"{NS} salario",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert set(body.keys()) == TX_KEYS  # contrato literal de keys
    assert isinstance(body["id"], int)
    assert isinstance(body["amount"], int | float)
    assert body["type"] == "ingreso"
    assert body["description"] == f"{NS} salario"
    assert isinstance(body["date"], str)  # datetime serializado ISO-8601


def test_list_pagination_contract(client: httpx.Client) -> None:
    for i in range(3):
        client.post(
            "/api/v1/transactions",
            json={
                "amount": float(10 * (i + 1)),
                "type": "egreso",
                "description": f"{NS} gasto {i}",
            },
        )
    r = client.get("/api/v1/transactions", params={"skip": 0, "limit": 2})
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == PAGE_KEYS
    assert isinstance(body["total"], int) and body["total"] >= 4
    assert body["skip"] == 0
    assert body["limit"] == 2
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 2
    assert set(body["data"][0].keys()) == TX_KEYS


def test_list_limit_over_max_returns_400(client: httpx.Client) -> None:
    r = client.get("/api/v1/transactions", params={"limit": 101})
    assert r.status_code == 400


def test_balance_contract(client: httpx.Client) -> None:
    r = client.get("/api/v1/balance")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == BALANCE_KEYS
    assert isinstance(body["total_ingresos"], int | float)
    assert isinstance(body["total_egresos"], int | float)
    diff = body["total_ingresos"] - body["total_egresos"]
    assert abs(body["balance"] - diff) < 1e-6  # invariante de negocio


def test_create_invalid_type_returns_422(client: httpx.Client) -> None:
    r = client.post(
        "/api/v1/transactions",
        json={"amount": 1.0, "type": "invalid", "description": f"{NS} bad"},
    )
    assert r.status_code == 422


def test_missing_api_key_returns_401(client: httpx.Client) -> None:
    r = client.get("/api/v1/balance", headers={"X-API-Key": ""})
    assert r.status_code == 401
