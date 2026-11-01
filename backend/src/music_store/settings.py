from datetime import date
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_path: Path = Path("music_store.db")
    data_dir: Path = REPO_ROOT / "data"
    cors_origins: list[str] = ["http://localhost:5173"]
    reference_date: date = date(2026, 3, 25)
