"""Reads the chat SSE stream into a `Reply`: the answer text and the tools the Assistant used."""

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    input: Any
    output: Any = None


@dataclass
class Reply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    error: str | None = None

    @property
    def tool_names(self) -> list[str]:
        return [call.name for call in self.tool_calls]


def parse_stream(lines: Iterable[str]) -> Reply:
    reply = Reply()
    pending: dict[str, ToolCall] = {}
    for line in lines:
        if not line.startswith("data:"):
            continue
        payload = line.removeprefix("data:").strip()
        if payload == "[DONE]":
            break
        event = json.loads(payload)
        match event.get("type"):
            case "text-delta":
                reply.text += event["delta"]
            case "tool-input-available":
                call = ToolCall(name=event["toolName"], input=event["input"])
                pending[event["toolCallId"]] = call
                reply.tool_calls.append(call)
            case "tool-output-available":
                if event["toolCallId"] in pending:
                    pending[event["toolCallId"]].output = event["output"]
            case "error":
                reply.error = event["errorText"]
    return reply
