# backend/config.py
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── БД: окремі змінні ─────────────────────────────────────────────────
    DB_HOST:     str = "localhost"
    DB_PORT:     int = 5432
    DB_USER:     str = "postgres"
    DB_PASSWORD: str = "root"
    DB_NAME:     str = "medipredictor"

    # ── БД: або повний URL (необов'язково) ────────────────────────────────
    DATABASE_URL: str = ""

    # ── Безпека ────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev_secret_key_change_in_production_min_32_chars"
    ALGORITHM:  str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ── CORS ───────────────────────────────────────────────────────────────
    FRONTEND_ORIGINS: str = "*"

    # ── Сервер ─────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def db_url(self) -> str:
        """Asyncpg URL з окремих змінних або DATABASE_URL."""
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql"):
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    @property
    def cors_origins(self) -> list[str]:
        raw = self.FRONTEND_ORIGINS.strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


# ── ОБОВ'ЯЗКОВО: ця функція потрібна скрізь ───────────────────────────────
@lru_cache()
def get_settings() -> Settings:
    return Settings()
