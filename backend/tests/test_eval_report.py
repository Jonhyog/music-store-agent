from evals.report import render_summary, render_transcript
from evals.runner import Scenario, ScenarioResult, Step
from evals.transcript import Reply, ToolCall


def _result(model="qwen3:4b", failures=None):
    scenario = Scenario(id="s1", title="Title", customer_id=3, steps=[Step("Oi?", [])])
    reply = Reply(
        text="Olá!",
        tool_calls=[ToolCall(name="get_my_order", input={"order_id": 1}, output={"status": "ok"})],
    )
    return ScenarioResult(scenario, model, [reply], failures if failures is not None else [[]])


def test_transcript_shows_the_messages_tools_and_verdict():
    text = render_transcript(_result(failures=[["expected a call to x"]]))
    assert "Oi?" in text and "Olá!" in text
    assert "get_my_order" in text and '"order_id": 1' in text
    assert "FAIL" in text and "expected a call to x" in text


def test_summary_has_a_row_per_scenario_and_a_column_per_model():
    summary = render_summary([_result("a"), _result("b", failures=[["boom"]])])
    assert "| s1 | PASS | FAIL |" in summary
    assert "a" in summary and "b" in summary
    assert "| **Total** | 1/1 | 0/1 |" in summary
