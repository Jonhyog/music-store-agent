# 04: Chat API: streaming Assistant that answers catalog questions

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** Through the API (Bruno), a person sends a message in a Conversation and receives the Assistant's reply as a stream. The Assistant speaks in the store's persona in Brazilian Portuguese (or the customer's language), stays on scope, and answers catalog questions by searching Products and Categories, with each tool call visible in the stream. Conversations are held on the server and bound to one identity (ADR 0002).

**Blocked by:** 03 (Model registry, `/models` and header middlewares).

**Status:** ready-for-agent

- [ ] `POST /chat` accepts `{ conversation_id: uuid, message: 1–2000 chars }` with the resolved Customer/Visitor and model, and responds with an SSE stream in the Vercel AI SDK UI message stream protocol, including the identifying header. Events: `start`, `text-start`, `text-delta`, `text-end`, `tool-input-available`, `tool-output-available`, `finish`, `[DONE]`.
- [ ] A stream Adapter converts the LangChain v1 agent's streamed output (message chunks and step updates) into those events. Tool calls carry the tool name, arguments and full result.
- [ ] Conversations are stored in an in-memory checkpointer keyed by `conversation_id`. A Conversation is bound to the identity of its first message, and a request with a different identity returns 409.
- [ ] A per-Conversation lock returns 409 `conversation busy` for a concurrent message.
- [ ] `DELETE /chat/{conversation_id}` returns 204, even for an unknown id.
- [ ] Catalog tools: search Products (free text, Category, maximum price, in-stock only), get a Product by name or id, list Categories. Results include List Price, stock quantity, Catalog Status and parsed specs.
- [ ] A versioned system prompt template (English instructions) covers identity and tone (§7.1), context (reference date, Customer first name or Visitor), scope (instruments only, Accessories redirected politely, off-topic declined), the tool rule "never state price/stock without a tool call this turn" and "product name beats description", and light markdown style.
- [ ] The Customer is passed to tools through runtime context, never as a model-visible argument.
- [ ] Optional LangSmith tracing, enabled by environment settings.
- [ ] Tests with the fake chat model cover the stream event sequence and header, tool events for a catalog search, the identity-mismatch 409, the busy 409, DELETE, and 422 on an invalid body.
- [ ] Bruno requests for a streaming chat (as a Visitor and as a Customer) and DELETE.
