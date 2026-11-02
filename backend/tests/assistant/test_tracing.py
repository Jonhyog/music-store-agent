from langchain_core.tracers.langchain import LangChainTracer
from langsmith import Client

from music_store.assistant.tracing import build_tracing_callbacks
from music_store.settings import Settings


def test_tracing_is_off_by_default():
    assert build_tracing_callbacks(Settings(_env_file=None)) == []


def test_tracing_needs_both_the_flag_and_a_key():
    assert build_tracing_callbacks(Settings(_env_file=None, langsmith_tracing=True)) == []
    assert build_tracing_callbacks(Settings(_env_file=None, langsmith_api_key="k")) == []


def test_tracing_enabled_returns_a_langsmith_tracer_for_the_project(monkeypatch):
    offline = lambda **kwargs: Client(api_key="k", auto_batch_tracing=False)  # noqa: E731
    monkeypatch.setattr("music_store.assistant.tracing.Client", offline)
    settings = Settings(_env_file=None, langsmith_tracing=True, langsmith_api_key="k")
    [tracer] = build_tracing_callbacks(settings)
    assert isinstance(tracer, LangChainTracer)
    assert tracer.project_name == "music-store-assistant"
