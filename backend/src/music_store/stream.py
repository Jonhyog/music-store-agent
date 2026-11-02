"""Stream adapter: LangChain agent output -> Vercel AI SDK UI message stream over SSE."""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, ToolMessage

logger = logging.getLogger(__name__)

STREAM_HEADERS = {
    "x-vercel-ai-ui-message-stream": "v1",
    "cache-control": "no-cache",
    "x-accel-buffering": "no",
}
STREAM_ERROR_TEXT = "Something went wrong while answering."
DONE = "data: [DONE]\n\n"


def sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def _tool_output(message: ToolMessage) -> Any:
    content = message.content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except ValueError:
            return content
    return content


class _Adapter:
    def __init__(self) -> None:
        self._text_id: str | None = None
        self._text_parts = 0
        self._streamed_ids: set[str | None] = set()

    def start(self) -> list[dict[str, Any]]:
        return [{"type": "start", "messageId": str(uuid.uuid4())}]

    def message(self, message: BaseMessage, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle a `messages` stream item: model text, as chunks or one whole message."""
        if metadata.get("langgraph_node") != "model" or not isinstance(message, AIMessage):
            return []
        if isinstance(message, AIMessageChunk):
            self._streamed_ids.add(message.id)
        elif message.id in self._streamed_ids:
            return []
        text = _text(message)
        if not text:
            return []
        events = []
        if self._text_id is None:
            self._text_parts += 1
            self._text_id = f"text-{self._text_parts}"
            events.append({"type": "text-start", "id": self._text_id})
        events.append({"type": "text-delta", "id": self._text_id, "delta": text})
        return events

    def update(self, update: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle an `updates` stream item: a finished model step or finished tool calls."""
        events: list[dict[str, Any]] = []
        for node, payload in update.items():
            for message in (payload or {}).get("messages", []):
                if node == "model" and isinstance(message, AIMessage):
                    events += self.close_text()
                    events += [
                        {
                            "type": "tool-input-available",
                            "toolCallId": call["id"],
                            "toolName": call["name"],
                            "input": call["args"],
                        }
                        for call in message.tool_calls
                    ]
                elif node == "tools" and isinstance(message, ToolMessage):
                    events.append(
                        {
                            "type": "tool-output-available",
                            "toolCallId": message.tool_call_id,
                            "output": _tool_output(message),
                        }
                    )
        return events

    def close_text(self) -> list[dict[str, Any]]:
        if self._text_id is None:
            return []
        event = {"type": "text-end", "id": self._text_id}
        self._text_id = None
        return [event]


async def ui_message_stream(raw: AsyncIterator[tuple[str, Any]]) -> AsyncIterator[str]:
    """Turn `(mode, data)` items of `agent.astream(stream_mode=["messages", "updates"])` into SSE.

    A failure mid-stream becomes an `error` event instead of an exception.
    """
    adapter = _Adapter()
    for event in adapter.start():
        yield sse(event)
    try:
        async for mode, data in raw:
            if mode == "messages":
                events = adapter.message(*data)
            elif mode == "updates":
                events = adapter.update(data)
            else:
                events = []
            for event in events:
                yield sse(event)
    except Exception:
        logger.exception("Chat stream failed")
        for event in adapter.close_text():
            yield sse(event)
        yield sse({"type": "error", "errorText": STREAM_ERROR_TEXT})
        yield DONE
        return
    for event in adapter.close_text():
        yield sse(event)
    yield sse({"type": "finish"})
    yield DONE
