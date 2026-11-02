from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from music_store.models.pagination import PaginatedResponseBaseModel

ComplaintCategory = Literal["product_defect", "delivery", "service", "payment", "other"]


class ComplaintModel(BaseModel):
    complaint_id: int
    created_at: datetime


class ComplaintListItemModel(BaseModel):
    complaint_id: int
    customer_id: int
    customer_name: str
    order_id: int | None
    category: ComplaintCategory
    description: str
    conversation_id: str
    created_at: datetime


class ComplaintsResponseModel(PaginatedResponseBaseModel):
    complaints: list[ComplaintListItemModel]
