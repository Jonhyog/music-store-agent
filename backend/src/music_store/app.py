from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from music_store.routes import customers
from music_store.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Music Store Assistant")
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(customers.router)
    return app


app = create_app()
