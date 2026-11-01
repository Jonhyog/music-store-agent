from typing import Annotated

from anyio import to_thread
from fastapi import Depends, Request
from starlette.types import ASGIApp, Receive, Scope, Send

from music_store.errors import ModelUnavailableError, UnknownModelError
from music_store.middleware.errors import error_response
from music_store.providers import ModelSpec

MODEL_HEADER = b"x-model"

# Only these paths call a model, so only they need it to be available. Everything else
# (/customers, /models, ...) must keep working while a provider is down.
MODEL_PATHS = frozenset({"/chat"})


async def _resolve_model(scope: Scope) -> ModelSpec:
    """Return the allowlisted model named by the header (or the default).

    Raises a DomainError for an unknown model, or an unavailable one on model paths.
    """
    registry = scope["app"].state.registry
    raw = dict(scope["headers"]).get(MODEL_HEADER)
    model_id = raw.decode("latin-1").strip() if raw is not None else registry.default_id
    spec = registry.get_spec(model_id)
    if spec is None:
        raise UnknownModelError
    if scope["path"] in MODEL_PATHS and not await to_thread.run_sync(registry.is_available, spec):
        raise ModelUnavailableError(f"Model {spec.id} is unavailable.")
    return spec


class ModelMiddleware:
    """Resolves `x-model` against the allowlist into `request.state.model`.

    This is the hook for future per-Customer model entitlements.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            spec = await _resolve_model(scope)
        except Exception as error:
            response = error_response(error)
        else:
            scope.setdefault("state", {})["model"] = spec
            await self.app(scope, receive, send)
            return
        await response(scope, receive, send)


def get_current_model(request: Request) -> ModelSpec:
    return request.state.model


CurrentModel = Annotated[ModelSpec, Depends(get_current_model)]
