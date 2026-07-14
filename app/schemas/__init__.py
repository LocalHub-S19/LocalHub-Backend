"""LocalHub API 요청 및 응답 스키마 모음."""

from app.schemas.chat import (
    ChatMessage,
    ChatReference,
    ChatRequest,
    ChatResponse,
)
from app.schemas.location import (
    LocationDetailResponse,
    LocationListItemResponse,
    LocationListResponse,
    LocationMapItemResponse,
    LocationMapListResponse,
)
from app.schemas.post import (
    PostCreateRequest,
    PostDeleteRequest,
    PostDetailResponse,
    PostListItemResponse,
    PostListResponse,
    PostUpdateRequest,
)
from app.schemas.weather import WeatherResponse

__all__ = [
    "LocationListItemResponse",
    "LocationDetailResponse",
    "LocationListResponse",
    "LocationMapItemResponse",
    "LocationMapListResponse",
    "PostCreateRequest",
    "PostUpdateRequest",
    "PostDeleteRequest",
    "PostListItemResponse",
    "PostDetailResponse",
    "PostListResponse",
    "WeatherResponse",
    "ChatMessage",
    "ChatReference",
    "ChatRequest",
    "ChatResponse",
]