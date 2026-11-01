from pydantic import BaseModel


class PaginatedResponseBaseModel(BaseModel):
    """Common envelope fields for paginated endpoints. Subclasses add their items list."""

    page: int
    total: int
