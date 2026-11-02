"""Policy Manual search: one in-memory vector index per provider, built lazily (ADR 0003)."""

from collections.abc import Callable
from pathlib import Path
from threading import Lock

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from music_store.assistant.policy_chunks import load_policy_chunks
from music_store.models.policy import PolicyChunkModel
from music_store.providers import Provider, ProviderRegistry

DEFAULT_TOP_K = 4

PolicySearch = Callable[[str], list[PolicyChunkModel]]


class PolicyIndexes:
    def __init__(self, registry: ProviderRegistry, pdf_path: Path) -> None:
        self._registry = registry
        self._pdf_path = pdf_path
        self._stores: dict[Provider, InMemoryVectorStore] = {}
        self._chunks: dict[str, PolicyChunkModel] | None = None
        self._lock = Lock()

    def search(self, model_id: str, query: str, k: int = DEFAULT_TOP_K) -> list[PolicyChunkModel]:
        """Top chunks for the query, using the index of the provider that serves `model_id`."""
        store = self._store_for(model_id)
        assert self._chunks is not None
        docs = store.similarity_search(query, k=k)
        return [self._chunks[doc.metadata["section"]] for doc in docs]

    def searcher(self, model_id: str) -> PolicySearch:
        return lambda query: self.search(model_id, query)

    def _store_for(self, model_id: str) -> InMemoryVectorStore:
        spec = self._registry.get_spec(model_id)
        if spec is None:
            raise KeyError(model_id)
        provider = spec.provider
        with self._lock:
            if provider not in self._stores:
                self._stores[provider] = self._build(model_id)
            return self._stores[provider]

    def _build(self, model_id: str) -> InMemoryVectorStore:
        if self._chunks is None:
            chunks = load_policy_chunks(self._pdf_path)
            self._chunks = {chunk.section: chunk for chunk in chunks}
        documents = [
            Document(page_content=chunk.content, metadata={"section": chunk.section})
            for chunk in self._chunks.values()
        ]
        return InMemoryVectorStore.from_documents(documents, self._registry.embeddings(model_id))
