"""LocalHub API 라우터 모음."""

from app.routers.chat import router as chat_router
from app.routers.health import router as health_router
from app.routers.locations import router as locations_router
from app.routers.posts import router as posts_router
from app.routers.weather import router as weather_router

__all__ = [
    "health_router",
    "locations_router",
    "posts_router",
    "weather_router",
    "chat_router",
]