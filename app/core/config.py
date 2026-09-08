"""Configuration settings for FinTech No-LLM Chatbot."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "FinTech No-LLM Knowledge Chatbot"
    API_PREFIX: str = "/api/v1"

    # Database: Supports SQLite (sqlite:///./data/fintech_rag.db) or PostgreSQL / Neon / Supabase
    DATABASE_URL: str = "sqlite:///./data/fintech_rag.db"

    ADMIN_API_KEY: str = "fintech-secret-admin-key-2026"
    SESSION_SECRET: str = "fintech-session-secret-key-32chars"

    ALLOWED_ORIGINS: str = "*"
    MAX_UPLOAD_MB: int = 25
    MAX_QUERY_LENGTH: int = 1000

    ENABLE_SEMANTIC_RETRIEVAL: bool = False
    ENABLE_DEBUG_ROUTES: bool = True

    # Retrieval parameters
    BM25_K1: float = 1.2
    BM25_B: float = 0.75
    RETRIEVAL_TOP_K: int = 30
    FINAL_EVIDENCE_K: int = 4
    MIN_HYBRID_SCORE: float = 0.35
    MIN_SENTENCE_SCORE: float = 0.40

    LOG_LEVEL: str = "INFO"

    # 24/7 Render Uptime / Keep-Alive Configuration
    RENDER_EXTERNAL_URL: str | None = None
    KEEP_ALIVE_URL: str | None = None
    KEEP_ALIVE_INTERVAL_SECONDS: int = 540  # 9 minutes (Render sleeps at 15 mins)

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    INDEXES_DIR: Path = DATA_DIR / "indexes"
    CONFIGS_DIR: Path = BASE_DIR / "configs"

    @property
    def cors_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
