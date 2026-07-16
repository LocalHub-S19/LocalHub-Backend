from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# [수정] 프로젝트 최상위 폴더 경로
#
# 현재 파일:
# LocalHub-Backend/app/core/config.py
#
# parents[0] = app/core
# parents[1] = app
# parents[2] = LocalHub-Backend
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """LocalHub 백엔드 공통 환경설정."""

    # 애플리케이션 설정
    app_name: str = "LocalHub API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # 공통 API prefix
    api_prefix: str = "/api"

    # SQLite
    # [수정] DATABASE_URL과 database_url 중복 제거
    database_url: str = "sqlite:///./data/localhub.db"

    # Vue 개발 서버 및 배포 프론트엔드 주소
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://localhub-s19.netlify.app",
    ]

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    # 날씨 API
    # Open-Meteo는 API 키가 필요하지 않는다.
    weather_api_key: str | None = None
    weather_api_base_url: str = (
        "https://api.open-meteo.com/v1/forecast"
    )

    # 서비스 기본 설정
    target_region: str = "서울"

    # 지도 조회 제한
    default_map_limit: int = 300
    max_map_limit: int = 500

    # 페이지네이션 제한
    default_page_size: int = 20
    max_page_size: int = 100

    # [수정] 실행 위치와 관계없이 프로젝트 루트의 .env를 읽는다.
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """환경설정을 한 번 생성한 뒤 재사용한다."""

    return Settings()


settings = get_settings()