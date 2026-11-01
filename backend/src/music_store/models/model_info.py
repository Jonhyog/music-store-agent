from pydantic import BaseModel


class ModelInfoModel(BaseModel):
    id: str
    provider: str
    label: str
    available: bool
    default: bool


class ModelsResponseModel(BaseModel):
    models: list[ModelInfoModel]
