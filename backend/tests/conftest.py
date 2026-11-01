from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from music_store.app import create_app
from music_store.seed import seed
from music_store.settings import REPO_ROOT, Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    db = tmp_path / "test.db"
    seed(db, REPO_ROOT / "data")
    return Settings(_env_file=None, database_path=db)


@pytest.fixture
def client(settings: Settings):
    with TestClient(create_app(settings)) as c:
        yield c
