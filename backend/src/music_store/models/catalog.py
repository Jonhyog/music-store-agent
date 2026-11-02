from typing import Any

from pydantic import BaseModel


class AppliedPromotionModel(BaseModel):
    campaign: str | None
    discount_percent: int


class ProductModel(BaseModel):
    """A Product as the Assistant sees it: catalog fields plus prices computed in code."""

    product_id: int
    name: str
    category: str | None
    list_price_brl: float
    stock_quantity: int
    status: str | None
    description: str | None
    specs: dict[str, Any] | None
    promotion: AppliedPromotionModel | None
    promotional_price_brl: float | None
    pix_price_brl: float | None
