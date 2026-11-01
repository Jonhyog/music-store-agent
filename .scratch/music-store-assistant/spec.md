# Spec: Empório da Música Assistant (MVP)

Status: ready-for-agent

References: `GLOSSARY.md` (vocabulary), `docs/adr/0001`–`0003` (binding decisions), `docs/design.md` (agreed design), `desafio_tecnico_ai_eng_artefact.pdf` (challenge brief), `data/store-policies.pdf` (Policy Manual).

## Problem Statement

Empório da Música's staff are overloaded with repetitive questions: store hours, Order status, Product prices and availability, and returns and payment rules. Customers wait for answers a machine could give from the store's own data and Policy Manual. Staff also have no single place to see the Complaints raised. The store needs a prototype virtual Assistant that answers in the store's voice, knows when to look up live data and when to consult policy, never invents prices or stock, keeps each Customer's Orders private, stays within the store's scope, and records Complaints for the team.

## Solution

A text-chat Assistant with a web UI and an HTTP API:

- The Assistant answers Customers and Visitors in Brazilian Portuguese, or in the language the person writes in. Its tone follows the Policy Manual: informal but professional.
- It looks up Products, Categories, active Promotions, and the Customer's own Orders through fixed tools. It retrieves Policy Manual sections when a policy question comes up, and cites the section it used.
- It computes prices exactly, including Promotional Price and PIX Discount rules. It politely redirects Accessory requests and declines off-topic requests.
- An identified Customer can file a Complaint after confirming it. They receive a protocol number and the store's 24-business-hour response promise.
- The person chatting picks who they are (a Customer or Visitor) and which model answers (local or API) from the UI. Replies stream in, and the UI shows which tools were consulted.
- A Complaints screen lists every recorded Complaint as cards, with an optional filter by Customer.
- There is no authentication. The chosen Customer is trusted, but Order visibility is enforced in code, not by the model.

## User Stories

### Asking about the catalog

1. As a Visitor, I want to ask which instruments of a Category are available under a price limit, so that I can find options within my budget.
2. As a Visitor, I want to ask the price of a Product by name, so that I know how much it costs.
3. As a Visitor, I want prices shown with any active Promotion as the Promotional Price next to the List Price and discount percentage, so that I understand the deal transparently.
4. As a Visitor, I want to know the PIX price of a Product, so that I can decide how to pay.
5. As a Visitor, I want the Assistant to never stack the PIX Discount on a Promotional Price, so that I'm not promised a discount the store won't honour.
6. As a Visitor, I want to know whether a Product is in stock, so that I don't travel to the store for nothing.
7. As a Visitor asking about an out-of-stock Product, I want similar available alternatives suggested, so that I still find something to buy.
8. As a Visitor asking about a discontinued Product, I want to be told it's no longer sold and offered equivalents, so that I'm not misled.
9. As a Visitor asking about a coming-soon Product, I want to be told it isn't available yet, so that I can plan.
10. As a Visitor, I want to ask about a Promotion I heard of, and be told honestly if it's no longer active along with the current price, so that I'm never promised an expired discount.
11. As a Visitor, I want to list the active Promotions, optionally within a Category, so that I can find deals.
12. As a Visitor, I want to see the Categories the store sells, so that I know what kinds of instruments are available.
13. As a Visitor, I want Product specs (top wood, strings, electronics, etc.) summarized when relevant, so that I can compare instruments.
14. As a Visitor, I want the Product name treated as authoritative when its description mentions a different brand, so that I get consistent answers.

### Asking about policies

15. As a Visitor, I want to ask the store's address, phone and email, so that I can contact or visit it.
16. As a Visitor, I want to ask the store's opening hours, so that I know when to visit.
17. As a Visitor, I want to ask which payment methods and installment rules apply, so that I can plan my purchase.
18. As a Visitor, I want to ask about the exchange and return policy, so that I know my rights.
19. As a Visitor, I want to ask about shipping costs and delivery times inside and outside Campo Grande, so that I know when I'd receive an instrument.
20. As a Visitor, I want to ask about warranty coverage, so that I know what's protected.
21. As a Visitor, I want policy answers to cite the Policy Manual section they come from, so that I can trust them.
22. As a Visitor, when the Policy Manual contradicts itself, I want the more conservative answer and a suggestion to confirm with the store, so that I'm not misinformed.

### Asking about my Orders

