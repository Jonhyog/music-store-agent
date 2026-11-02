"""`uv run python -m evals`: play the scenarios against the running server.

Runs every available model by default; `--model ID` narrows the run to one.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import httpx

from evals.report import render_summary, render_transcript
from evals.runner import EvalError, run_scenario, select_models
from evals.scenarios import SCENARIOS

DEFAULT_OUTPUT = Path(__file__).parent / "transcripts"
REQUEST_TIMEOUT_SECONDS = 300.0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m evals", description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000", help="the running server")
    parser.add_argument("--model", help="run only this model id (default: every available model)")
    parser.add_argument(
        "--scenario",
        action="append",
        metavar="ID",
        help="run only this scenario id (repeatable)",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="transcripts folder")
    return parser


def _scenarios(ids: list[str] | None):
    if not ids:
        return SCENARIOS
    unknown = set(ids) - {s.id for s in SCENARIOS}
    if unknown:
        known = ", ".join(s.id for s in SCENARIOS)
        raise EvalError(f"unknown scenario {', '.join(sorted(unknown))}. Known scenarios: {known}")
    return [s for s in SCENARIOS if s.id in ids]


def _run(args: argparse.Namespace) -> bool:
    scenarios = _scenarios(args.scenario)
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS, connect=5.0)
    with httpx.Client(base_url=args.base_url, timeout=timeout) as client:
        try:
            models = client.get("/models").raise_for_status().json()["models"]
        except httpx.HTTPError as exc:
            raise EvalError(f"cannot reach the server at {args.base_url}: {exc}") from exc
        model_ids = select_models(models, args.model)
        if not model_ids:
            raise EvalError("no model is available on this server")
        folder = args.output / datetime.now().strftime("%Y%m%d-%H%M%S")
        results = []
        for model_id in model_ids:
            for scenario in scenarios:
                result = run_scenario(client, scenario, model_id)
                results.append(result)
                target = folder / model_id.replace(":", "-") / f"{scenario.id}.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(render_transcript(result), encoding="utf-8")
                print(
                    f"{'PASS' if result.passed else 'FAIL'}  {model_id}  {scenario.id}", flush=True
                )
    summary = render_summary(results)
    (folder / "summary.md").write_text(summary + "\n", encoding="utf-8")
    print(f"\n{summary}\n\nTranscripts saved in {folder}")
    return all(r.passed for r in results)


def main() -> int:
    try:
        return 0 if _run(_parser().parse_args()) else 1
    except EvalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
