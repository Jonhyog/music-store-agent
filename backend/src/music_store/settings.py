from datetime import date
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_path: Path = Path("music_store.db")
    data_dir: Path = REPO_ROOT / "data"
    cors_origins: list[str] = ["http://localhost:5173"]
    reference_date: date = date(2026, 3, 25)
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: SecretStr | None = None
    default_model: str = "qwen3:4b"
