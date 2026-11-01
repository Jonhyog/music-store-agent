# 03: Model registry, `/models` and header middlewares

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A person sees which models they can chat with (local Ollama models and the API model), with unavailable ones disabled and the default preselected. The API resolves and validates the `x-customer-id` and `x-model` headers on every request, rejecting bad values with clear errors. Tests can substitute fake models and embeddings through one seam.

**Blocked by:** 01 (Backend skeleton), 02 (Frontend skeleton).

**Status:** ready-for-agent

- [ ] A provider registry maps each model id in the config allowlist (`qwen3:4b` default with thinking disabled, `qwen3:8b`, `gpt-5.6-luna`) to its chat model and its provider's embedding model (Ollama `bge-m3`, or an OpenAI embedding model), and reports availability: Ollama reachable, or OpenAI key present.
- [ ] `GET /models` returns `{ models: [{ id, provider, label, available, default }] }` with no pagination.
- [ ] The server starts even when Ollama is down or no OpenAI key is set, logging a warning only.
- [ ] A pure ASGI customer middleware loads the Customer from `x-customer-id` into request state, treats a missing header as Visitor, and returns its own JSON 400 for malformed or unknown ids. A typed dependency only reads the result.
- [ ] A pure ASGI model middleware resolves `x-model` against the allowlist (default when absent), returning 400 for unknown models and 503 for unavailable ones.
- [ ] Middleware order: CORS first, then customer, then model, so error responses still carry CORS headers.
- [ ] The test harness can override the registry with a scripted fake chat model (supports tool binding, emits predetermined tool calls and text, can raise mid-turn) and deterministic fake embeddings.
- [ ] Tests cover `/models` availability and default, customer 400s, Visitor when the header is absent, model 400 and 503, and CORS headers on a 400.
- [ ] The header gains a model Select showing each model's availability, with unavailable models disabled and the default preselected. The selection is held in app state for the chat to send as `x-model`.
- [ ] Bruno requests for `/models` and the header error cases.
