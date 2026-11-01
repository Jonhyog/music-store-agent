from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fakes import FakeRegistry
from music_store.app import create_app
from music_store.seed import seed
from music_store.settings import REPO_ROOT, Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    db = tmp_path / "test.db"
    seed(db, REPO_ROOT / "data")
    return Settings(_env_file=None, database_path=db)


@pytest.fixture
def registry(settings: Settings) -> FakeRegistry:
    return FakeRegistry(settings)


@pytest.fixture
def client(settings: Settings, registry: FakeRegistry):
    with TestClient(create_app(settings, registry=registry)) as c:
        yield c
