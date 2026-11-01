def test_lists_allowlisted_models_without_pagination(client):
    body = client.get("/models").json()
    assert set(body) == {"models"}
    assert [m["id"] for m in body["models"]] == ["qwen3:4b", "qwen3:8b", "gpt-5.6-luna"]
    assert set(body["models"][0]) == {"id", "provider", "label", "available", "default"}
    assert [m["provider"] for m in body["models"]] == ["ollama", "ollama", "openai"]


def test_exactly_one_default_and_it_is_the_configured_one(client):
    defaults = [m["id"] for m in client.get("/models").json()["models"] if m["default"]]
    assert defaults == ["qwen3:4b"]


def test_availability_reflects_the_registry(client, registry):
    registry.available.update({"qwen3:8b": False, "gpt-5.6-luna": False})
    available = {m["id"]: m["available"] for m in client.get("/models").json()["models"]}
    assert available == {"qwen3:4b": True, "qwen3:8b": False, "gpt-5.6-luna": False}


def test_models_are_listed_even_when_everything_is_unavailable(client, registry):
    registry.available.clear()
    body = client.get("/models").json()
    assert len(body["models"]) == 3
    assert not any(m["available"] for m in body["models"])
