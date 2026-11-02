import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from fakes import FakeChatModel, FakeEmbeddings
from music_store.app import create_app
from music_store.providers import ProviderRegistry
from music_store.settings import Settings


def test_server_starts_without_ollama_or_openai_key(settings):
    unreachable = Settings(
        _env_file=None,
        database_path=settings.database_path,
        ollama_base_url="http://127.0.0.1:1",
        openai_api_key=None,
    )
    with TestClient(create_app(unreachable)) as c:
        assert c.get("/customers").status_code == 200


def test_unknown_default_model_is_rejected(settings):
    bad = Settings(_env_file=None, database_path=settings.database_path, default_model="nope")
    with pytest.raises(ValueError):
        create_app(bad)


def test_fake_chat_model_emits_scripted_tool_calls_and_text():
    call = {"name": "ping", "args": {}, "id": "1"}
    model = FakeChatModel(
        script=[AIMessage(content="", tool_calls=[call]), AIMessage(content="hi")]
    )

    @tool
    def ping() -> str:
        """Ping."""
        return "pong"

    bound = model.bind_tools([ping])
    assert bound.invoke([HumanMessage("x")]).tool_calls[0]["name"] == "ping"
    assert bound.invoke([HumanMessage("x")]).content == "hi"


def test_fake_chat_model_can_raise_mid_turn():
    model = FakeChatModel(script=[AIMessage(content="a"), RuntimeError("boom")])
    model.invoke([HumanMessage("x")])
    with pytest.raises(RuntimeError, match="boom"):
        model.invoke([HumanMessage("x")])


def test_fake_embeddings_are_deterministic():
    e = FakeEmbeddings()
    assert e.embed_query("a") == e.embed_query("a")
    assert e.embed_query("a") != e.embed_query("b")


def test_blank_openai_key_marks_api_model_unavailable(settings):
    blank = Settings(
        _env_file=None,
        database_path=settings.database_path,
        ollama_base_url="http://127.0.0.1:1",
        openai_api_key="",
    )
    with TestClient(create_app(blank)) as c:
        models = {m["id"]: m for m in c.get("/models").json()["models"]}
    assert models["gpt-5.6-luna"]["available"] is False
    assert models["qwen3:4b"]["available"] is False


def test_ollama_models_keep_thinking_on_so_reasoning_stays_out_of_the_answer(settings):
    model = ProviderRegistry(settings).chat_model("qwen3:4b")
    assert model.reasoning is True
