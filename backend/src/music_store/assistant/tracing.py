"""Optional LangSmith tracing, passed per request instead of through process environment."""

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tracers.langchain import LangChainTracer
from langsmith import Client

from music_store.settings import Settings


def build_tracing_callbacks(settings: Settings) -> list[BaseCallbackHandler]:
    """A LangSmith tracer when tracing is enabled and keyed, else no callbacks."""
    if not settings.langsmith_tracing or settings.langsmith_api_key is None:
        return []
    client = Client(api_key=settings.langsmith_api_key.get_secret_value())
    return [LangChainTracer(client=client, project_name=settings.langsmith_project)]
