"""데이터베이스 접근 Repository 모듈."""

from app.repositories.location_repository import LocationRepository
from app.repositories.post_repository import PostRepository

__all__ = [
    "LocationRepository",
    "PostRepository",
]