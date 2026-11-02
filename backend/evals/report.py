"""Markdown for the saved transcripts and the pass/fail summary."""

import json

from evals.runner import ScenarioResult


def _verdict(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_transcript(result: ScenarioResult) -> str:
    scenario = result.scenario
    who = f"Customer {scenario.customer_id}" if scenario.customer_id else "Visitor"
    lines = [
        f"# {scenario.title}",
        "",
        f"- Scenario: `{scenario.id}`",
        f"- Model: `{result.model_id}`",
        f"- Talking as: {who}",
        f"- Result: **{_verdict(result.passed)}**",
        "",
    ]
    for step, reply, failures in zip(scenario.steps, result.replies, result.failures, strict=False):
        lines += ["## User", "", step.message, ""]
        for call in reply.tool_calls:
            lines += [
                f"> Tool call: `{call.name}`",
                "",
                "```json",
                _json(call.input),
                "```",
                "",
                "Result:",
                "",
                "```json",
                _json(call.output),
                "```",
                "",
            ]
        lines += ["## Assistant", "", reply.text or "_(no text)_", ""]
        lines += [f"- Check failed: {message}" for message in failures]
        lines += [""] if failures else []
    for failures in result.failures[len(result.replies) :]:
        lines += [f"- Request failed: {message}" for message in failures] + [""]
    return "\n".join(lines)


def render_summary(results: list[ScenarioResult]) -> str:
    models = list(dict.fromkeys(r.model_id for r in results))
    by_key = {(r.scenario.id, r.model_id): r for r in results}
    scenario_ids = list(dict.fromkeys(r.scenario.id for r in results))
    lines = [
        "| Scenario | " + " | ".join(models) + " |",
        "|---|" + "---|" * len(models),
    ]
    for scenario_id in scenario_ids:
        cells = [
            _verdict(by_key[scenario_id, m].passed) if (scenario_id, m) in by_key else "-"
            for m in models
        ]
        lines.append(f"| {scenario_id} | " + " | ".join(cells) + " |")
    totals = [
        f"{sum(r.passed for r in results if r.model_id == m)}/"
        f"{sum(1 for r in results if r.model_id == m)}"
        for m in models
    ]
    lines.append("| **Total** | " + " | ".join(totals) + " |")
    return "\n".join(lines)
