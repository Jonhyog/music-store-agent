import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from music_store.settings import Settings


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(request.app.state.settings.database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


Db = Annotated[sqlite3.Connection, Depends(get_db)]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Music Store Assistant")
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/customers")
    def list_customers(
        db: Db,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    ) -> dict:
        total = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        rows = db.execute(
            """
            SELECT c.customer_id, c.name, c.phone, c.email, c.city,
                   COUNT(o.order_id) AS order_count
            FROM customers c
            LEFT JOIN orders o ON o.customer_id = c.customer_id
            GROUP BY c.customer_id
            ORDER BY c.customer_id
            LIMIT ? OFFSET ?
            """,
            (page_size, (page - 1) * page_size),
        ).fetchall()
        return {"customers": [dict(r) for r in rows], "page": page, "total": total}

    return app


app = create_app()
