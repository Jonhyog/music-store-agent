# Backend

Python 3.12 + uv + FastAPI.

```
uv sync
cp .env.example .env
uv run seed            # rebuilds the store tables, keeps Complaints
# uv run seed --reset  # wipes everything, Complaints included
uv run uvicorn music_store.app:app --reload
```

## Eval

An opt-in behavioural eval, outside pytest. It drives a running server over HTTP, plays the challenge, scope, safety and complaint scenarios, and saves a transcript per scenario and model plus a pass/fail summary. Checks look at the tools called and coarse signals, not exact wording.

```
uv run uvicorn music_store.app:app            # in one terminal
uv run python -m evals                        # every available model
uv run python -m evals --model qwen3:4b       # only one model
uv run python -m evals --scenario off-topic   # only some scenarios (repeatable)
```

Transcripts go to `evals/transcripts/<timestamp>/` (git-ignored); `--output` changes the folder. The exit code is 1 when any scenario fails. The complaint scenario files a real Complaint, so point it at a throwaway database. Curated runs live in `docs/examples`.
