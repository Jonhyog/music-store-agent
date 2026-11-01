# 09: Conversation robustness

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** Chat keeps working when things go wrong. A reply that fails or is stopped leaves the Conversation in a clean state, so the next message works. A person can stop a reply mid-stream (the partial text stays, marked as interrupted), retry a failed reply inline, and gets clear feedback for rejected requests or an unreachable backend. Server memory stays bounded.

**Blocked by:** 05 (Chat page in the UI).

**Status:** ready-for-agent

- [ ] When a turn fails mid-stream, the server emits an `error` event and removes every message added since the turn began, so stored history never holds a tool request without its result.
- [ ] When the client disconnects mid-turn (Stop), the turn is cancelled and rolled back the same way.
- [ ] Only the most recent ~20 messages (configurable) are sent to the model.
- [ ] Conversations idle beyond the configured timeout (default 1 hour) are evicted.
- [ ] Tests with the fake chat model: a failure after a tool request, then a follow-up turn that succeeds with no orphaned tool request in history; a disconnect rolls back; the history window limits what the model receives; idle eviction removes a Conversation.
- [ ] UI: a Stop control during streaming, with the stopped reply kept and marked interrupted. An `error` event shows inline on the message with a Try again action that resends the same message.
- [ ] UI: 400/409/503 responses show a toast with a translated message.
- [ ] UI: when the backend is unreachable, a banner appears and sending is disabled until it recovers.
- [ ] ADR 0002's rollback behaviour is honoured. Update ADR 0002 if the implementation reveals a needed change.
