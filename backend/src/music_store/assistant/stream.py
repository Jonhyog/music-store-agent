"""Stream adapter: LangChain agent output -> Vercel AI SDK UI message stream over SSE."""

import json
import logging
import uuid
from collections.abc import AsyncIterator, Callable
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

Event = dict[str, Any]


def sse(event: Event) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _text_of(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def _result_of(message: ToolMessage) -> Any:
    """The tool's result as structured data when it is JSON, else as the raw content."""
    content = message.content
    if not isinstance(content, str):
        return content
    try:
        return json.loads(content)
    except ValueError:
        return content


class StreamAdapter:
    """Translates `agent.astream(stream_mode=["messages", "updates"])` items into UI events.

    - `messages` items carry the model's text (as chunks, or as one whole message when the
      model does not stream). They open and fill a text part.
    - `updates` items report finished steps: a model step closes the text part and announces its
      tool calls, a tools step delivers the tool results.
    """

    def __init__(self) -> None:
        self._open_text_id: str | None = None
        self._text_parts = 0
        self._chunked_message_ids: set[str] = set()
        self._by_mode: dict[str, Callable[[Any], list[Event]]] = {
            "messages": self._on_messages_item,
            "updates": self._on_updates_item,
        }
        self._by_node: dict[str, Callable[[BaseMessage], list[Event]]] = {
            "model": self._on_model_step,
            "tools": self._on_tools_step,
        }

    def start(self) -> list[Event]:
        return [{"type": "start", "messageId": str(uuid.uuid4())}]

    def translate(self, mode: str, data: Any) -> list[Event]:
        handler = self._by_mode.get(mode)
        return handler(data) if handler else []

    def finish(self) -> list[Event]:
        return [*self.close_text(), {"type": "finish"}]

    def fail(self) -> list[Event]:
        return [*self.close_text(), {"type": "error", "errorText": STREAM_ERROR_TEXT}]

    def close_text(self) -> list[Event]:
        if self._open_text_id is None:
            return []
        event = {"type": "text-end", "id": self._open_text_id}
        self._open_text_id = None
        return [event]

    # --- `messages` items -------------------------------------------------------------------

    def _on_messages_item(self, item: tuple[BaseMessage, dict[str, Any]]) -> list[Event]:
        message, metadata = item
        if not self._is_model_output(message, metadata):
            return []
        if isinstance(message, AIMessageChunk):
            self._remember_chunked(message)
        elif self._was_already_chunked(message):
            return []
        text = _text_of(message)
        if not text:
            return []
        return [
            *self._open_text_part(),
            {"type": "text-delta", "id": self._open_text_id, "delta": text},
        ]

    @staticmethod
    def _is_model_output(message: BaseMessage, metadata: dict[str, Any]) -> bool:
        return metadata.get("langgraph_node") == "model" and isinstance(message, AIMessage)

    def _remember_chunked(self, chunk: AIMessageChunk) -> None:
        if chunk.id is not None:
            self._chunked_message_ids.add(chunk.id)

    def _was_already_chunked(self, message: AIMessage) -> bool:
        """True for the whole-message echo of a message whose chunks were already streamed."""
        return message.id in self._chunked_message_ids

    def _open_text_part(self) -> list[Event]:
        if self._open_text_id is not None:
            return []
        self._text_parts += 1
        self._open_text_id = f"text-{self._text_parts}"
        return [{"type": "text-start", "id": self._open_text_id}]

    # --- `updates` items --------------------------------------------------------------------

    def _on_updates_item(self, update: dict[str, Any]) -> list[Event]:
        events: list[Event] = []
        for node, payload in update.items():
            handler = self._by_node.get(node)
            if handler is None:
                continue
            for message in (payload or {}).get("messages", []):
                events += handler(message)
        return events

    def _on_model_step(self, message: BaseMessage) -> list[Event]:
        if not isinstance(message, AIMessage):
            return []
        return [
            *self.close_text(),
            *(
                {
                    "type": "tool-input-available",
                    "toolCallId": call["id"],
                    "toolName": call["name"],
                    "input": call["args"],
                }
                for call in message.tool_calls
            ),
        ]

    def _on_tools_step(self, message: BaseMessage) -> list[Event]:
        if not isinstance(message, ToolMessage):
            return []
        return [
            {
                "type": "tool-output-available",
                "toolCallId": message.tool_call_id,
                "output": _result_of(message),
            }
        ]


async def ui_message_stream(raw: AsyncIterator[tuple[str, Any]]) -> AsyncIterator[str]:
    """Turn the agent's `(mode, data)` stream into SSE lines.

    A failure mid-stream becomes an `error` event instead of an exception.
    """
    adapter = StreamAdapter()
    for event in adapter.start():
        yield sse(event)
    try:
        async for mode, data in raw:
            for event in adapter.translate(mode, data):
                yield sse(event)
    except Exception:
        logger.exception("Chat stream failed")
        for event in adapter.fail():
            yield sse(event)
    else:
        for event in adapter.finish():
            yield sse(event)
    yield DONE
