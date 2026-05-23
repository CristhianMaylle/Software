from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# POST /api/v1/transactions
# ---------------------------------------------------------------------------


def test_create_ingreso_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/transactions",
        json={"amount": 1500.0, "type": "ingreso", "description": "Monthly salary"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 1500.0
    assert data["type"] == "ingreso"
    assert data["description"] == "Monthly salary"
    assert isinstance(data["id"], int)


def test_create_egreso_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/transactions",
        json={"amount": 350.0, "type": "egreso", "description": "Electricity bill"},
    )
    assert response.status_code == 201
    assert response.json()["type"] == "egreso"


def test_create_transaction_invalid_type_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/transactions",
        json={"amount": 100.0, "type": "invalid", "description": "Bad type"},
    )
    assert response.status_code == 422


def test_create_transaction_negative_amount_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/transactions",
        json={"amount": -50.0, "type": "ingreso", "description": "Negative"},
    )
    assert response.status_code == 422


def test_create_transaction_zero_amount_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/transactions",
        json={"amount": 0.0, "type": "egreso", "description": "Zero"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/transactions
# ---------------------------------------------------------------------------


def test_list_transactions_empty(client: TestClient) -> None:
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


def test_list_transactions_pagination(client: TestClient) -> None:
    for i in range(5):
        client.post(
            "/api/v1/transactions",
            json={
                "amount": float(100 * (i + 1)),
                "type": "ingreso",
                "description": f"tx-{i}",
            },
        )
    response = client.get("/api/v1/transactions?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 3
    assert data["skip"] == 0
    assert data["limit"] == 3


def test_list_transactions_limit_exceeds_max_returns_400(client: TestClient) -> None:
    response = client.get("/api/v1/transactions?limit=101")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/v1/balance
# ---------------------------------------------------------------------------


def test_balance_empty_database(client: TestClient) -> None:
    response = client.get("/api/v1/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["total_ingresos"] == 0.0
    assert data["total_egresos"] == 0.0
    assert data["balance"] == 0.0


def test_balance_correct_calculation(client: TestClient) -> None:
    client.post(
        "/api/v1/transactions",
        json={"amount": 2000.0, "type": "ingreso", "description": "Salary"},
    )
    client.post(
        "/api/v1/transactions",
        json={"amount": 500.0, "type": "egreso", "description": "Rent"},
    )
    client.post(
        "/api/v1/transactions",
        json={"amount": 150.0, "type": "egreso", "description": "Utilities"},
    )

    response = client.get("/api/v1/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["total_ingresos"] == 2000.0
    assert data["total_egresos"] == 650.0
    assert data["balance"] == 1350.0


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
