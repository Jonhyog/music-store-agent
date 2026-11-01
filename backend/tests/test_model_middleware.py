import pytest
from fastapi.testclient import TestClient

from music_store.app import create_app
from music_store.middleware.model import CurrentModel


@pytest.fixture
def probe(settings, registry):
    app = create_app(settings, registry=registry)

    @app.get("/chat")
    def chat(model: CurrentModel):
        return {"model": model.id}

    with TestClient(app) as c:
        yield c


def test_absent_header_uses_default(probe):
    assert probe.get("/chat").json() == {"model": "qwen3:4b"}


def test_known_model_is_resolved(probe):
    assert probe.get("/chat", headers={"x-model": "qwen3:8b"}).json() == {"model": "qwen3:8b"}


def test_unknown_model_is_400(probe):
    r = probe.get("/chat", headers={"x-model": "gpt-2"})
    assert r.status_code == 400


def test_unavailable_model_is_503(probe, registry):
    registry.available["gpt-5.6-luna"] = False
    r = probe.get("/chat", headers={"x-model": "gpt-5.6-luna"})
    assert r.status_code == 503


def test_unavailable_default_is_503(probe, registry):
    registry.available["qwen3:4b"] = False
    assert probe.get("/chat").status_code == 503


def test_unavailable_model_does_not_block_other_routes(client, registry):
    registry.available["qwen3:4b"] = False
    assert client.get("/customers").status_code == 200


def test_unknown_model_error_carries_cors_headers(client):
    r = client.get("/customers", headers={"x-model": "nope", "Origin": "http://localhost:5173"})
    assert r.status_code == 400
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