23. As a Customer, I want to list my Orders, optionally by Order Status, so that I can see my purchase history.
24. As a Customer, I want to ask the status of a specific Order, so that I know where it is.
25. As a Customer, I want my tracking code when my Order has shipped, so that I can follow the delivery.
26. As a Customer, I want my estimated delivery date, so that I can plan to receive it.
27. As a Customer, I want to see which Products and quantities are in my Order, so that I can confirm what I bought.
28. As a Customer with a cancelled Order, I want to know the cancellation reason recorded by the store, so that I understand what happened.
29. As a Customer, I want to ask whether I can return my Order, and have the return policy applied to my Order's dates against the store's reference date, so that I get a concrete answer.
30. As a Customer, I want the Assistant to say when it's using the estimated delivery date as the delivery date, so that I understand the basis of the answer.
31. As a Customer, I want my Orders to be invisible to anyone chatting as a different Customer or as a Visitor, so that my data is private.
32. As a Customer, if I ask about an Order number that isn't mine, I want the same "not found" answer as for a non-existent Order, so that other Customers' Orders aren't revealed.
33. As a Visitor asking about Orders, I want to be told the Assistant needs to know which Customer I am, so that I understand why it can't answer.
34. As a Customer, I want to be greeted by my first name, so that the conversation feels personal.

### Complaints

35. As a Customer, I want to raise a Complaint in the chat, so that the store team follows up.
36. As a Customer, I want the Assistant to summarize my Complaint (category, related Order, description) and ask for confirmation before filing it, so that nothing is filed by mistake or wrongly.
37. As a Customer, I want a protocol number and the 24-business-hour response promise after filing, so that I can reference it later.
38. As a Customer, I want to link a Complaint to one of my Orders, so that the team has context.
39. As a Customer, I want an attempt to link a Complaint to an Order that isn't mine to be refused, so that Complaints stay consistent.
40. As a Visitor wanting to complain, I want to be told I need to be identified, and given the WhatsApp number and email, so that I still have a way to reach the store.
41. As store staff, I want to see all Complaints as cards, newest first, so that I can follow up.
42. As store staff, I want to filter Complaints by Customer, so that I can see one Customer's history.
43. As store staff, I want each Complaint card to show the protocol number, category, Customer name, Order (if any), when it was raised, and the description, so that I have what I need to act.
44. As store staff, I want Complaints to survive a server restart and a data re-seed, so that nothing is lost.
45. As store staff, I want paginated Complaints and a manual refresh, so that the list stays usable as it grows.

### Scope and safety

46. As the store, I want the Assistant to politely say the store sells only instruments when asked for Accessories, and suggest partner stores, so that the policy is followed.
47. As the store, I want off-topic requests (homework, coding, politics, general chit-chat) politely declined and steered back to the store, so that the Assistant stays on brand.
48. As the store, I want the Assistant to never state prices, stock, delivery times or Order facts without consulting the system in that turn, so that it never misleads customers.
49. As the store, I want jailbreak and role-play attempts not to change the Assistant's scope or persona, so that it can't be turned against the brand.
50. As the store, I want Conversation history kept on the server, so that nobody can forge earlier Assistant replies to manipulate it.
51. As the store, I want a Conversation to stay bound to the Customer or Visitor who started it, so that one person's context never leaks into another's.
52. As the store, I want the Assistant to never discuss other Customers, so that privacy is respected.
53. As the store, I want complaints and unresolved matters routed to the WhatsApp number and email when the Assistant can't settle them, so that customers reach a human.

### Chat experience (UI)

54. As a person chatting, I want replies to stream word by word, so that I'm not staring at a blank screen.
55. As a person chatting, I want to see which tools the Assistant consulted (e.g. "Consultando pedidos…"), expandable to show inputs and results, so that I understand where answers come from.
56. As a person chatting, I want to pick a Customer from a searchable list showing name, city and number of Orders, with Visitor first, so that I can quickly choose who I am.
57. As a person chatting, I want to be asked for confirmation before switching Customer mid-Conversation, and then start a new Conversation, so that I don't lose context by accident.
58. As a person chatting, I want to pick the model (local or API) from a list showing which models are available, with unavailable ones disabled, so that I can compare them.
59. As a person chatting, I want to switch models mid-Conversation and keep the history, with a visible divider, so that I can compare answers on the same context.
60. As a person chatting, I want a Clear chat button that starts a fresh Conversation, so that I can begin again.
61. As a person chatting, I want suggested starter questions on an empty chat, with Order-related ones only when a Customer is selected, so that I know what to ask.
62. As a person chatting, I want to stop a reply mid-stream, with the partial text kept and marked as interrupted, so that I control the conversation.
63. As a person chatting, I want a failed reply shown inline with a Try again action that resends my message, so that I can recover.
64. As a person chatting, I want a banner and disabled sending when the backend is unreachable, so that I know why nothing works.
65. As a person chatting, I want clear notifications for rejected requests (unknown Customer, unavailable model, busy Conversation), so that I know what went wrong.
66. As a person chatting, I want replies with light formatting (bold, short lists), so that product options are easy to scan.
67. As a person chatting, I want the interface in Portuguese by default and switchable to English, remembered across visits, so that it suits me.
68. As a person chatting, I want the Assistant's reply language to follow what I write, not the interface language, so that conversations feel natural.
69. As a person chatting, I want a reload to start a fresh Conversation, so that behaviour is predictable.
70. As anyone, I want a not-found page for unknown routes, so that I'm not stuck on a blank screen.
71. As anyone, I want navigation between Chat and Complaints in the header, so that I can move between screens.

