from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.location import (
    LocationDetailResponse,
    LocationListResponse,
    LocationMapListResponse,
)
from app.services.location_service import LocationService


router = APIRouter(
    prefix="/locations",
    tags=["서울 지역정보"],
)


@router.get(
    "",
    response_model=LocationListResponse,
    summary="지역정보 목록 조회",
    description=(
        "서울의 관광지, 문화시설, 숙박, 음식점 등 지역정보를 "
        "카테고리와 검색어 기준으로 조회합니다."
    ),
)
def get_locations(
    category: str | None = Query(
        default=None,
        max_length=50,
        description="지역정보 카테고리",
        examples=["문화시설"],
    ),
    keyword: str | None = Query(
        default=None,
        max_length=100,
        description="장소명 또는 주소 검색어",
        examples=["박물관"],
    ),
    sigungu_code: str | None = Query(
        default=None,
        max_length=20,
        description="서울 시군구 코드",
        examples=["1"],
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호",
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=settings.max_page_size,
        description="페이지당 조회 개수",
    ),
    db: Session = Depends(get_db),
) -> LocationListResponse:
    """서울 지역정보 목록을 조회한다."""

    service = LocationService(db)

    return service.get_locations(
        category=category,
        keyword=keyword,
        sigungu_code=sigungu_code,
        page=page,
        size=size,
    )


@router.get(
    "/map",
    response_model=LocationMapListResponse,
    summary="지도 마커 목록 조회",
    description=(
        "위도와 경도가 존재하는 서울 지역정보만 "
        "지도 마커에 필요한 형태로 조회합니다."
    ),
)
def get_location_map_markers(
    category: str | None = Query(
        default=None,
        max_length=50,
        description="지역정보 카테고리",
        examples=["관광지"],
    ),
    keyword: str | None = Query(
        default=None,
        max_length=100,
        description="장소명 또는 주소 검색어",
        examples=["남산"],
    ),
    sigungu_code: str | None = Query(
        default=None,
        max_length=20,
        description="서울 시군구 코드",
        examples=["21"],
    ),
    limit: int = Query(
        default=settings.default_map_limit,
        ge=1,
        le=settings.max_map_limit,
        description="반환할 최대 지도 마커 수",
    ),
    db: Session = Depends(get_db),
) -> LocationMapListResponse:
    """좌표가 존재하는 지역정보를 지도용으로 조회한다."""

    service = LocationService(db)

    return service.get_map_markers(
        category=category,
        keyword=keyword,
        sigungu_code=sigungu_code,
        limit=limit,
    )


@router.get(
    "/{content_id}",
    response_model=LocationDetailResponse,
    summary="지역정보 상세 조회",
    description="콘텐츠 ID에 해당하는 서울 지역정보의 상세 내용을 조회합니다.",
    responses={
        404: {
            "description": "해당 지역정보를 찾을 수 없음",
        },
    },
)
def get_location_detail(
    content_id: str = Path(
        ...,
        min_length=1,
        max_length=30,
        description="TourAPI 콘텐츠 고유 ID",
        examples=["126508"],
    ),
    db: Session = Depends(get_db),
) -> LocationDetailResponse:
    """콘텐츠 ID로 지역정보 한 건을 조회한다."""

    service = LocationService(db)

    return service.get_location_detail(
        content_id=content_id,
    )