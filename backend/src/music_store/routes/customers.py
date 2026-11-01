from typing import Annotated

from fastapi import APIRouter, Query

from music_store.db import Db

router = APIRouter()


@router.get("/customers")
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
