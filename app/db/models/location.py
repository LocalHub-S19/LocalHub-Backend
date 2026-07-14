from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utc_now() -> datetime:
    """현재 UTC 시각을 반환한다."""
    return datetime.now(timezone.utc)


class Location(Base):
    """한국관광공사 TourAPI에서 제공한 서울 지역정보 모델."""

    __tablename__ = "locations"

    __table_args__ = (
        Index(
            "idx_locations_category",
            "category",
        ),
        Index(
            "idx_locations_content_type_id",
            "content_type_id",
        ),
        Index(
            "idx_locations_title",
            "title",
        ),
        Index(
            "idx_locations_sigungu_code",
            "sigungu_code",
        ),
        Index(
            "idx_locations_coordinates",
            "latitude",
            "longitude",
        ),
    )

    # 한국관광공사 콘텐츠 고유 ID
    content_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    # 수집 권역: 현재 프로젝트에서는 서울
    region: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="서울",
    )

    # 콘텐츠 유형 ID
    # 12 관광지, 14 문화시설, 15 축제공연행사,
    # 25 여행코스, 28 레포츠, 32 숙박,
    # 38 쇼핑, 39 음식점
    content_type_id: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # 콘텐츠 유형의 한글명
    # 예: 관광지, 문화시설, 숙박
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # 장소명
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # 기본 주소
    addr1: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    # 상세 주소
    addr2: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    # 우편번호
    zipcode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 전화번호
    tel: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # 경도: 원본 JSON의 mapx
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # 위도: 원본 JSON의 mapy
    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # 지도 확대 레벨
    map_level: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    # 지역 코드
    area_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 시군구 코드
    sigungu_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 법정동 지역 코드
    legal_region_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 법정동 시군구 코드
    legal_sigungu_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 관광정보 대분류 코드
    cat1: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 관광정보 중분류 코드
    cat2: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 관광정보 소분류 코드
    cat3: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 분류 체계 1
    class_system1: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # 분류 체계 2
    class_system2: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # 분류 체계 3
    class_system3: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # 대표 이미지 URL
    first_image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # 썸네일 이미지 URL
    thumbnail_image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # 저작권 구분 코드
    copyright_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # TourAPI 원본 최초 등록 시각
    # 원본 형식: YYYYMMDDHHmmss
    source_created_at: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
    )

    # TourAPI 원본 최종 수정 시각
    # 원본 형식: YYYYMMDDHHmmss
    source_modified_at: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
    )

    # 적재한 원본 JSON 파일명
    # 예: 서울_관광지.json
    source_file: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # SQLite에 데이터를 적재한 시각
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    def __repr__(self) -> str:
        return (
            f"Location("
            f"content_id={self.content_id!r}, "
            f"category={self.category!r}, "
            f"title={self.title!r}"
            f")"
        )