from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    APP_NAME: str = "automation-engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DRY_RUN: bool = True
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    CID_BASE_URL: str = "http://cid-web:3000"
    CINE_PLATFORM_BASE_URL: str = "http://cine-api:3000"
    WEB_BASE_URL: str = "http://cid-web:3000"

    CID_INTERNAL_TOKEN: str = ""
    CINE_PLATFORM_INTERNAL_TOKEN: str = ""

    DIRECTIVAS_DIR: Path = BASE_DIR / "directivas"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()