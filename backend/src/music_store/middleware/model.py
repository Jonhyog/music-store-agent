from typing import Annotated

from anyio import to_thread
from fastapi import Depends, Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from music_store.providers import ModelSpec

MODEL_HEADER = b"x-model"

# Only these paths call a model, so only they need it to be available. Everything else
# (/customers, /models, ...) must keep working while a provider is down.
MODEL_PATHS = frozenset({"/chat"})


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

        registry = scope["app"].state.registry
        raw = dict(scope["headers"]).get(MODEL_HEADER)
        model_id = raw.decode("latin-1").strip() if raw is not None else registry.default_id
        spec = registry.get_spec(model_id)
        if spec is None:
            await self._reject(scope, receive, send, 400, "Unknown model.")
            return
        if scope["path"] in MODEL_PATHS and not await to_thread.run_sync(
            registry.is_available, spec
        ):
            await self._reject(scope, receive, send, 503, f"Model {spec.id} is unavailable.")
            return

        scope.setdefault("state", {})["model"] = spec
        await self.app(scope, receive, send)

    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send, status: int, detail: str):
        await JSONResponse({"detail": detail}, status_code=status)(scope, receive, send)


def get_current_model(request: Request) -> ModelSpec:
    return request.state.model


CurrentModel = Annotated[ModelSpec, Depends(get_current_model)]
