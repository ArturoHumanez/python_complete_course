import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from intermediate.lab_8.models import Base
from intermediate.lab_9.database import get_db
from intermediate.lab_9.main import app

# === Base de datos en memoria para tests ===

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

@pytest.fixture(autouse=True)
def setup_db():
    """Crea las tablas antes de cada test y las destruye después."""
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db():
    """Sesión de base de datos para tests."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    """Cliente HTTP que usa la DB de prueba."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# === Helper para autenticación ===

@pytest.fixture
def auth_headers(client):
    """Registra un usuario y devuelve headers con token."""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "test1234",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# === Tests del CRUD ===

@pytest.fixture
def sample_order():
    return {
        "customer": "Juan",
        "items": [
            {"product": "Laptop", "price": 25000, "quantity": 1},
            {"product": "Mouse", "price": 350, "quantity": 2},
        ],
    }


class TestCreateOrder:
    def test_create_order_success(self, client, auth_headers, sample_order):
        response = client.post("/orders/", json=sample_order, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["customer"] == "Juan"
        assert data["status"] == "pending"
        assert data["total"] == 25700.0
        assert len(data["items"]) == 2

    def test_create_order_without_token(self, client, sample_order):
        response = client.post("/orders/", json=sample_order)

        assert response.status_code == 401

    def test_create_order_empty_items(self, client, auth_headers):
        response = client.post(
            "/orders/",
            json={"customer": "Juan", "items": []},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_create_order_negative_price(self, client, auth_headers):
        response = client.post(
            "/orders/",
            json={
                "customer": "Juan",
                "items": [{"product": "X", "price": -5, "quantity": 1}],
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetOrders:
    def test_list_orders_empty(self, client):
        response = client.get("/orders/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_orders_with_data(self, client, auth_headers, sample_order):
        client.post("/orders/", json=sample_order, headers=auth_headers)

        response = client.get("/orders/")

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_by_status(self, client, auth_headers, sample_order):
        client.post("/orders/", json=sample_order, headers=auth_headers)

        response = client.get("/orders/", params={"status": "completed"})

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_order_by_id(self, client, auth_headers, sample_order):
        create_resp = client.post("/orders/", json=sample_order, headers=auth_headers)
        order_id = create_resp.json()["id"]

        response = client.get(f"/orders/{order_id}")

        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_get_order_not_found(self, client):
        response = client.get("/orders/999")

        assert response.status_code == 404


class TestUpdateOrder:
    def test_update_status(self, client, auth_headers, sample_order):
        create_resp = client.post("/orders/", json=sample_order, headers=auth_headers)
        order_id = create_resp.json()["id"]

        response = client.patch(
            f"/orders/{order_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    @pytest.mark.parametrize("bad_status", ["refunded", "shipped", ""])
    def test_update_invalid_status(self, client, auth_headers, sample_order, bad_status):
        create_resp = client.post("/orders/", json=sample_order, headers=auth_headers)
        order_id = create_resp.json()["id"]

        response = client.patch(
            f"/orders/{order_id}",
            json={"status": bad_status},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestDeleteOrder:
    def test_delete_order(self, client, auth_headers, sample_order):
        create_resp = client.post("/orders/", json=sample_order, headers=auth_headers)
        order_id = create_resp.json()["id"]

        response = client.delete(f"/orders/{order_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verificar que ya no existe
        get_resp = client.get(f"/orders/{order_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client, auth_headers):
        response = client.delete("/orders/999", headers=auth_headers)

        assert response.status_code == 404