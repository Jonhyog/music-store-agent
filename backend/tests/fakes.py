import hashlib
from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from music_store.providers import ModelSpec, ProviderRegistry


class FakeChatModel(BaseChatModel):
    """Scripted chat model. Each call plays the next step of `script`.

    A step is an `AIMessage` (text and/or `tool_calls`) or an `Exception` to raise.
    """

    script: list[Any]
    cursor: int = 0
    on_call: Callable[[list[BaseMessage]], None] | None = None  # sees what each call was sent

    @property
    def _llm_type(self) -> str:
        return "fake-scripted"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "FakeChatModel":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        if self.cursor >= len(self.script):
            raise AssertionError("FakeChatModel script exhausted")
        if self.on_call is not None:
            self.on_call(list(messages))
        step = self.script[self.cursor]
        self.cursor += 1
        if isinstance(step, Exception):
            raise step
        return ChatResult(generations=[ChatGeneration(message=step)])


class FakeEmbeddings(Embeddings):
    """Deterministic embeddings derived from a text hash."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [b / 255 for b in digest[:8]]


class FakeRegistry(ProviderRegistry):
    """Registry with controllable availability and a scripted chat model."""

    def __init__(self, settings, *, available: dict[str, bool] | None = None, script=None):
        super().__init__(settings)
        self.available = available if available is not None else {s.id: True for s in self.specs}
        self.script = script or [AIMessage(content="ok")]
        self.received: list[list[BaseMessage]] = []

    def is_available(self, spec: ModelSpec) -> bool:
        return self.available.get(spec.id, False)

    def chat_model(self, model_id: str) -> BaseChatModel:
        return FakeChatModel(script=list(self.script), on_call=self.received.append)

    def embeddings(self, model_id: str) -> Embeddings:
        return FakeEmbeddings()

    def warn_unavailable(self) -> None:
        pass
