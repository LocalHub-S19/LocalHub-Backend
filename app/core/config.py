from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """LocalHub 백엔드 공통 환경설정."""

    # 애플리케이션
    app_name: str = "LocalHub API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # API
    api_prefix: str = "/api"

    # Database
    database_url: str = "sqlite:///./data/localhub.db"

    # CORS
    # 로컬 기본값만 코드에 작성하고,
    # 배포 주소는 Render의 CORS_ORIGINS 환경변수로 덮어쓴다.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://localhub-s19.netlify.app",
    ]

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    # Weather
    weather_api_key: str | None = None
    weather_api_base_url: str = (
        "https://api.open-meteo.com/v1/forecast"
    )

    # Service
    target_region: str = "서울"

    # Map
    default_map_limit: int = 300
    max_map_limit: int = 500

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @field_validator("cors_origins")
    @classmethod
    def normalize_cors_origins(
        cls,
        origins: list[str],
    ) -> list[str]:
        """끝의 슬래시와 공백을 제거해 Origin 비교 오류를 방지한다."""

        return [
            origin.strip().rstrip("/")
            for origin in origins
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()