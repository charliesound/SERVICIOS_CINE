from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    app_name: str = "CINE AI PLATFORM API"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 3000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    shots_store_backend: str = "json"
    shots_json_file: str = str(DATA_DIR / "shots.json")
    shots_sqlite_file: str = str(DATA_DIR / "shots.db")
    render_jobs_sqlite_file: str = str(DATA_DIR / "render_jobs.db")
    auth_sqlite_file: str = str(DATA_DIR / "auth.db")
    auth_session_ttl_days: int = 30
    auth_bootstrap_users: str = "admin@cine.local:CHANGE_ME_ADMIN_PASSWORD:admin"
    enable_legacy_routes: bool = False
    enable_render_context_flags: bool = False
    comfyui_base_url: str = "http://127.0.0.1:8188"
    comfyui_timeout_seconds: float = 2.5
    embeddings_service_base_url: str = "http://host.docker.internal:8091"
    embeddings_service_timeout_seconds: float = 5.0
    qdrant_base_url: str = "http://qdrant:6333"
    qdrant_timeout_seconds: float = 5.0
    semantic_context_collection: str = "cine_project_context"
    semantic_context_vector_size: int = 384
    sequence_semantic_context_limit: int = 5
    sequence_semantic_prompt_enrichment_enabled: bool = True
    sequence_semantic_prompt_enrichment_max_chars: int = 400
    ipadapter_sdxl_model: str = "ip-adapter-plus_sdxl_vit-h.safetensors"
    clip_vision_model: str = "clip_vision_h.safetensors"

    # Follow-up email settings
    followup_send_mode: str = "simulated"  # disabled | simulated | smtp
    followup_auto_send_enabled: bool = False
    followup_from_name: str = "CID"
    followup_from_email: str = "noreply@cid.example.com"
    followup_reply_to: str = ""
    followup_test_recipient: str = ""
    followup_default_campaign_key: str = "cid_storyboard_ia"
    followup_sqlite_file: str = str(DATA_DIR / "followups.db")

    # SMTP settings
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = 30
    smtp_allow_self_signed: bool = False


    model_config = SettingsConfigDict(
        env_file=(".env.private", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
