from datetime import date

from pydantic import BaseModel


class OrderItemModel(BaseModel):
    product_name: str
    quantity: int


class OrderModel(BaseModel):
    """An Order as the Assistant sees it: Order facts plus its Items with Product names."""

    order_id: int
    order_date: date | None
    status: str | None
    total_brl: float | None
    payment_method: str | None
    tracking_code: str | None
    estimated_delivery: date | None
    notes: str | None
    items: list[OrderItemModel]
