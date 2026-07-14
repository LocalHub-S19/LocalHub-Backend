from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import create_tables
from app.routers import (
    chat_router,
    health_router,
    locations_router,
    posts_router,
    weather_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """애플리케이션 시작 시 필요한 초기화 작업을 실행한다."""

    create_tables()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix=settings.api_prefix,
)

app.include_router(
    locations_router,
    prefix=settings.api_prefix,
)

app.include_router(
    posts_router,
    prefix=settings.api_prefix,
)

app.include_router(
    weather_router,
    prefix=settings.api_prefix,
)

app.include_router(
    chat_router,
    prefix=settings.api_prefix,
)


@app.get(
    "/",
    tags=["시스템"],
    summary="API 루트",
)
def root() -> dict[str, str]:
    """API 기본 정보를 반환한다."""

    return {
        "message": "LocalHub API",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }