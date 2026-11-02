import logging
from dataclasses import dataclass
from typing import Literal

import httpx
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from music_store.settings import Settings

logger = logging.getLogger(__name__)

Provider = Literal["ollama", "openai"]

OLLAMA_EMBEDDING_MODEL = "bge-m3"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
AVAILABILITY_TIMEOUT_SECONDS = 1.0

OLLAMA_NUM_CTX = 16384
OLLAMA_TEMPERATURE = 0.6
OLLAMA_TOP_P = 0.95
OLLAMA_TOP_K = 20


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: Provider
    label: str


# The allowlist: only these ids can be requested through `x-model`.
MODEL_SPECS: tuple[ModelSpec, ...] = (
    ModelSpec("qwen3:4b", "ollama", "Qwen3 4B (local)"),
    ModelSpec("qwen3:8b", "ollama", "Qwen3 8B (local)"),
    ModelSpec("gpt-6-luna", "openai", "GPT-6 Luna (API)"),
)


class ProviderRegistry:
    """Maps allowlisted model ids to chat models, provider embeddings and availability.

    This is the single seam tests override with fakes.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.specs = MODEL_SPECS
        if settings.default_model not in {s.id for s in self.specs}:
            raise ValueError(f"default_model {settings.default_model!r} is not in the allowlist")

    @property
    def default_id(self) -> str:
        return self.settings.default_model

    def get_spec(self, model_id: str) -> ModelSpec | None:
        return next((s for s in self.specs if s.id == model_id), None)

    def is_available(self, spec: ModelSpec) -> bool:
        if spec.provider == "openai":
            key = self.settings.openai_api_key
            return key is not None and bool(key.get_secret_value().strip())
        try:
            r = httpx.get(
                f"{self.settings.ollama_base_url}/api/tags",
                timeout=AVAILABILITY_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError:
            return False
        return r.is_success

    def chat_model(self, model_id: str) -> BaseChatModel:
        spec = self._require(model_id)
        if spec.provider == "openai":
            return ChatOpenAI(
                model=spec.id,
                api_key=self.settings.openai_api_key,
                reasoning={"effort": "low", "summary": "concise"},
            )
        # Thinking stays on: with it off, Ollama's qwen3 template leaves the model inside an
        # unclosed <think> block and the reasoning leaks into the answer. With it on, Ollama
        # separates it into `reasoning_content`, which the stream adapter forwards as reasoning
        # parts.
        #
        # `num_ctx` is explicit because Ollama's small default silently truncates the start of
        # the request (the system prompt) once tool results are added. The sampling values are
        # Qwen's recommended thinking-mode settings; greedy decoding makes it loop in thought.
        return ChatOllama(
            model=spec.id,
            base_url=self.settings.ollama_base_url,
            reasoning=True,
            num_ctx=OLLAMA_NUM_CTX,
            temperature=OLLAMA_TEMPERATURE,
            top_p=OLLAMA_TOP_P,
            top_k=OLLAMA_TOP_K,
        )

    def embeddings(self, model_id: str) -> Embeddings:
        spec = self._require(model_id)
        if spec.provider == "openai":
            return OpenAIEmbeddings(
                model=OPENAI_EMBEDDING_MODEL, api_key=self.settings.openai_api_key
            )
        return OllamaEmbeddings(
            model=OLLAMA_EMBEDDING_MODEL, base_url=self.settings.ollama_base_url
        )

    def warn_unavailable(self) -> None:
        for spec in self.specs:
            if not self.is_available(spec):
                logger.warning("Model %s (%s) is unavailable", spec.id, spec.provider)

    def _require(self, model_id: str) -> ModelSpec:
        spec = self.get_spec(model_id)
        if spec is None:
            raise KeyError(model_id)
        return spec
