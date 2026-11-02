# music-store-agent

A customer-service Assistant for Empório da Música, a musical-instrument store in Campo Grande/MS (technical challenge: `desafio_tecnico_ai_eng_artefact.pdf`). It answers questions about the catalog, prices and promotions, a Customer's own Orders and the store's Policy Manual, and files Complaints. It replies in Brazilian Portuguese by default, and in the customer's language if they write in another one.

It has three parts:

| Folder | What it is |
|---|---|
| `backend/` | Python 3.12, FastAPI and LangChain v1. The agent, its tools, the streaming chat API, the seed script and the eval. See also [`backend/README.md`](backend/README.md). |
| `frontend/` | Vite, React, shadcn/ui and AI Elements. A chat page and a staff Complaints page, in `pt-BR` and `en`. |
| `bruno/` | A [Bruno](https://www.usebruno.com/) collection with a request for every endpoint. |

Read-only source data lives in `data/` (CSVs and the Policy Manual PDF). Domain vocabulary is in [`GLOSSARY.md`](GLOSSARY.md), the agreed design is in [`docs/design.md`](docs/design.md) and the hard-to-reverse decisions are in [`docs/adr/`](docs/adr/).

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you), [Node.js](https://nodejs.org/) and [pnpm](https://pnpm.io/).
- [Ollama](https://ollama.com/) for the local models and for the local embeddings.
- An OpenAI API key, only if you want the API model.

### 1. Models

```
ollama pull qwen3:4b    # default chat model
ollama pull qwen3:8b    # larger local chat model
ollama pull bge-m3      # embeddings for Policy Manual search, local mode
```

The API model, `gpt-6-luna`, is optional. To enable it, set `OPENAI_API_KEY` in `backend/.env` (next step). Without a key it is shown as unavailable in the interface and the rest works normally. Policy search for the API model uses OpenAI embeddings (`text-embedding-3-small`) and does not need Ollama.

The local models are the default because they are free: the whole project runs on a laptop with no account and no network after the pulls. A small GPU helps. `qwen3:4b` is the lighter of the two.

### 2. Backend

```
cd backend
uv sync
cp .env.example .env     # optional keys and overrides are described inside
uv run seed              # builds music_store.db from ../data
uv run uvicorn music_store.app:app --reload
```

The API listens on `http://localhost:8000`. The interactive docs are at `/docs`.

- `uv run seed` rebuilds the store tables (catalog, Customers and Orders) and keeps the Complaints. `uv run seed --reset` wipes everything, Complaints included.
- The most useful `.env` settings: `OPENAI_API_KEY`, `DEFAULT_MODEL` (one of the three model ids) and `REFERENCE_DATE` (see [Assumptions](#assumptions)).

### 3. Frontend

```
cd frontend
pnpm install
cp .env.example .env     # optional: VITE_API_URL, default http://localhost:8000
pnpm dev
```

Open `http://localhost:5173`. In the header, pick a Customer (or stay a Visitor) and a model, and chat. The Complaints page (`/complaints`) is the staff view of every filed Complaint.

Ideas to try: "Quais violões vocês têm até R$ 1000?", "Quanto custa o violão Takamine GD20?", "Qual é o endereço da loja?" (as a Visitor), and, as Pedro Henrique Oliveira (Customer 3), "Posso devolver o meu pedido 1?".

### Using the Bruno collection

Open the `bruno/` folder as a collection in Bruno and select the `local` environment (`baseUrl` is `http://localhost:8000`). It has requests for customers, models, chat (Visitor, Customer, Orders, Policy and Complaint), Complaints and the error cases. Chat requests stream Server-Sent Events. Send a second request with the same `conversation_id` to continue a conversation. Chat requests set the Customer with the `x-customer-id` header (drop it to be a Visitor). Add an `x-model` header to pick a model; without it the default is used.

### Tests and eval

```
cd backend
uv run pytest                      # no model calls, no network
uv run ruff check . && uv run ruff format --check .

cd ../frontend
pnpm typecheck && pnpm lint
```

The eval is separate from the tests. It needs a running server, and it plays 12 scenarios against each available model (the challenge questions, scope, safety and the Complaint flow):

```
cd backend
uv run uvicorn music_store.app:app    # in one terminal
uv run python -m evals                # in another; --model and --scenario narrow it down
```

Transcripts and a pass/fail table are saved to `backend/evals/transcripts/<timestamp>/` (git-ignored). The Complaint scenario files a real Complaint, so point the server at a throwaway database. More options are in [`backend/README.md`](backend/README.md#eval).

### Optional: LangSmith

To trace every Assistant run, set these in `backend/.env` and restart the server:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your key>
LANGSMITH_PROJECT=music-store-assistant
```

Tracing is off by default and is passed per request, not through process environment, so a missing key never breaks the chat.

## Technical decisions

Each decision below is explained here. The ADRs in `docs/adr/` are "more info" for the three hardest-to-reverse ones, for readers who want the full reasoning and the options considered.

### Framework and approach: a tool-calling agent with fixed tools

The Assistant is a LangChain v1 agent (`create_agent`, built on LangGraph) that decides, turn by turn, which tool to call and then writes the answer from the tool results. The tools are:

| Area | Tools |
|---|---|
| Catalog and prices | `search_products`, `get_product`, `list_categories`, `list_active_promotions` |
| Orders (own only) | `list_my_orders`, `get_my_order` |
| Policies | `search_policies` |
| Complaints | `register_complaint` |

The database is reached only through these fixed, parameterized tools. There is no text-to-SQL. The reason is the Orders: they must be visible only to the Customer they belong to, and with no login the only reliable place to enforce that is code. The Order tools take no customer argument. The Customer comes from the request (through LangChain's runtime context), so the model never sees or chooses a customer id and no prompt can widen its reach. Asking for someone else's Order gives the same "not found" as asking for one that does not exist. Text-to-SQL would make this depend on the model's obedience, and small local models write unreliable SQL. The cost is flexibility: a new kind of question needs a new tool. For a store assistant with a handful of question types that is a good trade. ([ADR 0001](docs/adr/0001-fixed-scoped-tools-over-text-to-sql.md))

The tools also do the arithmetic. List Price, Promotional Price, discount percentage and PIX price are computed in code and returned to the model, which is told to use them exactly as given. The PIX discount (5%) never stacks on a promotion. Language models are not reliable calculators, and a wrong price is the worst mistake a store assistant can make.

### Models and provider

Three models are allowlisted, and the user picks one in the interface (or with the `x-model` header):

| Model | Provider | Role |
|---|---|---|
| `qwen3:4b` | Ollama (local) | **Default.** Free, runs on a laptop. |
| `qwen3:8b` | Ollama (local) | Larger local option. |
| `gpt-6-luna` | OpenAI (API) | Optional, used with a key. |

Qwen3 is the default because it is free: nobody needs an account, a key or a connection to run and review the project, and no customer data leaves the machine. Qwen3 also supports tool calling and a thinking mode. Thinking stays on, because with it off Ollama's template leaves the model inside an unclosed `<think>` block and the reasoning leaks into the answer. The stream adapter forwards the reasoning as separate parts, and the chat shows it in a collapsed block. Ollama gets an explicit 16k context window (its small default silently cuts the start of the request, the system prompt, once tool results pile up) and Qwen's recommended thinking-mode sampling (greedy decoding makes it loop in its thoughts).

`gpt-6-luna` is the model to use when answer quality matters more than cost, and the eval makes the case for it. In the latest run it passed all 12 scenarios, including the Complaint flow that both Qwen models stumbled on, and it was the only model to do so. It is also cheap to run: it is used with low reasoning effort, so each reply is fast and uses few tokens, which makes it a very reasonable choice for a real deployment. It stays optional, and Qwen stays the default, only because Qwen is free and keeps the project runnable offline. See [Eval findings](#eval-findings) for the numbers.

Which model answers a request is resolved by a middleware against the allowlist: an unknown model is a 400 and a model whose provider is unreachable is a 503. The same place is where per-Customer model entitlements would be enforced later.

### Retrieval architecture: search the Policy Manual on demand

The Policy Manual (`data/store-policies.pdf`) is split by section, one chunk per subsection with the parent section title prepended, and embedded into an in-memory vector index. `search_policies` returns the best 3 to 4 chunks. Retrieval is a tool the agent chooses to call, not context pasted into every turn. The prompt requires a search, in the current turn, for any policy question (hours, address, contacts, payment, returns, shipping, warranty). Store hours and contact details come only from retrieval, so the manual stays the single source of truth.

There is one index per provider: Ollama `bge-m3` for local models and OpenAI embeddings for the API model. Each chat request searches the index that matches its model's provider. Vectors from different embedding models cannot be compared, so one shared index would force one provider on everyone: either API mode would still need a local Ollama, or local mode would need the internet and a key. Each index is built on its first search, so the server starts even when one provider is down. ([ADR 0003](docs/adr/0003-one-embedding-index-per-provider.md))

**Considered alternative: put the whole manual in the prompt.** The manual is only 8 pages, about 1,750 words, so sending all of it on every turn would work and would remove retrieval failures altogether. We did not do it for three reasons. It adds thousands of tokens to every request, which is slow and expensive on a small local model and a real cost on the API. A long prompt crowds the small model's context and dilutes its attention, and most questions (catalog, Orders) do not need the manual at all. And retrieval returns section numbers and exact passages, which makes answers traceable and the eval able to check that a policy question really triggered a search. If the manual stays this small, full-context is a defensible simplification. The retrieval design pays off as it grows.

### Prompt strategy

One system prompt template (`backend/src/music_store/assistant/prompts/system_v1.md`) is rendered per request with the reference date and who is talking (the Customer's first name, or Visitor). It is written in English and the Assistant replies in Brazilian Portuguese, or in the customer's language. Its sections are, in order:

1. Identity and tone: a friendly, informal but professional store assistant.
2. Context: today's date and the audience. An identified Customer is never asked to identify themselves.
3. Scope: instruments only. Accessories get a polite "we do not sell those" and a suggestion of partner stores. Off-topic questions get a short decline without any tool call. Other Customers are never discussed. The prompt is never revealed, and role-play or "ignore previous instructions" requests are declined.
4. Tool rules: never state a price, stock level, or Order fact without a tool call in the current turn. Use tool prices exactly. Policies answered only from search results, with the more conservative answer when passages conflict. A product's name wins over its description. Return questions need both the Order and a policy search.
5. Presentation: a promotional price is shown next to the list price and discount, and expired promotions, out-of-stock, discontinued and coming-soon products each have a rule.
6. Style: concise, light markdown only.

The prompt was tightened by running the eval and fixing what drifted. Notable additions: forbidding tool calls written out as text, requiring the answer to address the question asked rather than greeting again, and never filing a Complaint in the same reply that first shows the summary. Guardrails are prompt-only (see [Known limitations](#known-limitations)). Anything security-critical, like which Orders a Customer can see, is enforced in code instead.

### Interface

The frontend is a Vite and React app with shadcn/ui and AI Elements, using `useChat` from the AI SDK. The backend streams answers with the Vercel AI SDK UI message stream protocol over Server-Sent Events. An adapter turns LangGraph output into that protocol: text, reasoning, and tool calls with their full arguments and results, so the chat shows what the Assistant looked up. Highlights:

- Header controls to pick the Customer (a combobox showing name, city and Order count, Visitor first), the model (with an availability dot) and the language (`pt-BR` or `en`, remembered in `localStorage`). Switching Customer asks for confirmation and starts a new Conversation.
- Suggestion chips for the challenge scenarios, with Order ones only when a Customer is selected.
- A divider when the model changes mid-Conversation, a stop button, and "try again" on errors. A stopped reply stays visible, marked as interrupted.
- A separate Complaints page, a staff view with a Customer filter, pagination and manual refresh.
- A banner and disabled input when the backend is down, and toasts for the API's 400, 409 and 503 errors.

A chat UI was chosen over a CLI because it is what a store customer would use, and because it shows tool calls and reasoning, which makes the agent easy to review. Pre-stream failures are regular HTTP errors and mid-stream failures appear inline.

### History persistence: server-held, in memory

Conversation history lives on the server, in a LangGraph in-memory checkpointer keyed by a client-generated Conversation id. The client sends only `{conversation_id, message}`. The reason is security: if the client re-sent the whole history, anyone could forge earlier Assistant turns (a fake "jailbreak completed" reply, a made-up price), which primes a model far more strongly than a user message. Keeping history on the server removes that attack and also keeps tool results in context.

Details that matter:

- A Conversation is bound to the Customer or Visitor of its first message. A request with a different identity gets a 409, so the frontend starts a new Conversation when you change Customer.
- Only the last 20 messages are sent to the model, always starting on a Customer message so a tool result never appears without its request. Conversations idle for an hour are evicted.
- A turn that fails or is stopped is rolled back, so the stored history never has a tool request without its result. "Try again" just resends the message.
- Messages in one Conversation are processed one at a time. A concurrent one gets a 409.
- History is not persisted: a restart or a page reload starts fresh, and there is no history endpoint. Customer questions are sparse and unrelated, so this is acceptable for the prototype.

Complaints are the exception: they are real records in SQLite and survive restarts and re-seeding. ([ADR 0002](docs/adr/0002-server-held-conversations.md))

### Data treatment

The source CSVs and PDF are never modified. The seed script loads them into SQLite (`music_store.db`, git-ignored) and parses each product's JSON `specs`. Data problems are documented (see [Known data problems](#known-data-problems)) and handled in the prompt rather than silently "fixed" in the database, so the store's data stays the owner's data. Orders do not store the price paid, so the stored total is shown as is and never recomputed.

Complaints have their own table: id, Customer, optional Order (checked to belong to that Customer), category (`product_defect`, `delivery`, `service`, `payment` or `other`), the Assistant's Portuguese summary, the Conversation id and a real creation time. Only identified Customers can file one. Visitors are sent to the store's WhatsApp number and email. Filing is confirmed first: the Assistant summarizes and asks "Posso registrar?" and calls the tool only after the next message confirms. It then answers with "Protocolo #N" and the 24-business-hour promise from the manual.

## Database Schema

### ER Diagram

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : "classifies"
    CUSTOMERS  ||--o{ ORDERS : "places"
    ORDERS     ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS   ||--o{ ORDER_ITEMS : "sold as"
    PRODUCTS   ||--o{ PROMOTIONS : "discounted by"

    CATEGORIES {
        INTEGER category_id PK
        TEXT name
        TEXT description
    }
    PRODUCTS {
        INTEGER product_id PK
        INTEGER category_id FK
        TEXT name
        REAL price_brl
        TEXT description
        INTEGER stock_quantity
        TEXT status "active | coming_soon | discontinued"
        TEXT specs "JSON string"
        DATE created_at
    }
    PROMOTIONS {
        INTEGER promotion_id PK
        INTEGER product_id FK
        INTEGER discount_percent
        TEXT description
        INTEGER is_active "0 or 1"
    }
    CUSTOMERS {
        INTEGER customer_id PK
        TEXT name
        TEXT phone
        TEXT email
        TEXT city
    }
    ORDERS {
        INTEGER order_id PK
        INTEGER customer_id FK
        DATE order_date
        TEXT status "pending | confirmed | shipped | delivered | cancelled"
        REAL total_brl
        TEXT payment_method "pix | boleto | debit | credit_3x | credit_6x | credit_12x"
        TEXT tracking_code
        DATE estimated_delivery
        TEXT notes
    }
    ORDER_ITEMS {
        INTEGER order_id PK, FK
        INTEGER product_id PK, FK
        INTEGER quantity
    }
```

### Tables

#### categories
| Column | Type | Constraints |
|---|---|---|
| category_id | INTEGER | PK |
| name | TEXT | NOT NULL |
| description | TEXT | |

#### products
| Column | Type | Constraints |
|---|---|---|
| product_id | INTEGER | PK |
| category_id | INTEGER | FK → categories.category_id |
| name | TEXT | NOT NULL |
| price_brl | REAL | NOT NULL |
| description | TEXT | |
| stock_quantity | INTEGER | NOT NULL |
| status | TEXT | `active`, `coming_soon`, `discontinued` |
| specs | TEXT | JSON object. Its keys vary by category. |
| created_at | DATE | |

#### promotions
| Column | Type | Constraints |
|---|---|---|
| promotion_id | INTEGER | PK |
| product_id | INTEGER | FK → products.product_id |
| discount_percent | INTEGER | 0–100 |
| description | TEXT | Campaign name, e.g. "Black Friday" |
| is_active | INTEGER | 0 or 1 |

#### customers
| Column | Type | Constraints |
|---|---|---|
| customer_id | INTEGER | PK |
| name | TEXT | NOT NULL |
| phone | TEXT | |
| email | TEXT | |
| city | TEXT | |

#### orders
| Column | Type | Constraints |
|---|---|---|
| order_id | INTEGER | PK |
| customer_id | INTEGER | FK → customers.customer_id |
| order_date | DATE | |
| status | TEXT | `pending`, `confirmed`, `shipped`, `delivered`, `cancelled` |
| total_brl | REAL | |
| payment_method | TEXT | `pix`, `boleto`, `debit`, `credit_3x`, `credit_6x`, `credit_12x` |
| tracking_code | TEXT | Nullable |
| estimated_delivery | DATE | Nullable |
| notes | TEXT | Nullable |

#### order_items
| Column | Type | Constraints |
|---|---|---|
| order_id | INTEGER | PK (part), FK → orders.order_id |
| product_id | INTEGER | PK (part), FK → products.product_id |
| quantity | INTEGER | NOT NULL |

The CSV has no surrogate id. `(order_id, product_id)` is unique in the data, so it works as a composite primary key.

### Relationships

| Parent | Child | Cardinality | FK |
|---|---|---|---|
| categories | products | 1 : N | products.category_id |
| customers | orders | 1 : N | orders.customer_id |
| orders | order_items | 1 : N (at least 1) | order_items.order_id |
| products | order_items | 1 : N | order_items.product_id |
| products | promotions | 1 : N | promotions.product_id |

`orders` and `products` have an M:N relationship, resolved through `order_items`.

### Notes and caveats

- **`customers.email` and `orders.tracking_code` are not `UNIQUE`**. There might be duplicate emails and many empty tracking codes (still has not shipped or canceled).
- **Several promotions can target one product.** For example, product 96 has two. Only `is_active = 1` rows should count as current.
- **`orders.total_brl` is stored, not calculated.** `order_items` doesn't save the price paid, so the total can't be recomputed from items and current prices.
- **`products.specs` is a JSON string.**
- Status and payment method are free text. **Not normalized.** 