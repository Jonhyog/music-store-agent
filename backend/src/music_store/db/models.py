"""Typed rows, one model per table in ``schema.py``. Build them with ``Row.model_validate(row)``."""

import json
from datetime import date
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, field_validator


class RowModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_row(cls, row: Any) -> Self:
        return cls.model_validate(dict(row))


class CategoryRow(RowModel):
    category_id: int
    name: str
    description: str | None


class ProductRow(RowModel):
    product_id: int
    category_id: int | None
    name: str
    price_brl: float
    description: str | None
    stock_quantity: int
    status: str | None
    specs: dict[str, Any] | None
    created_at: date | None

    @field_validator("specs", mode="before")
    @classmethod
    def _parse_specs(cls, value: Any) -> Any:
        return json.loads(value) if isinstance(value, str) else value


class PromotionRow(RowModel):
    promotion_id: int
    product_id: int | None
    discount_percent: int
    description: str | None
    is_active: bool


class CustomerRow(RowModel):
    customer_id: int
    name: str
    phone: str | None
    email: str | None
    city: str | None


class OrderRow(RowModel):
    order_id: int
    customer_id: int | None
    order_date: date | None
    status: str | None
    total_brl: float | None
    payment_method: str | None
    tracking_code: str | None
    estimated_delivery: date | None
    notes: str | None


class OrderItemRow(RowModel):
    order_id: int
    product_id: int
    quantity: int
