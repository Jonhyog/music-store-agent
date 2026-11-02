"""Filing Complaints. A Complaint is append-only: no status, no edits, no removal."""

import sqlite3
from datetime import UTC, datetime

from music_store.assistant import orders
from music_store.models.complaint import ComplaintCategory, ComplaintModel

INSERT = """
    INSERT INTO complaints (customer_id, order_id, category, description, conversation_id,
                            created_at)
    VALUES (:customer_id, :order_id, :category, :description, :conversation_id, :created_at)
"""


class OrderNotFoundForComplaint(LookupError):
    """The Order doesn't exist or isn't the Customer's own."""


def register_complaint(
    conn: sqlite3.Connection,
    *,
    customer_id: int,
    conversation_id: str,
    category: ComplaintCategory,
    description: str,
    order_id: int | None = None,
) -> ComplaintModel:
    """Record a Complaint for the Customer, stamped with the real wall-clock time."""
    if (
        order_id is not None
        and orders.get_order(conn, customer_id=customer_id, order_id=order_id) is None
    ):
        raise OrderNotFoundForComplaint(order_id)
    created_at = datetime.now(UTC)
    cursor = conn.execute(
        INSERT,
        {
            "customer_id": customer_id,
            "order_id": order_id,
            "category": category,
            "description": description,
            "conversation_id": conversation_id,
            "created_at": created_at.isoformat(),
        },
    )
    conn.commit()
    return ComplaintModel(complaint_id=cursor.lastrowid, created_at=created_at)
