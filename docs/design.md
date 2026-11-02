# Design — Empório da Música Assistant (MVP)

Agreed design for the customer-service Assistant prototype described in `desafio_tecnico_ai_eng_artefact.pdf`. Domain vocabulary lives in [`GLOSSARY.md`](../GLOSSARY.md); hard-to-reverse decisions live in [`docs/adr/`](./adr/).

## Agent approach

- Hybrid agent on LangChain v1 `create_agent` (LangGraph-based) with tool calling. No text-to-SQL ([ADR 0001](./adr/0001-fixed-scoped-tools-over-text-to-sql.md)).
- Tools:
  - Catalog and pricing: `search_products(query, category, max_price, in_stock)`, `get_product(name_or_id)`, `list_categories()`, `list_active_promotions(category?)`.
  - Orders, scoped to the Customer: `list_my_orders(status?)`, `get_my_order(order_id)`.
  - Complaints: `register_complaint(category, description, order_id?)`.
  - Policies: `search_policies(query)`. Retrieval is a tool the agent chooses to call, not context injected on every turn.
- Tools compute money values: List Price, Promotional Price, discount %, and PIX price. The PIX Discount never stacks on a Promotional Price.

## Scoping and identity

- There is no authentication. A pure ASGI middleware reads `x-customer-id`, loads the Customer from SQLite into `request.state.customer`, and returns its own JSON 400 if the id is malformed or unknown. If the header is missing, the caller is a Visitor.
- A typed dependency `current_customer() -> Customer | None` only reads that state.
- A second middleware resolves `x-model` against the config allowlist: an unknown model returns 400 and an unavailable provider returns 503. This is the extension point for per-Customer model entitlements.
- Middleware order: CORS → customer → model.
- The Customer reaches the tools through LangChain runtime `context` / `ToolRuntime`. The model never sees or chooses a customer id. Another Customer's Order returns "not found".

## Models

- The allowlist is defined in config: `qwen3:4b` (default), `qwen3:8b` (Ollama), and `gpt-5.6-luna` (OpenAI).
- `GET /models` returns `{ models: [{id, provider, label, available, default}] }` with no pagination. `available` reflects whether the provider can be reached or has an API key.
- A missing `x-model` falls back to the default from config.

## Retrieval (Policy Manual)

- `data/store-policies.pdf` is split by section, one chunk per subsection, with the parent section title prepended.
- There is one `InMemoryVectorStore` per provider: Ollama `bge-m3` for local models and OpenAI embeddings for API models. Each request searches the index matching its model's provider. Each index is built lazily on first search and kept in memory ([ADR 0003](./adr/0003-one-embedding-index-per-provider.md)).
- `search_policies` returns the top 3–4 chunks with their section numbers, for citation.
- Store hours and contact details come only from retrieval, so the manual stays the single source.

## Conversations

- History is held on the server in LangGraph `InMemorySaver`, keyed by a client-generated UUID `conversation_id` ([ADR 0002](./adr/0002-server-held-conversations.md)).
- Each Conversation is bound to the Customer or Visitor of its first message. A mismatch returns 409.
- Only the last ~20 messages go to the model. Conversations idle for more than 1 hour are evicted.
- Each Conversation has an `asyncio.Lock`. A concurrent message gets a 409 `conversation busy`.
- A failed or stopped turn is rolled back automatically: messages added since the turn started are removed. "Try again" just resends the message.
- Switching models keeps the history. A page reload starts a new Conversation, and there is no history-fetch endpoint.

## API (FastAPI)

| Method | Path | Notes |
|---|---|---|
| GET | `/customers?page&pageSize` | `{ customers: [...with order_count], page, total }` |
| GET | `/models` | see Models |
| POST | `/chat` | body `{ conversation_id, message (≤2000 chars) }`; headers `x-customer-id`, `x-model`; SSE stream |
| DELETE | `/chat/{conversation_id}` | 204, idempotent |
| GET | `/complaints?page&pageSize&customerId` | `{ complaints: [...with customer name], page, total }`, newest first; staff view, ignores `x-customer-id`; unknown id → empty list |

- Errors that happen before streaming starts are regular HTTP errors (400, 409, 422, 503).
- The stream uses the Vercel AI SDK UI message stream protocol (header `x-vercel-ai-ui-message-stream: v1`). Event types: `start`, `text-start`, `text-delta`, `text-end`, `tool-input-available`, `tool-output-available`, `error`, `finish`, `[DONE]`.
- An Adapter converts LangGraph `astream` output into this protocol. Tool calls are streamed with their full arguments and results. qwen3 runs with thinking on so Ollama separates the reasoning from the answer; the Adapter drops it, so there are no reasoning parts.

## Data

- `backend` seed script builds SQLite `store.db` (gitignored) from the read-only `data/` CSVs and parses `products.specs` from JSON.
- Re-seeding rebuilds the catalog, customer, and order tables but keeps `complaints`. `--reset` wipes everything.
- Source data is not modified. Known problems are documented rather than fixed:
  - Product names conflict with the brand in their descriptions (e.g. products 135, 137, 139, 140, 142, 144). The prompt treats the name as authoritative.
  - The Policy Manual contradicts itself: two phone numbers, an email with an accent, and inconsistent installment minimums. The Assistant gives the more conservative answer and suggests confirming with the store.
  - Duplicate customer email.
