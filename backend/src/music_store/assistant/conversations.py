"""Server-held Conversations: identity binding, one turn at a time, in-memory history (ADR 0002)."""

from dataclasses import dataclass

from langchain_core.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph.state import CompiledStateGraph

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


class TurnRollback:
    """Remembers a thread's messages when a turn begins and removes any added since.

    Called when the turn fails or is stopped, so stored history never holds a tool request
    without its result (ADR 0002). Synchronous on purpose: it must also run while the request
    is being cancelled, where awaiting is unreliable.
    """

    def __init__(self, agent: CompiledStateGraph, thread_id: str) -> None:
        self._agent = agent
        self._config = {"configurable": {"thread_id": thread_id}}
        self._before = self._message_ids()

    def _message_ids(self) -> list[str]:
        # Read the checkpoint itself: `get_state` also shows writes of a step that was cut short,
        # which `update_state` cannot remove because they were never checkpointed.
        saved = self._agent.checkpointer.get_tuple(self._config)
        if saved is None:
            return []
        return [m.id for m in saved.checkpoint["channel_values"].get("messages", [])]

    def __call__(self) -> None:
        added = [i for i in self._message_ids() if i not in set(self._before)]
        if added:
            # `as_node=START` skips the model/tools conditional edges, which would re-apply
            # the removals to messages that are already gone.
            self._agent.update_state(
                self._config,
                {"messages": [RemoveMessage(id=i) for i in added]},
                as_node=START,
            )
