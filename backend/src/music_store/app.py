from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from anyio import to_thread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from music_store.middleware.customer import CustomerMiddleware
from music_store.middleware.model import ModelMiddleware
from music_store.providers import ProviderRegistry
from music_store.routes import customers
from music_store.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Unavailable providers only warn: the server must start without Ollama or an API key.
    await to_thread.run_sync(app.state.registry.warn_unavailable)
    yield


def create_app(
    settings: Settings | None = None, registry: ProviderRegistry | None = None
) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Music Store Assistant", lifespan=lifespan)
    app.state.settings = settings
    app.state.registry = registry or ProviderRegistry(settings)
    # Last added runs first, so the order is CORS, customer, model. CORS wraps the rest so
    # error responses still carry CORS headers.
    app.add_middleware(ModelMiddleware)
    app.add_middleware(CustomerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(customers.router)
    return app


app = create_app()
