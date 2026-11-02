import json
from datetime import date

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from fakes import FakeChatModel
from music_store.assistant.agent import build_agent
from music_store.assistant.context import AgentContext
from music_store.assistant.stream import DONE, ui_message_stream

pytestmark = pytest.mark.anyio


async def _raw(items):
    for item in items:
        if isinstance(item, Exception):
            raise item
        yield item


async def _collect(items) -> list[dict | str]:
    out = []
    async for line in ui_message_stream(_raw(items)):
        payload = line.removeprefix("data: ").strip()
        out.append(payload if payload == "[DONE]" else json.loads(payload))
    return out


def _model(chunk):
    return ("messages", (chunk, {"langgraph_node": "model"}))


async def test_streamed_chunks_become_one_text_part():
    events = await _collect(
        [
            _model(AIMessageChunk(content="Olá", id="m1")),
            _model(AIMessageChunk(content=" mundo", id="m1")),
            ("updates", {"model": {"messages": [AIMessage(content="Olá mundo", id="m1")]}}),
        ]
    )
    assert [e["type"] for e in events[:-1]] == [
        "start", "text-start", "text-delta", "text-delta", "text-end", "finish",
    ]  # fmt: skip
    assert [e["delta"] for e in events[:-1] if e["type"] == "text-delta"] == ["Olá", " mundo"]
    assert events[-1] == "[DONE]"


async def test_whole_message_without_chunks_is_not_duplicated():
    events = await _collect(
        [
            _model(AIMessage(content="Oi", id="m1")),
            ("updates", {"model": {"messages": [AIMessage(content="Oi", id="m1")]}}),
        ]
    )
    assert [e["delta"] for e in events if e != "[DONE]" and e["type"] == "text-delta"] == ["Oi"]


async def test_tool_call_and_result_events_carry_name_args_and_full_result():
    call = AIMessage(
        content="", tool_calls=[{"name": "list_categories", "args": {"a": 1}, "id": "c1"}]
    )
    result = ToolMessage(content=json.dumps([{"name": "Guitarras"}]), tool_call_id="c1")
    events = await _collect(
        [
            ("updates", {"model": {"messages": [call]}}),
            ("updates", {"tools": {"messages": [result]}}),
        ]
    )
    assert events[1] == {
        "type": "tool-input-available",
        "toolCallId": "c1",
        "toolName": "list_categories",
        "input": {"a": 1},
    }
    assert events[2] == {
        "type": "tool-output-available",
        "toolCallId": "c1",
        "output": [{"name": "Guitarras"}],
    }


async def test_failure_becomes_error_event_then_done():
    events = await _collect([_model(AIMessageChunk(content="Ol", id="m1")), RuntimeError("boom")])
    assert [e["type"] for e in events[:-1]] == [
        "start", "text-start", "text-delta", "text-end", "error",
    ]  # fmt: skip
    assert "boom" not in json.dumps(events)
    assert events[-1] == "[DONE]"


async def test_real_agent_stream_emits_tool_events_then_text(settings):
    script = [
        AIMessage(content="", tool_calls=[{"name": "list_categories", "args": {}, "id": "c1"}]),
        AIMessage(content="Temos 9 categorias."),
    ]
    agent = build_agent(FakeChatModel(script=script), InMemorySaver())
    context = AgentContext(None, date(2026, 3, 25), settings.database_path)
    raw = agent.astream(
        {"messages": [("user", "categorias?")]},
        config={"configurable": {"thread_id": "t"}},
        context=context,
        stream_mode=["messages", "updates"],
    )
    events = [json.loads(line.removeprefix("data: ")) async for line in _lines(raw)]
    assert [e["type"] for e in events] == [
        "start", "tool-input-available", "tool-output-available",
        "text-start", "text-delta", "text-end", "finish",
    ]  # fmt: skip


async def _lines(raw):
    async for line in ui_message_stream(raw):
        if line != DONE:
            yield line
