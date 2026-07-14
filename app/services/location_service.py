from __future__ import annotations

import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.location_repository import LocationRepository
from app.schemas.location import (
    LocationDetailResponse,
    LocationListItemResponse,
    LocationListResponse,
    LocationMapItemResponse,
    LocationMapListResponse,
)


class LocationService:
    """서울 지역정보 조회 비즈니스 로직을 담당한다."""

    def __init__(self, db: Session) -> None:
        """DB 세션을 저장한다."""

        self.db = db

    def get_locations(
        self,
        category: str | None = None,
        keyword: str | None = None,
        sigungu_code: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> LocationListResponse:
        """
        서울 지역정보 목록을 조회한다.

        지원 기능:
        - 카테고리 필터
        - 장소명·주소 검색
        - 시군구 코드 필터
        - 페이지네이션
        """

        locations, total = LocationRepository.find_all(
            db=self.db,
            category=category,
            keyword=keyword,
            sigungu_code=sigungu_code,
            page=page,
            size=size,
        )

        items = [
            LocationListItemResponse(
                content_id=location.content_id,
                content_type_id=location.content_type_id,
                category=location.category,
                title=location.title,
                addr1=location.addr1,
                addr2=location.addr2,
                tel=location.tel,
                longitude=location.longitude,
                latitude=location.latitude,
                thumbnail_image=location.thumbnail_image,
            )
            for location in locations
        ]

        total_pages = (
            math.ceil(total / size)
            if total > 0
            else 0
        )

        return LocationListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    def get_location_detail(
        self,
        content_id: str,
    ) -> LocationDetailResponse:
        """콘텐츠 ID에 해당하는 지역정보 상세내용을 조회한다."""

        location = LocationRepository.find_by_content_id(
            db=self.db,
            content_id=content_id,
        )

        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 지역정보를 찾을 수 없습니다.",
            )

        return LocationDetailResponse(
            content_id=location.content_id,
            region=location.region,
            content_type_id=location.content_type_id,
            category=location.category,
            title=location.title,
            addr1=location.addr1,
            addr2=location.addr2,
            zipcode=location.zipcode,
            tel=location.tel,
            longitude=location.longitude,
            latitude=location.latitude,
            map_level=location.map_level,
            area_code=location.area_code,
            sigungu_code=location.sigungu_code,
            legal_region_code=location.legal_region_code,
            legal_sigungu_code=location.legal_sigungu_code,
            cat1=location.cat1,
            cat2=location.cat2,
            cat3=location.cat3,
            class_system1=location.class_system1,
            class_system2=location.class_system2,
            class_system3=location.class_system3,
            first_image=location.first_image,
            thumbnail_image=location.thumbnail_image,
            copyright_code=location.copyright_code,
            source_created_at=location.source_created_at,
            source_modified_at=location.source_modified_at,
            imported_at=location.imported_at,
        )

    def get_map_markers(
        self,
        category: str | None = None,
        keyword: str | None = None,
        sigungu_code: str | None = None,
        limit: int = 300,
    ) -> LocationMapListResponse:
        """
        위도와 경도가 존재하는 지역정보를 지도 마커용으로 조회한다.
        """

        locations = LocationRepository.find_map_markers(
            db=self.db,
            category=category,
            keyword=keyword,
            sigungu_code=sigungu_code,
            limit=limit,
        )

        items: list[LocationMapItemResponse] = []

        for location in locations:
            # Repository에서도 좌표가 없는 데이터를 제외하지만,
            # 응답 생성 전 한 번 더 확인한다.
            if (
                location.latitude is None
                or location.longitude is None
            ):
                continue

            items.append(
                LocationMapItemResponse(
                    content_id=location.content_id,
                    category=location.category,
                    title=location.title,
                    addr1=location.addr1,
                    longitude=location.longitude,
                    latitude=location.latitude,
                    thumbnail_image=location.thumbnail_image,
                )
            )

        return LocationMapListResponse(
            items=items,
            count=len(items),
        )