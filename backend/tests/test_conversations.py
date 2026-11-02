from music_store.assistant.conversations import Conversations
import pytest

from music_store.errors import ConversationBusyError, ConversationIdentityMismatchError


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _conversations(clock: Clock) -> Conversations:
    return Conversations(idle_timeout_seconds=3600, clock=clock)


def test_an_idle_conversation_is_evicted_and_its_identity_binding_freed():
    clock = Clock()
    conversations = _conversations(clock)
    conversations.begin_turn("a", 1).release()

    clock.now += 3601
    conversations.begin_turn("b", None).release()  # any later activity sweeps idle ones

    conversations.begin_turn("a", 2)  # "a" is gone, so a new identity may bind


def test_a_recently_used_conversation_is_kept():
    clock = Clock()
    conversations = _conversations(clock)
    conversations.begin_turn("a", 1).release()

    clock.now += 3000
    conversations.begin_turn("a", 1).release()  # activity renews it
    clock.now += 3000
    conversations.begin_turn("b", None).release()

    with pytest.raises(ConversationIdentityMismatchError):
        conversations.begin_turn("a", 2)


def test_a_conversation_with_a_turn_in_progress_is_never_evicted():
    clock = Clock()
    conversations = _conversations(clock)
    conversations.begin_turn("a", 1)  # still streaming

    clock.now += 7200
    conversations.begin_turn("b", None).release()

    with pytest.raises(ConversationBusyError):
        conversations.begin_turn("a", 1)
