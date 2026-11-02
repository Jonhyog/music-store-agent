"""Server-held Conversations: identity binding, one turn at a time, in-memory history (ADR 0002)."""

from dataclasses import dataclass

from langgraph.checkpoint.memory import InMemorySaver

from music_store.errors import ConversationBusyError, ConversationIdentityMismatchError

# The customer id, or None for a Visitor.
Identity = int | None


@dataclass
class _Conversation:
    identity: Identity
    busy: bool = False


class Turn:
    """Holds a Conversation's turn lock until `release` is called (safe to call twice)."""

    def __init__(self, conversation: _Conversation) -> None:
        self._conversation = conversation
        self._released = False

    def release(self) -> None:
        if not self._released:
            self._released = True
            self._conversation.busy = False


class Conversations:
    def __init__(self) -> None:
        self.checkpointer = InMemorySaver()
        self._conversations: dict[str, _Conversation] = {}

    def begin_turn(self, conversation_id: str, identity: Identity) -> Turn:
        """Bind the Conversation to `identity` on first use and take its turn lock.

        Raises a DomainError for a different identity or a turn already in progress. This is
        synchronous on purpose: with no await in between, check and lock can't interleave.
        """
        conversation = self._conversations.setdefault(conversation_id, _Conversation(identity))
        if conversation.identity != identity:
            raise ConversationIdentityMismatchError
        if conversation.busy:
            raise ConversationBusyError
        conversation.busy = True
        return Turn(conversation)

    def delete(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)
        self.checkpointer.delete_thread(conversation_id)