### Developer and evaluator

72. As a developer, I want to run the Assistant fully locally on Ollama without internet or API keys, so that local mode is truly local.
73. As a developer, I want to switch to the API model per request, so that I can compare quality and latency.
74. As a developer, I want the server to start even if Ollama is down or no API key is set, with those models reported unavailable, so that one missing provider doesn't block the other.
75. As a developer, I want a one-command seed that builds the store database from the provided CSVs without modifying them, so that setup is reproducible.
76. As a developer, I want the store's reference date to be configurable, so that policy-window scenarios are reproducible.
77. As a developer, I want a Bruno collection covering every endpoint, including streaming chat, so that I can exercise the API without the UI.
78. As a developer, I want optional LangSmith tracing, so that I can inspect tool choices and capture evidence for the README.
79. As an evaluator, I want an eval script that runs the challenge scenarios and safety prompts against each model and saves transcripts, so that I can see the Assistant's behaviour and compare models.
80. As an evaluator, I want a README explaining setup, every technical decision with its rationale, assumptions, known limitations, and how AI coding assistants were used, so that I can judge the reasoning.
81. As an evaluator, I want 3–5 example conversations in the repo, including at least one that consults live data or applies a policy, so that I can see the Assistant working.

## Implementation Decisions

### Modules

- **Store database**: SQLite, built by a seed command from the read-only CSVs, following the schema in the README. Adds a `complaints` table. Re-seeding rebuilds catalog, customer and order tables and preserves `complaints`. A reset option wipes everything. Product specs are parsed from JSON. Source CSVs and the Policy Manual are never modified.
- **Catalog and pricing tools**: search Products (free text, Category, maximum price, in-stock only), get a Product by name or id, list Categories, list active Promotions (optional Category). Product results include List Price, active Promotion (if any) with discount %, Promotional Price, PIX price (only when there is no active Promotion), stock quantity, Catalog Status and parsed specs. Only Promotions with `is_active = 1` count. When several Promotions target one Product, the tool picks one deterministically (highest discount).
- **Order tools**: list my Orders (optional Order Status), get my Order by id. Both take **no customer argument** and read the Customer from the runtime context. They return Order Status, total, payment method, tracking code, estimated delivery, notes and Order Items with Product names. For a Visitor, or for an Order that isn't the Customer's, they return a uniform "not identified" or "not found" result (ADR 0001).
- **Complaint tool**: register a Complaint with category, description and an optional Order id. The Customer comes from context. It refuses Visitors and Orders that don't belong to the Customer. It returns the Complaint id and creation time.
- **Policy retrieval**: the Policy Manual is chunked by section, one chunk per subsection, with the parent section title prepended. One in-memory vector index per provider (ADR 0003), built lazily on first search. The policy search tool returns the top 3–4 chunks with section numbers.
- **Provider registry**: the single place that maps a model id from the config allowlist to its chat model and its provider's embedding model, and reports availability. The allowlist holds `qwen3:4b` (default, thinking disabled), `qwen3:8b` and `gpt-5.6-luna`. Embeddings are Ollama `bge-m3` for local models and an OpenAI embedding model for the API model. This is also the test seam (see Testing Decisions).
- **Agent**: LangChain v1 agent with all tools, a versioned system prompt template, a runtime context carrying the Customer (or Visitor), the selected model and the reference date, and an in-memory checkpointer keyed by Conversation id (ADR 0002).
- **Conversation manager**:
  - Binds each Conversation to the identity of its first message and rejects mismatches.
  - Holds one lock per Conversation and rejects concurrent turns.
  - Trims what's sent to the model to the last ~20 messages.
  - Evicts Conversations idle for more than one hour.
  - Rolls back a turn automatically on failure or client disconnect by removing every message added since the turn began.
  - Deletes a Conversation on request.
