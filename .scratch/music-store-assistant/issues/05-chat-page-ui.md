# 05: Chat page in the UI

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A person chats with the Assistant in the browser: they type a question, watch the reply stream in, see expandable chips for the tools the Assistant consulted, clear the chat to start over, switch model mid-Conversation (history kept, divider shown), and switch Customer after confirming, which starts a new Conversation. An empty chat offers starter questions.

**Blocked by:** 04 (Chat API: streaming Assistant that answers catalog questions).

**Status:** ready-for-agent

- [ ] The chat uses the AI SDK chat hook against `POST /chat`, customized to send only `{ conversation_id, message }`, plus the `x-customer-id` (omitted for Visitor) and `x-model` headers. The Conversation id is a client-generated UUID.
- [ ] Built with AI Elements: Conversation with auto-scroll, Message with markdown rendering, Tool chips (expandable inputs and results), and PromptInput pinned at the bottom.
- [ ] Clear chat calls `DELETE /chat/{id}`, generates a new Conversation id, and empties the view.
- [ ] Changing the Customer with messages present opens a confirmation dialog. Confirming starts a new Conversation, and cancelling keeps the current Customer. With no messages, it switches silently.
- [ ] Changing the model keeps the Conversation and inserts a visible divider naming the new model.
- [ ] The empty state shows suggestions from the challenge scenarios (Violões up to R$1000, store address, Takamine GD20 price, returning an Order). Order-related suggestions appear only when a Customer is selected.
- [ ] Sending is disabled while a reply streams.
- [ ] A reload starts a fresh Conversation.
- [ ] All strings go through i18n.
