from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


LocationCategory = Literal[
    "관광지",
    "문화시설",
    "축제공연행사",
    "여행코스",
    "레포츠",
    "숙박",
    "쇼핑",
    "음식점",
]


class LocationListItemResponse(BaseModel):
    """지역정보 목록에서 사용하는 간략 응답."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    content_id: str = Field(
        description="TourAPI 콘텐츠 고유 ID",
        examples=["126508"],
    )

    content_type_id: str = Field(
        description="TourAPI 콘텐츠 유형 ID",
        examples=["14"],
    )

    category: str = Field(
        description="지역정보 카테고리",
        examples=["문화시설"],
    )

    title: str = Field(
        description="장소명",
        examples=["서울역사박물관"],
    )

    addr1: str | None = Field(
        default=None,
        description="기본 주소",
        examples=["서울특별시 종로구 새문안로 55"],
    )

    addr2: str | None = Field(
        default=None,
        description="상세 주소 또는 건물명",
        examples=["서울역사박물관"],
    )

    tel: str | None = Field(
        default=None,
        description="전화번호",
        examples=["02-724-0274"],
    )

    longitude: float | None = Field(
        default=None,
        description="경도",
        examples=[126.9705],
    )

    latitude: float | None = Field(
        default=None,
        description="위도",
        examples=[37.5704],
    )

    thumbnail_image: str | None = Field(
        default=None,
        description="대표 이미지 썸네일 URL",
    )


class LocationDetailResponse(BaseModel):
    """지역정보 상세조회 응답."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    content_id: str = Field(
        description="TourAPI 콘텐츠 고유 ID",
        examples=["126508"],
    )

    region: str = Field(
        description="수집 지역",
        examples=["서울"],
    )

    content_type_id: str = Field(
        description="TourAPI 콘텐츠 유형 ID",
        examples=["14"],
    )

    category: str = Field(
        description="지역정보 카테고리",
        examples=["문화시설"],
    )

    title: str = Field(
        description="장소명",
        examples=["서울역사박물관"],
    )

    addr1: str | None = Field(
        default=None,
        description="기본 주소",
        examples=["서울특별시 종로구 새문안로 55"],
    )

    addr2: str | None = Field(
        default=None,
        description="상세 주소 또는 건물명",
    )

    zipcode: str | None = Field(
        default=None,
        description="우편번호",
        examples=["03177"],
    )

    tel: str | None = Field(
        default=None,
        description="전화번호",
        examples=["02-724-0274"],
    )

    longitude: float | None = Field(
        default=None,
        description="경도",
        examples=[126.9705],
    )

    latitude: float | None = Field(
        default=None,
        description="위도",
        examples=[37.5704],
    )

    map_level: str | None = Field(
        default=None,
        description="TourAPI 지도 확대 레벨",
    )

    area_code: str | None = Field(
        default=None,
        description="지역 코드",
        examples=["1"],
    )

    sigungu_code: str | None = Field(
        default=None,
        description="시군구 코드",
        examples=["23"],
    )

    legal_region_code: str | None = Field(
        default=None,
        description="법정동 지역 코드",
    )

    legal_sigungu_code: str | None = Field(
        default=None,
        description="법정동 시군구 코드",
    )

    cat1: str | None = Field(
        default=None,
        description="관광정보 대분류 코드",
    )

    cat2: str | None = Field(
        default=None,
        description="관광정보 중분류 코드",
    )

    cat3: str | None = Field(
        default=None,
        description="관광정보 소분류 코드",
    )

    class_system1: str | None = Field(
        default=None,
        description="분류 체계 1",
    )

    class_system2: str | None = Field(
        default=None,
        description="분류 체계 2",
    )

    class_system3: str | None = Field(
        default=None,
        description="분류 체계 3",
    )

    first_image: str | None = Field(
        default=None,
        description="대표 이미지 원본 URL",
    )

    thumbnail_image: str | None = Field(
        default=None,
        description="대표 이미지 썸네일 URL",
    )

    copyright_code: str | None = Field(
        default=None,
        description="저작권 구분 코드",
    )

    source_created_at: str | None = Field(
        default=None,
        description="TourAPI 원본 최초 등록 시각",
        examples=["20240101120000"],
    )

    source_modified_at: str | None = Field(
        default=None,
        description="TourAPI 원본 최종 수정 시각",
        examples=["20260710153000"],
    )

    imported_at: datetime = Field(
        description="SQLite 데이터 적재 시각",
    )


class LocationListResponse(BaseModel):
    """지역정보 목록과 페이지네이션 정보 응답."""

    items: list[LocationListItemResponse] = Field(
        default_factory=list,
        description="지역정보 목록",
    )

    total: int = Field(
        ge=0,
        description="검색 조건에 해당하는 전체 데이터 수",
        examples=[120],
    )

    page: int = Field(
        ge=1,
        description="현재 페이지 번호",
        examples=[1],
    )

    size: int = Field(
        ge=1,
        description="페이지당 데이터 수",
        examples=[20],
    )

    total_pages: int = Field(
        ge=0,
        description="전체 페이지 수",
        examples=[6],
    )


class LocationMapItemResponse(BaseModel):
    """지도 마커에 필요한 지역정보 응답."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    content_id: str = Field(
        description="TourAPI 콘텐츠 고유 ID",
        examples=["126508"],
    )

    category: str = Field(
        description="지역정보 카테고리",
        examples=["관광지"],
    )

    title: str = Field(
        description="장소명",
        examples=["남산서울타워"],
    )

    addr1: str | None = Field(
        default=None,
        description="기본 주소",
        examples=["서울특별시 용산구 남산공원길 105"],
    )

    longitude: float = Field(
        description="지도 마커 경도",
        examples=[126.9882],
    )

    latitude: float = Field(
        description="지도 마커 위도",
        examples=[37.5512],
    )

    thumbnail_image: str | None = Field(
        default=None,
        description="지도 팝업용 썸네일 URL",
    )


class LocationMapListResponse(BaseModel):
    """지도 마커 목록 응답."""

    items: list[LocationMapItemResponse] = Field(
        default_factory=list,
        description="지도 마커 목록",
    )

    count: int = Field(
        ge=0,
        description="반환된 지도 마커 수",
        examples=[300],
    )