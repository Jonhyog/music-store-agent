import pytest
from fastapi.testclient import TestClient

from music_store.app import create_app
from music_store.middleware.customer import CurrentCustomer


@pytest.fixture
def whoami(settings, registry):
    app = create_app(settings, registry=registry)

    @app.get("/whoami")
    def whoami(customer: CurrentCustomer):
        return {"customer_id": customer.customer_id if customer else None}

    with TestClient(app) as c:
        yield c


def test_missing_header_is_visitor(whoami):
    assert whoami.get("/whoami").json() == {"customer_id": None}


def test_valid_header_loads_customer(whoami):
    r = whoami.get("/whoami", headers={"x-customer-id": "1"})
    assert r.json() == {"customer_id": 1}


@pytest.mark.parametrize("value", ["abc", "1.5", "-1", "1 2", ""])
def test_malformed_id_is_400(whoami, value):
    r = whoami.get("/whoami", headers={"x-customer-id": value})
    assert r.status_code == 400


def test_unknown_id_is_400(whoami):
    r = whoami.get("/whoami", headers={"x-customer-id": "999999"})
    assert r.status_code == 400
    assert "detail" in r.json()


def test_400_carries_cors_headers(client):
    r = client.get(
        "/customers",
        headers={"x-customer-id": "abc", "Origin": "http://localhost:5173"},
    )
    assert r.status_code == 400
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_unexpected_failure_is_a_generic_500(whoami, settings, monkeypatch):
    def boom(*args):
        raise RuntimeError("secret internals")

    monkeypatch.setattr("music_store.middleware.customer._load_customer", boom)
    r = whoami.get("/whoami", headers={"x-customer-id": "1"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Unexpected error."}