- **Stream adapter**: converts the agent's streamed output (message chunks and step updates) into the Vercel AI SDK UI message stream protocol over SSE: `start`, `text-start`, `text-delta`, `text-end`, `tool-input-available` (tool name and arguments), `tool-output-available` (full result), `error`, `finish`, and the `[DONE]` terminator, with the protocol's identifying response header. There are no reasoning parts.
- **HTTP layer (FastAPI)**:
  - CORS runs first.
  - Then a pure ASGI customer middleware: it reads `x-customer-id`, loads the Customer into request state (or Visitor when the header is absent), and returns its own JSON 400 for malformed or unknown ids.
  - Then a pure ASGI model middleware: it resolves `x-model` against the allowlist (default when absent), returning 400 for unknown models and 503 for unavailable ones. This is the future hook for per-Customer model entitlements.
  - A typed dependency only reads the resolved Customer.
- **System prompt** (English instructions, PT-BR replies or the customer's language), sections in order:
  1. Identity and tone (Policy Manual §7.1).
  2. Context: reference date, and the Customer's first name or Visitor.
  3. Scope: instruments only, Accessories redirected with partner-store suggestion, off-topic declined, never discuss other Customers.
  4. Tool rules: no price, stock, timing or Order claims without a tool call in the current turn; policies via retrieval with section citation; the product name beats the description; the more conservative answer on manual contradictions; Complaints summarized and confirmed before filing; Visitors pointed to contact channels for Complaints.
  5. Presentation: §6.2 Promotional Price next to List Price and discount %; §7.3 out-of-stock, discontinued and expired-promotion handling.
  6. Style: concise, light markdown only (bold and short lists, no tables or headings).

  Store hours and contact details are **not** hard-coded in the prompt; they come only from retrieval.
- **Frontend**:
  - Vite + React SPA, scaffolded with the shadcn CLI, using AI Elements and the AI SDK chat hook. The hook is customized to send only `{conversation_id, message}`, never the full history. The Conversation id is a client-generated UUID.
  - Routes: Chat (root), Complaints, and not-found.
  - i18n with `react-i18next`: `pt-BR` by default and `en`, with a header toggle persisted in local storage.
  - Header: store name, navigation, and the language toggle. On Chat only, it also holds the Customer Combobox, the model Select with availability indicator, and Clear chat.
  - Complaints screen: Customer filter, card grid, pagination, empty state, manual refresh.
- **Bruno collection**: one request per endpoint and error case, including a streaming chat request.
- **Eval script**: drives the running server over HTTP with fixed prompts per model and saves the transcripts.

### API contracts

- `GET /customers?page&pageSize` returns `{ customers: Customer[], page, total }`. Each Customer has `customer_id`, `name`, `phone`, `email`, `city` and `order_count`.
- `GET /models` returns `{ models: Model[] }`, with no pagination. Each Model has `id`, `provider`, `label`, `available` and `default`.
- `POST /chat`:
  - Headers: optional `x-customer-id` and `x-model`.
  - Body: `{ conversation_id: uuid, message: string (1–2000 chars) }`.
  - Returns an SSE stream in the AI SDK UI message stream protocol.
  - Errors before streaming starts:
    - 400: malformed or unknown customer, or unknown model.
    - 409: the Conversation belongs to a different identity, or is busy.
    - 422: invalid body.
    - 503: model provider unavailable.
  - Errors after streaming starts arrive as an `error` event, and the turn is rolled back.
- `DELETE /chat/{conversation_id}` returns 204, even if the Conversation doesn't exist.
- `GET /complaints?page&pageSize&customerId` returns `{ complaints: Complaint[], page, total }`, newest first.
  - Each Complaint has `complaint_id`, `customer_id`, `customer_name`, `order_id | null`, `category`, `description`, `conversation_id` and `created_at`.
  - This is a staff view: it ignores `x-customer-id`.
  - An unknown `customerId` returns an empty list.

### Schema addition

- `complaints`:
  - `complaint_id` INTEGER PK.
  - `customer_id` INTEGER FK, not null.
  - `order_id` INTEGER FK, nullable.
  - `category` TEXT, one of `product_defect | delivery | service | payment | other`.
  - `description` TEXT, not null.
  - `conversation_id` TEXT.
  - `created_at` TIMESTAMP, real wall-clock time, not the reference date.
  - There is no status column.

### Configuration

- Settings are read from environment / `.env`, with an example file committed:
  - Ollama base URL, OpenAI API key, default model.
  - Reference date, default `2026-03-25`.
  - Database path.
  - History window, idle eviction timeout.
  - CORS origins.
  - Optional LangSmith settings.

### Repository layout

- `backend/` is a Python 3.12 project managed by uv.
- `frontend/` is managed by pnpm.
- `bruno/` holds the collection.
- `data/` stays at the root as the read-only source.
- The generated database is gitignored.

## Testing Decisions

- **Good tests exercise external behaviour only**: HTTP requests in, status codes, JSON bodies and stream events out, plus what's observable in the database. They never assert on internal function calls, prompt wording, or LangGraph internals. Tests must not call real models or the network.
- **Seam A (primary): the backend HTTP API.**
  - Tests run the real application against a temporary database seeded from `data/`.
  - The provider registry is overridden with a scripted fake chat model, which emits predetermined tool calls and text, can raise partway through a turn, and supports tool binding. Fake deterministic embeddings replace the real ones.
  - Through this seam the tests cover:
    - Order scoping: another Customer's Order and a non-existent Order give identical results; Visitors are refused.
    - Customer middleware 400s; model 400 and 503.
    - Conversation identity 409 and busy 409.
    - Stream protocol event sequence and header.
    - Tool calls surfacing as input and output events.
    - Price math (Promotional Price, PIX price rules, multiple Promotions on one Product, inactive Promotions ignored), read from tool-output events.
    - Policy search results carrying section numbers.
    - Automatic rollback: after a mid-turn failure, the next turn succeeds and history contains no orphaned tool request.
    - `DELETE /chat`.
    - `/customers` pagination and `order_count`.
    - `/models` availability and default.
    - Complaint creation via the tool: Order ownership validation, Visitor refusal.
    - `/complaints` filtering, ordering and pagination.
- **Seam B (secondary): the seed command**, only for re-seed preserving Complaints and reset wiping them.
- **Eval (outside pytest, opt-in)**:
  - Runs the challenge scenarios against each real model through the running server: Category plus price ceiling, store address, Takamine GD20 price, and return eligibility.
  - Also runs Accessory requests, off-topic requests, jailbreak attempts, asking for another Customer's Order, and the complaint confirm-before-filing flow.
  - It checks behaviour (which tools were called, refusals, confirmation before filing), not exact wording. Saved transcripts feed the example conversations.
- **Frontend**: no automated tests in the MVP beyond type-checking and lint. Its behaviour is covered by Seam A, the Bruno collection, and manual testing.
- **Prior art**: none in the repo yet (greenfield). These tests establish the conventions.

## Out of Scope

- Authentication or authorization of any kind. The customer header is trusted.
- Persisting Conversations across restarts. Fetching history after a reload.
- Updating, resolving, assigning or deleting Complaints. Complaint status or lifecycle.
- Placing, changing or cancelling Orders. Checkout, payments, shipping quotes.
- An input classifier or moderation model. Guardrails are prompt-only, apart from code-enforced scoping.
- Out-of-business-hours behaviour (the reference date has no time of day).
- Per-Customer model entitlements (only the middleware hook exists).
- Cleaning or correcting the source data.
- Frontend automated tests.
- Deployment, containerization and production hardening.

## Further Notes

- Known data problems to document in the README:
  - Product names whose description mentions a different brand (e.g. products 135, 137, 139, 140, 142, 144).
  - Policy Manual contradictions: two phone numbers, an email with an accent, inconsistent installment minimums.
  - One duplicate customer email.
  - Only 18 of the 50 customers have Orders.
- Assumptions to document:
  - The reference date defaults to `2026-03-25`, the day after the latest Order.
  - The estimated delivery date stands in for the actual delivery date.
  - The Complaints screen is a staff view.
- The README should note that loading the full Policy Manual into context was a viable alternative to retrieval. Retrieval was chosen because it isn't always needed and it lays the groundwork for retrieving more than policies later.
- The local environment has an 8 GB GPU, which is why `qwen3:4b` is the default and `qwen3:8b` is offered for comparison. Ollama must be installed, with `qwen3:4b`, `qwen3:8b` and `bge-m3` pulled.
- The challenge requires a real commit history. Implementation should land in incremental commits.
