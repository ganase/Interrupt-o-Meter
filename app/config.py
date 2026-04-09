from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "Interrupt-o-Meter"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    openai_timeout_sec: int = int(os.getenv("OPENAI_TIMEOUT_SEC", "30"))

    ms_tenant_id: str = os.getenv("MS_TENANT_ID", "")
    ms_client_id: str = os.getenv("MS_CLIENT_ID", "")
    ms_client_secret: str = os.getenv("MS_CLIENT_SECRET", "")
    ms_redirect_uri: str = os.getenv("MS_REDIRECT_URI", "")
    ms_auth_mode: str = os.getenv("MS_AUTH_MODE", "device_code")
    graph_scope: str = os.getenv("GRAPH_SCOPE", "Calendars.ReadBasic")

    default_lookback_days: int = int(os.getenv("DEFAULT_LOOKBACK_DAYS", "14"))
    calendar_cache_ttl_sec: int = int(os.getenv("CALENDAR_CACHE_TTL_SEC", "300"))

    frame_interval_sec: int = int(os.getenv("FRAME_INTERVAL_SEC", "5"))
    image_max_width: int = int(os.getenv("IMAGE_MAX_WIDTH", "1024"))
    image_jpeg_quality: float = float(os.getenv("IMAGE_JPEG_QUALITY", "0.75"))

    schedule_weight: float = float(os.getenv("SCHEDULE_WEIGHT", "0.6"))
    visual_weight: float = float(os.getenv("VISUAL_WEIGHT", "0.4"))

    store_images: bool = _as_bool(os.getenv("STORE_IMAGES"), False)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")


settings = Settings()
