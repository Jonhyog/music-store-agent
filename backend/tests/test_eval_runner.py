import json

import httpx
import pytest
from evals.checks import calls_tool, uses_no_tools
from evals.runner import EvalError, Scenario, Step, run_scenario, select_models

MODELS = [
    {"id": "qwen3:4b", "available": True},
    {"id": "qwen3:8b", "available": False},
    {"id": "gpt-5.6-luna", "available": True},
]


def test_without_a_flag_every_available_model_runs():
    assert select_models(MODELS, None) == ["qwen3:4b", "gpt-5.6-luna"]


def test_a_flag_narrows_the_run_to_that_model():
    assert select_models(MODELS, "gpt-5.6-luna") == ["gpt-5.6-luna"]


def test_a_flag_naming_an_unavailable_or_unknown_model_is_an_error():
    with pytest.raises(EvalError, match="not available"):
        select_models(MODELS, "qwen3:8b")
    with pytest.raises(EvalError, match="unknown"):
        select_models(MODELS, "nope")


def _sse(*events):
    return "".join(f"data: {json.dumps(e)}\n\n" for e in events) + "data: [DONE]\n\n"


def _server(seen):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE":
            seen.append(("DELETE", request.url.path))
            return httpx.Response(204)
        seen.append(
            (
                request.headers.get("x-model"),
                request.headers.get("x-customer-id"),
                json.loads(request.content),
            )
        )
        body = _sse(
            {
                "type": "tool-input-available",
                "toolCallId": "a",
                "toolName": "get_product",
                "input": {},
            },
            {"type": "text-delta", "id": "t", "delta": "pronto"},
        )
        return httpx.Response(200, text=body)

    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test")


def test_run_scenario_sends_identity_and_model_headers_one_conversation_and_cleans_up():
    seen = []
    scenario = Scenario(
        id="s",
        title="S",
        customer_id=3,
        steps=[Step("um", [calls_tool("get_product")]), Step("dois", [uses_no_tools()])],
    )

    result = run_scenario(_server(seen), scenario, "qwen3:4b")

    posts = [s for s in seen if s[0] != "DELETE"]
    assert [(p[0], p[1]) for p in posts] == [("qwen3:4b", "3")] * 2
    assert posts[0][2]["conversation_id"] == posts[1][2]["conversation_id"]
    assert [p[2]["message"] for p in posts] == ["um", "dois"]
    assert seen[-1][0] == "DELETE"
    assert [r.text for r in result.replies] == ["pronto", "pronto"]
    assert result.failures == [[], ["expected no tools, got get_product"]]
    assert not result.passed


def test_a_visitor_sends_no_customer_header():
    seen = []
    scenario = Scenario(id="s", title="S", customer_id=None, steps=[Step("oi", [])])

    assert run_scenario(_server(seen), scenario, "qwen3:4b").passed
    assert seen[0][1] is None


def test_a_rejected_request_is_a_failure_not_a_crash():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(204 if r.method == "DELETE" else 503)
        ),
        base_url="http://test",
    )
    scenario = Scenario(id="s", title="S", customer_id=None, steps=[Step("oi", [])])

    result = run_scenario(client, scenario, "qwen3:4b")

    assert not result.passed
    assert "503" in result.failures[0][0]


def test_every_step_is_also_held_to_the_complete_answer_check():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(
            200, text=_sse({"type": "text-delta", "id": "t", "delta": "ok \\boxed{ok}"})
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test")
    scenario = Scenario(id="s", title="S", customer_id=None, steps=[Step("oi", [])])

    result = run_scenario(client, scenario, "qwen3:4b")

    assert not result.passed
    assert "boxed" in result.failures[0][0]
