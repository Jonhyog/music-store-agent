"""Behavioural checks on one `Reply`. Each returns a failure message, or None when it passes.

They look at which tools were called and at coarse signals in the text, never at exact wording.
"""

from collections.abc import Callable
from functools import wraps

from evals.transcript import Reply

Check = Callable[[Reply], str | None]


def _unless_errored(make: Callable[..., Check]) -> Callable[..., Check]:
    @wraps(make)
    def wrapper(*args, **kwargs) -> Check:
        check = make(*args, **kwargs)

        def guarded(reply: Reply) -> str | None:
            if reply.error:
                return f"the stream ended with an error: {reply.error}"
            return check(reply)

        return guarded

    return wrapper


@_unless_errored
def calls_tool(name: str) -> Check:
    return lambda reply: None if name in reply.tool_names else f"expected a call to {name}"


@_unless_errored
def does_not_call_tool(name: str) -> Check:
    return lambda reply: f"must not call {name}" if name in reply.tool_names else None


@_unless_errored
def uses_no_tools() -> Check:
    def check(reply: Reply) -> str | None:
        if reply.tool_names:
            return f"expected no tools, got {', '.join(reply.tool_names)}"
        return None

    return check


@_unless_errored
def contains_any(*fragments: str) -> Check:
    def check(reply: Reply) -> str | None:
        text = reply.text.lower()
        if any(f.lower() in text for f in fragments):
            return None
        return f"expected one of: {', '.join(fragments)}"

    return check


@_unless_errored
def does_not_contain(*fragments: str) -> Check:
    def check(reply: Reply) -> str | None:
        text = reply.text.lower()
        leaked = [f for f in fragments if f.lower() in text]
        return f"must not mention: {', '.join(leaked)}" if leaked else None

    return check


@_unless_errored
def asks_confirmation() -> Check:
    return lambda reply: None if "?" in reply.text else "expected a question asking to confirm"
