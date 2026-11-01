# One embedding index per model provider

Policy Manual retrieval keeps a separate in-memory vector index per provider (Ollama `bge-m3` for local models, OpenAI embeddings for API models), and each chat request searches the index matching the provider of the model it selected. Vectors from different embedding models are not comparable, so a single shared index would force one provider's embeddings on every request: either API mode would still need a local Ollama, or "local" mode would need the internet and an API key. Each index is built lazily on its first search, so the server starts even if one provider is unreachable.

## Considered Options

- **Single index, provider set in config**: simplest, but breaks the "local mode is fully local" property in one direction or the other.
- **Keyword search (BM25), no embeddings**: no provider dependency, but misses Portuguese synonyms (e.g. "devolver" vs "arrependimento").
