from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(
    prefix="/health",
    tags=["시스템"],
)


@router.get(
    "",
    summary="서버 상태 확인",
    description="LocalHub 백엔드 서버의 실행 상태를 확인합니다.",
)
def health_check() -> dict[str, str]:
    """백엔드 서버 상태를 반환한다."""

    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }