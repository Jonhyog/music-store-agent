"""Read-only Order queries. Every query is scoped to one Customer id, passed by the caller."""

import sqlite3

from music_store.db.models import OrderItemRow, OrderRow
from music_store.models.order import OrderItemModel, OrderModel

ORDERS_QUERY = """
    SELECT * FROM orders
    WHERE customer_id = :customer_id AND (:status IS NULL OR status = :status)
    ORDER BY order_date DESC, order_id DESC
"""

ORDER_QUERY = "SELECT * FROM orders WHERE customer_id = :customer_id AND order_id = :order_id"

ORDER_ITEMS_QUERY = """
    SELECT oi.order_id, oi.product_id, oi.quantity, p.name AS product_name
    FROM order_items oi JOIN products p ON p.product_id = oi.product_id
    WHERE oi.order_id = ?
    ORDER BY oi.product_id
"""


def _with_items(conn: sqlite3.Connection, order: OrderRow) -> OrderModel:
    items = [
        OrderItemModel(
            product_name=row["product_name"], quantity=OrderItemRow.from_row(row).quantity
        )
        for row in conn.execute(ORDER_ITEMS_QUERY, (order.order_id,))
    ]
    return OrderModel(**order.model_dump(exclude={"customer_id"}), items=items)


def list_orders(
    conn: sqlite3.Connection, *, customer_id: int, status: str | None = None
) -> list[OrderModel]:
    """The Customer's Orders, newest first, optionally only those with an Order Status."""
    rows = conn.execute(ORDERS_QUERY, {"customer_id": customer_id, "status": status})
    return [_with_items(conn, OrderRow.from_row(row)) for row in rows.fetchall()]


def get_order(conn: sqlite3.Connection, *, customer_id: int, order_id: int) -> OrderModel | None:
    """One of the Customer's Orders; None when it doesn't exist or belongs to someone else."""
    row = conn.execute(ORDER_QUERY, {"customer_id": customer_id, "order_id": order_id}).fetchone()
    return _with_items(conn, OrderRow.from_row(row)) if row else None
