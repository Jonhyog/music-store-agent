# Server-held Conversations bound to one Customer

Conversation history lives on the server in a LangGraph in-memory checkpointer keyed by a client-generated Conversation id, rather than being re-sent by the client on every request. Client-held history lets anyone forge prior Assistant turns (e.g. a fake "jailbreak completed" reply, or a made-up price), which primes the model far more strongly than a user message; keeping history server-side removes that attack at the source and also keeps tool results in context. History is deliberately not persisted: it is lost on restart, which is acceptable because Customer questions are sparse and unrelated.

## Consequences

- A Conversation is bound to the Customer (or Visitor) of its first message; a request for that Conversation with a different identity is rejected (409), so the frontend starts a new Conversation when the selected Customer changes.
- Only the most recent messages are sent to the model and idle Conversations are evicted, bounding memory.
- A turn that fails or is stopped is rolled back automatically on the server, so stored history never contains a tool request without its result; "try again" simply resends the message. Text the Customer already saw from a stopped turn is not part of the Assistant's memory. Rollback removes the messages added to the last saved checkpoint since the turn began; the history window sent to the model always starts on a Customer message, so a tool result is never sent without its request. Idle eviction runs when any Conversation begins a turn, not on a timer.
- Switching models mid-Conversation keeps the history; only the model changes.
- Page reload starts a new Conversation; there is no history-fetch endpoint.