- `STORE_TODAY` (default `2026-03-25`) is the reference date for policy windows and is injected into the prompt. For delivered Orders, `estimated_delivery` stands in for the delivery date, and the Assistant says so.

## Complaints

- Only identified Customers can file a Complaint. Visitors get the WhatsApp number and email instead.
- Fields: `complaint_id`, `customer_id`, `order_id?` (must belong to the Customer), `category` (`product_defect | delivery | service | payment | other`), `description` (the Assistant's PT-BR summary), `conversation_id`, `created_at` (real time, not `STORE_TODAY`). There is no status.
- Confirmation is enforced by the prompt: the Assistant summarizes and asks "Posso registrar?" before calling the tool. It replies with "Protocolo #N" and the 24-business-hour promise.
- Complaints cannot be updated, resolved, or deleted. That is the documented trade-off.

## Prompt

- The template file lives under `backend/.../prompts/system.md`. Instructions are in English and the Assistant replies in PT-BR, or in the customer's language. The UI locale does not affect the reply language.
- Sections, in order:
  1. Identity and tone (§7.1).
  2. Context: store date, and the Customer's first name or Visitor.
  3. Scope: instruments only, Accessories redirected politely, off-topic questions declined, never discuss other Customers.
  4. Tool rules: never state price, stock, timing, or Order facts without a tool call this turn; policies via `search_policies` with section citation; the name beats the description; the more conservative answer on manual conflicts; Complaints confirmed before filing.
  5. Presentation: §6.2 (Promotional Price next to List Price and discount %) and §7.3 (out of stock, discontinued, coming soon, expired promotions).
  6. Style: concise, light markdown only (bold and short lists, no tables or headings).
- Guardrails are prompt-only. Security-critical rules are enforced in code. No classifier for the MVP.

## Frontend (Vite + React + shadcn + AI Elements)

- `useChat` from `@ai-sdk/react`, with `prepareSendMessagesRequest` sending only `{conversation_id, message}`.
- i18n: `react-i18next` with `pt-BR` (default) and `en`. A header toggle switches language and the choice is persisted in `localStorage`.
- Routes:
  - `/`: Chat.
  - `/complaints`: Complaints.
  - 404 for anything else.
- Header: store name, Chat and Complaints navigation, and the language toggle. On the chat page only, it also has:
  - The Customer Combobox ("Name · City · N pedidos", Visitor first, loaded once with `pageSize=50`).
  - The model Select, with an availability dot; unavailable models are disabled.
  - A "Clear chat" button, which calls `DELETE /chat/{id}` and generates a new UUID.
- Chat page:
  - AI Elements `Conversation`, `Message` (markdown), `Tool` chips, and `PromptInput`.
  - Empty state with challenge-scenario `Suggestion`s; Order suggestions appear only when a Customer is selected.
  - A divider when the model changes.
  - A confirmation `AlertDialog` when switching Customer with messages present, followed by a new Conversation.
  - Stopped replies stay visible, marked as interrupted.
- Complaints page: a Customer filter Combobox ("All customers"), a `Card` grid (protocol, category `Badge`, customer, order, relative date, description), `Pagination`, an empty state, and a manual refresh button.
- Defaults are Visitor and the model with `default: true`.
- Errors:
  - Backend down: a banner, and sending is disabled.
  - 400/409/503: a `sonner` toast.
  - Errors mid-stream: shown inline with "Try again".

## Repo and quality

- Layout: `backend/` (uv, Python 3.12, FastAPI, LangChain v1, `langchain-ollama`, `langchain-openai`, pydantic-settings, `.env.example`), `frontend/` (pnpm), `bruno/` (collection), and `data/` (read-only source).
- `pytest` tests that make no model calls cover: tool scoping, price math, chunking, the 400/409 cases, Conversation binding, rollback, and Complaint validation.
- A scripted eval set runs against each model: the challenge scenarios, off-topic questions, Accessories, jailbreaks, another Customer's Order, and complaint confirmation. Its transcripts become the 3–5 example conversations.
- Optional LangSmith tracing, enabled through an environment variable.

## README must cover

- Setup: Ollama models, OpenAI key, seed, backend, frontend, and Bruno.
- Justification for each decision, linking the ADRs. Note that full-manual context was a viable alternative to RAG.
- Assumptions: `STORE_TODAY`, the delivery-date stand-in, and that the complaints screen is a staff view.
- Known limitations:
  - Data problems.
  - No authentication, so the customer header is trusted.
  - In-memory Conversations.
  - Read-only Complaints.
  - No out-of-hours behaviour.
  - Prompt-only guardrails.
- What we would do with more time:
  - Staff authentication.
  - Complaint lifecycle.
  - A per-provider index upgrade path.
  - An input classifier if the eval set shows drift.
- How AI coding assistants were used, including this design session.
