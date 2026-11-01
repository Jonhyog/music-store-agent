from pydantic import BaseModel

from music_store.models.pagination import PaginatedResponseBaseModel


class CustomerModel(BaseModel):
    customer_id: int
    name: str
    phone: str | None
    email: str | None
    city: str | None


class CustomerWithOrderCountModel(CustomerModel):
    order_count: int


class CustomersResponseModel(PaginatedResponseBaseModel):
    customers: list[CustomerWithOrderCountModel]
