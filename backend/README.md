# Backend

Python 3.12 + uv + FastAPI.

```
uv sync
cp .env.example .env
uv run seed            # rebuilds the store tables, keeps Complaints
# uv run seed --reset  # wipes everything, Complaints included
uv run uvicorn music_store.app:app --reload
```
