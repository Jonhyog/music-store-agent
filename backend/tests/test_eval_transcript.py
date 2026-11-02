import json

from evals.transcript import parse_stream


def _sse(*events):
    return [f"data: {json.dumps(e)}" for e in events] + ["data: [DONE]"]


def test_parse_stream_collects_text_and_pairs_tool_calls_with_their_results():
    reply = parse_stream(
        _sse(
            {"type": "start", "messageId": "m"},
            {
                "type": "tool-input-available",
                "toolCallId": "a",
                "toolName": "get_product",
                "input": {"name": "x"},
            },
            {"type": "tool-output-available", "toolCallId": "a", "output": {"price": 1}},
            {"type": "text-start", "id": "t"},
            {"type": "text-delta", "id": "t", "delta": "Olá, "},
            {"type": "text-delta", "id": "t", "delta": "tudo bem?"},
            {"type": "text-end", "id": "t"},
            {"type": "finish"},
        )
    )
    assert reply.text == "Olá, tudo bem?"
    assert [(c.name, c.input, c.output) for c in reply.tool_calls] == [
        ("get_product", {"name": "x"}, {"price": 1})
    ]
    assert reply.error is None
    assert reply.tool_names == ["get_product"]


def test_parse_stream_ignores_reasoning_and_blank_lines_and_keeps_errors():
    reply = parse_stream(
        [
            "",
            *_sse(
                {"type": "reasoning-delta", "id": "r", "delta": "pensando"},
                {"type": "error", "errorText": "boom"},
            ),
        ]
    )
    assert reply.text == ""
    assert reply.error == "boom"
