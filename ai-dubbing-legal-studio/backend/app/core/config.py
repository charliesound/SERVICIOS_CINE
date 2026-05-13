from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AI Dubbing Legal Studio"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    secret_key: str = "change-me"
    jwt_secret: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    database_url: str = "postgresql+asyncpg://dubbing:dubbing@localhost:5432/dubbing_legal"
    redis_url: str = "redis://localhost:6379/0"

    storage_provider: str = "local"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "dubbing"
    minio_secret_key: str = "dubbing-secret"
    minio_bucket: str = "dubbing-assets"
    storage_local_path: str = "./data/storage"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    whisper_model: str = "base"
    tts_provider: str = "comfyui"
    lipsync_provider: str = "comfyui"
    asr_provider: str = "comfyui"

    comfyui_base_url: str = "http://localhost:8188"
    comfyui_still: str = "http://localhost:8188"
    comfyui_video: str = "http://localhost:8189"
    comfyui_dubbing: str = "http://localhost:8190"
    comfyui_lab: str = "http://localhost:8191"

    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: Optional[str] = None

    worker_concurrency: int = 2
    comfyui_poll_interval: int = 2
    comfyui_poll_timeout: int = 300

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
