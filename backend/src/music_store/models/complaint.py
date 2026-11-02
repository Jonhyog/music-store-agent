from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ComplaintCategory = Literal["product_defect", "delivery", "service", "payment", "other"]


class ComplaintModel(BaseModel):
    complaint_id: int
    created_at: datetime
