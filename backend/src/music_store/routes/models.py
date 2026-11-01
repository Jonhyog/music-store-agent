from fastapi import APIRouter, Request

from music_store.models.model_info import ModelInfoModel, ModelsResponseModel

router = APIRouter()


@router.get("/models")
def list_models(request: Request) -> ModelsResponseModel:
    registry = request.app.state.registry
    return ModelsResponseModel(
        models=[
            ModelInfoModel(
                id=spec.id,
                provider=spec.provider,
                label=spec.label,
                available=registry.is_available(spec),
                default=spec.id == registry.default_id,
            )
            for spec in registry.specs
        ]
    )
