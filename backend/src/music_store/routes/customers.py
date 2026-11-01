from typing import Annotated

from fastapi import APIRouter, Query

from music_store.db import Db
from music_store.models.customer import CustomersResponseModel, CustomerWithOrderCountModel
from music_store.utils import pagination_params

router = APIRouter()

COUNT_CUSTOMERS_QUERY = "SELECT COUNT(*) FROM customers"

LIST_CUSTOMERS_QUERY = """
    SELECT c.customer_id, c.name, c.phone, c.email, c.city,
           COUNT(o.order_id) AS order_count
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    ORDER BY c.customer_id
    LIMIT ? OFFSET ?
"""


@router.get("/customers")
def list_customers(
    db: Db,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> CustomersResponseModel:
    total = db.execute(COUNT_CUSTOMERS_QUERY).fetchone()[0]
    rows = db.execute(
        LIST_CUSTOMERS_QUERY,
        pagination_params(page, page_size),
    ).fetchall()
    return CustomersResponseModel(
        customers=[CustomerWithOrderCountModel(**r) for r in rows], page=page, total=total
    )
