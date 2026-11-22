from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path(value: str, fallback: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@dataclass(frozen=True)
class Settings:
    app_name: str = "ReLoop AI API"
    api_version: str = "1.0.0"
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", f"sqlite:///{(PROJECT_ROOT / 'reloop.db').as_posix()}"
        )
    )
    secret_key: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "reloop-dev-secret-change-me")
    )
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    )
    cors_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:8501,http://127.0.0.1:8501,http://localhost:3000",
            ).split(",")
            if origin.strip()
        ]
    )
    upload_dir: Path = field(
        default_factory=lambda: _resolve_path(
            os.getenv("UPLOAD_DIR", "backend/uploads"), PROJECT_ROOT / "backend" / "uploads"
        )
    )
    max_upload_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "5"))
    )
    seed_demo_data: bool = field(
        default_factory=lambda: _as_bool(os.getenv("SEED_DEMO_DATA"), True)
    )
    demo_email: str = field(
        default_factory=lambda: os.getenv("DEMO_EMAIL", "demo@reloop.example")
    )
    demo_password: str = field(
        default_factory=lambda: os.getenv("DEMO_PASSWORD", "reloop123")
    )
    demo_name: str = field(
        default_factory=lambda: os.getenv("DEMO_NAME", "Aarav Mehta")
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
