from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from anyio import to_thread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from music_store.assistant.conversations import Conversations
from music_store.assistant.policy import PolicyIndexes
from music_store.errors import DomainError
from music_store.middleware.customer import CustomerMiddleware
from music_store.middleware.errors import error_response
from music_store.middleware.model import ModelMiddleware
from music_store.providers import ProviderRegistry
from music_store.routes import chat, customers, models
from music_store.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Unavailable providers only warn: the server must start without Ollama or an API key.
    await to_thread.run_sync(app.state.registry.warn_unavailable)
    yield


async def _domain_error_handler(request: Request, error: Exception):
    return error_response(error)


def create_app(
    settings: Settings | None = None, registry: ProviderRegistry | None = None
) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Music Store Assistant", lifespan=lifespan)
    app.state.settings = settings
    app.state.registry = registry or ProviderRegistry(settings)
    app.state.conversations = Conversations(settings.conversation_idle_timeout_seconds)
    app.state.policy_indexes = PolicyIndexes(
        app.state.registry, settings.data_dir / "store-policies.pdf"
    )
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
    app.add_exception_handler(DomainError, _domain_error_handler)
    app.include_router(chat.router)
    app.include_router(customers.router)
    app.include_router(models.router)
    return app


app = create_app()
