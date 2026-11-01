# 08: Policy retrieval

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A person asks about store hours, address and contacts, payment and installment rules, exchanges and returns, shipping or warranty, and the Assistant answers from the Policy Manual, citing the section used. When the manual contradicts itself, the Assistant gives the more conservative answer and suggests confirming with the store. Local models retrieve fully offline, and the API model uses API embeddings (ADR 0003).

**Blocked by:** 04 (Chat API: streaming Assistant that answers catalog questions).

**Status:** ready-for-agent

- [ ] The Policy Manual PDF is chunked by section, one chunk per subsection, with the parent section title prepended and the section number kept as metadata.
- [ ] There is one in-memory vector index per provider, using that provider's embedding model from the registry, built lazily on its first search and reused afterwards.
- [ ] A policy search tool returns the top 3–4 chunks with their section numbers, using the index for the provider of the request's model.
- [ ] The prompt adds: policy questions go through the policy search tool, answers cite the section, the more conservative answer applies on contradictions with a suggestion to confirm with the store, and store hours and contact details are never answered from memory.
- [ ] Tests with fake embeddings cover chunks carrying section numbers and titles, search results including section numbers, the index being built once per provider (second search doesn't rebuild), and separate indexes for the local and API providers.
- [ ] A Bruno request for a policy question.
