# Backend

Python 3.12 + uv + FastAPI.

```
uv sync
cp .env.example .env
uv run seed
uv run uvicorn music_store.app:app --reload
```
