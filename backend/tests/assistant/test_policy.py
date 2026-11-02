from fakes import FakeEmbeddings, FakeRegistry
from music_store.assistant.policy import PolicyIndexes
from music_store.settings import REPO_ROOT

PDF = REPO_ROOT / "data" / "store-policies.pdf"


class CountingEmbeddings(FakeEmbeddings):
    def __init__(self, name: str, log: list[str]) -> None:
        self.name = name
        self.log = log

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.log.append(self.name)
        return super().embed_documents(texts)


class CountingRegistry(FakeRegistry):
    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.builds: list[str] = []

    def embeddings(self, model_id: str):
        return CountingEmbeddings(self.get_spec(model_id).provider, self.builds)


def test_search_returns_chunks_with_section_numbers(settings):
    indexes = PolicyIndexes(CountingRegistry(settings), PDF)
    results = indexes.search("qwen3:4b", "horário de funcionamento", k=3)
    assert len(results) == 3
    assert all(chunk.section and chunk.title for chunk in results)
    assert len({chunk.section for chunk in results}) == 3


def test_search_finds_the_exact_chunk_text(settings):
    indexes = PolicyIndexes(CountingRegistry(settings), PDF)
    target = indexes.search("qwen3:4b", "x", k=1)[0]
    # Fake embeddings are hash based, so querying a chunk's exact content ranks it first.
    assert indexes.search("qwen3:4b", target.content, k=1)[0].section == target.section


def test_index_is_built_once_per_provider(settings):
    registry = CountingRegistry(settings)
    indexes = PolicyIndexes(registry, PDF)
    indexes.search("qwen3:4b", "devolução")
    indexes.search("qwen3:8b", "parcelamento")
    assert registry.builds == ["ollama"]


def test_local_and_api_providers_have_separate_indexes(settings):
    registry = CountingRegistry(settings)
    indexes = PolicyIndexes(registry, PDF)
    indexes.search("qwen3:4b", "garantia")
    indexes.search("gpt-5.6-luna", "garantia")
    indexes.search("gpt-5.6-luna", "frete")
    assert registry.builds == ["ollama", "openai"]


def test_nothing_is_built_before_the_first_search(settings):
    registry = CountingRegistry(settings)
    PolicyIndexes(registry, PDF)
    assert registry.builds == []
