from typing import Annotated

from fastapi import APIRouter, Query

from music_store.db import Db
from music_store.models.complaint import ComplaintListItemModel, ComplaintsResponseModel
from music_store.utils import pagination_params

router = APIRouter()

# A NULL customer id matches every Customer, so one statement serves filtered and unfiltered.
COUNT_COMPLAINTS_QUERY = """
    SELECT COUNT(*) FROM complaints WHERE :customer_id IS NULL OR customer_id = :customer_id
"""

LIST_COMPLAINTS_QUERY = """
    SELECT k.complaint_id, k.customer_id, c.name AS customer_name, k.order_id, k.category,
           k.description, k.conversation_id, k.created_at
    FROM complaints k
    JOIN customers c ON c.customer_id = k.customer_id
    WHERE :customer_id IS NULL OR k.customer_id = :customer_id
    ORDER BY k.created_at DESC, k.complaint_id DESC
    LIMIT :limit OFFSET :offset
"""


@router.get("/complaints")
def list_complaints(
    db: Db,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    customer_id: Annotated[int | None, Query(alias="customerId")] = None,
) -> ComplaintsResponseModel:
    """Staff view of every Complaint. Deliberately independent of `x-customer-id`."""
    total = db.execute(COUNT_COMPLAINTS_QUERY, {"customer_id": customer_id}).fetchone()[0]
    limit, offset = pagination_params(page, page_size)
    rows = db.execute(
        LIST_COMPLAINTS_QUERY, {"customer_id": customer_id, "limit": limit, "offset": offset}
    ).fetchall()
    return ComplaintsResponseModel(
        complaints=[ComplaintListItemModel(**r) for r in rows], page=page, total=total
    )
