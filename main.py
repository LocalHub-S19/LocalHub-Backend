from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import create_tables
from app.routers import (
    chat,
    health,
    locations,
    posts,
    weather,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


# 중요: settings.cors_origins를 실제 미들웨어에 전달
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    create_tables()

    # Render 로그에서 실제 적용된 Origin 확인용
    print(f"[CORS] allowed origins: {settings.cors_origins}")


app.include_router(
    health.router,
    prefix=settings.api_prefix,
)
app.include_router(
    locations.router,
    prefix=settings.api_prefix,
)
app.include_router(
    posts.router,
    prefix=settings.api_prefix,
)
app.include_router(
    weather.router,
    prefix=settings.api_prefix,
)
app.include_router(
    chat.router,
    prefix=settings.api_prefix,
)