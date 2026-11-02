"""Plays scenarios against the running server and checks each reply."""

import uuid
from dataclasses import dataclass, field

import httpx

from evals.checks import Check
from evals.transcript import Reply, parse_stream


class EvalError(Exception):
    """A problem with how the eval was invoked or set up, reported without a traceback."""


@dataclass
class Step:
    """One message from the Customer or Visitor and the checks its reply must pass."""

    message: str
    checks: list[Check] = field(default_factory=list)


@dataclass
class Scenario:
    id: str
    title: str
    customer_id: int | None
    steps: list[Step]


@dataclass
class ScenarioResult:
    scenario: Scenario
    model_id: str
    replies: list[Reply]
    failures: list[list[str]]

    @property
    def passed(self) -> bool:
        return len(self.failures) == len(self.scenario.steps) and not any(self.failures)


def select_models(models: list[dict], requested: str | None) -> list[str]:
    """The model ids to run: the requested one, or every available model."""
    if requested is None:
        return [m["id"] for m in models if m["available"]]
    match = next((m for m in models if m["id"] == requested), None)
    if match is None:
        known = ", ".join(m["id"] for m in models)
        raise EvalError(f"unknown model {requested!r}. Known models: {known}")
    if not match["available"]:
        raise EvalError(f"model {requested!r} is not available on this server")
    return [requested]


def _send(client: httpx.Client, headers: dict, conversation_id: str, message: str) -> Reply:
    body = {"conversation_id": conversation_id, "message": message}
    with client.stream("POST", "/chat", headers=headers, json=body) as response:
        if response.status_code != 200:
            response.read()
            raise EvalError(f"POST /chat returned {response.status_code}: {response.text[:200]}")
        return parse_stream(response.iter_lines())


def run_scenario(client: httpx.Client, scenario: Scenario, model_id: str) -> ScenarioResult:
    headers = {"x-model": model_id}
    if scenario.customer_id is not None:
        headers["x-customer-id"] = str(scenario.customer_id)
    conversation_id = str(uuid.uuid4())
    replies: list[Reply] = []
    failures: list[list[str]] = []
    try:
        for step in scenario.steps:
            try:
                reply = _send(client, headers, conversation_id, step.message)
            except (EvalError, httpx.HTTPError) as exc:
                failures.append([str(exc)])
                break
            replies.append(reply)
            failures.append([msg for check in step.checks if (msg := check(reply))])
    finally:
        client.delete(f"/chat/{conversation_id}")
    return ScenarioResult(scenario, model_id, replies, failures)
