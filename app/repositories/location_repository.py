def get_locations(db):
    return []
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models.location import Location


class LocationRepository:
    """서울 지역정보 데이터 접근을 담당한다."""

    @staticmethod
    def _build_filters(
        category: str | None = None,
        keyword: str | None = None,
        sigungu_code: str | None = None,
    ) -> list:
        """지역정보 검색 조건을 생성한다."""

        filters = []

        if category:
            filters.append(Location.category == category.strip())

        if sigungu_code:
            filters.append(Location.sigungu_code == sigungu_code.strip())

        if keyword and keyword.strip():
            search_keyword = f"%{keyword.strip()}%"

            filters.append(
                or_(
                    Location.title.ilike(search_keyword),
                    Location.addr1.ilike(search_keyword),
                    Location.addr2.ilike(search_keyword),
                )
            )

        return filters

    @staticmethod
    def find_all(
        db: Session,
        category: str | None = None,
        keyword: str | None = None,
        sigungu_code: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Location], int]:
        """
        지역정보 목록을 조회한다.

        반환값:
            (지역정보 목록, 전체 데이터 수)
        """

        filters = LocationRepository._build_filters(
            category=category,
            keyword=keyword,
            sigungu_code=sigungu_code,
        )

        count_statement = (
            select(func.count(Location.content_id))
            .where(*filters)
        )

        total = db.scalar(count_statement) or 0

        offset = (page - 1) * size

        statement = (
            select(Location)
            .where(*filters)
            .order_by(Location.title.asc())
            .offset(offset)
            .limit(size)
        )

        locations = list(db.scalars(statement).all())

        return locations, total

    @staticmethod
    def find_by_content_id(
        db: Session,
        content_id: str,
    ) -> Location | None:
        """콘텐츠 ID로 지역정보 한 건을 조회한다."""

        return db.get(Location, content_id)

    @staticmethod
    def find_map_markers(
        db: Session,
        category: str | None = None,
        keyword: str | None = None,
        sigungu_code: str | None = None,
        limit: int = 300,
    ) -> list[Location]:
        """위도와 경도가 있는 지역정보만 지도용으로 조회한다."""

        filters = LocationRepository._build_filters(
            category=category,
            keyword=keyword,
            sigungu_code=sigungu_code,
        )

        statement = (
            select(Location)
            .where(
                Location.latitude.is_not(None),
                Location.longitude.is_not(None),
                *filters,
            )
            .order_by(Location.title.asc())
            .limit(limit)
        )

        return list(db.scalars(statement).all())