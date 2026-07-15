"""
[신규 파일] 챗봇 전용 읽기 Repository

변경 사항
1. [추가] 지역정보·축제·모범음식점·게시글 검색 기능
2. [추가] 검색어 일치 개수에 따른 간단한 관련도 정렬
3. [추가] SQL LIKE 특수문자 이스케이프 처리
4. [주의] 기존 location_repository.py와 post_repository.py는 수정하지 않음
5. [주의] 이 Repository는 조회만 수행하며 DB 데이터를 변경하지 않음
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.location import Location
from app.db.models.post import Post
from app.db.models.post_tag import PostTag


CONTENT_TYPE_BY_CATEGORY: dict[str, str] = {
    "관광지": "12",
    "문화시설": "14",
    "축제공연행사": "15",
    "여행코스": "25",
    "레포츠": "28",
    "숙박": "32",
    "쇼핑": "38",
    "음식점": "39",
}


class ChatSearchRepository:
    """챗봇에서 사용할 지역정보와 게시글을 읽기 전용으로 검색한다."""

    MAX_LIMIT = 10

    @classmethod
    def _normalize_limit(
        cls,
        limit: int,
    ) -> int:
        """조회 개수를 1~10 범위로 제한한다."""

        return max(
            1,
            min(cls.MAX_LIMIT, limit),
        )

    @staticmethod
    def _escape_like_keyword(
        keyword: str,
    ) -> str:
        """SQL LIKE에서 특별한 의미를 갖는 문자를 이스케이프한다."""

        return (
            keyword.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

    @classmethod
    def _like_pattern(
        cls,
        keyword: str,
    ) -> str:
        """부분 일치 검색에 사용할 LIKE 패턴을 만든다."""

        return f"%{cls._escape_like_keyword(keyword)}%"

    @staticmethod
    def _normalize_keywords(
        keywords: list[str],
    ) -> list[str]:
        """빈 검색어와 중복 검색어를 제거한다."""

        normalized: list[str] = []
        seen: set[str] = set()

        for raw_keyword in keywords:
            keyword = raw_keyword.strip()

            if not keyword:
                continue

            duplicate_key = keyword.casefold()

            if duplicate_key in seen:
                continue

            seen.add(duplicate_key)
            normalized.append(keyword[:50])

            if len(normalized) >= 8:
                break

        return normalized

    @classmethod
    def _build_location_keyword_parts(
        cls,
        keywords: list[str],
    ) -> tuple[list[Any], list[Any]]:
        """지역정보 검색 조건과 관련도 점수 표현식을 만든다."""

        keyword_conditions: list[Any] = []
        score_parts: list[Any] = []

        for keyword in cls._normalize_keywords(keywords):
            pattern = cls._like_pattern(keyword)

            title_match = Location.title.ilike(
                pattern,
                escape="\\",
            )

            address_match = or_(
                Location.addr1.ilike(
                    pattern,
                    escape="\\",
                ),
                Location.addr2.ilike(
                    pattern,
                    escape="\\",
                ),
            )

            category_match = Location.category.ilike(
                pattern,
                escape="\\",
            )

            classification_match = or_(
                Location.class_system1.ilike(
                    pattern,
                    escape="\\",
                ),
                Location.class_system2.ilike(
                    pattern,
                    escape="\\",
                ),
                Location.class_system3.ilike(
                    pattern,
                    escape="\\",
                ),
                Location.source_file.ilike(
                    pattern,
                    escape="\\",
                ),
            )

            keyword_condition = or_(
                title_match,
                address_match,
                category_match,
                classification_match,
            )

            keyword_conditions.append(
                keyword_condition
            )

            # 장소명 일치를 가장 높게 평가하고,
            # 주소·카테고리·분류 정보 순으로 가중치를 준다.
            score_parts.append(
                case(
                    (title_match, 4),
                    else_=0,
                )
                + case(
                    (address_match, 2),
                    else_=0,
                )
                + case(
                    (category_match, 1),
                    else_=0,
                )
                + case(
                    (classification_match, 1),
                    else_=0,
                )
            )

        return keyword_conditions, score_parts

    @staticmethod
    def _sum_score_parts(
        score_parts: list[Any],
    ) -> Any | None:
        """여러 관련도 점수 표현식을 하나로 합친다."""

        if not score_parts:
            return None

        score_expression = score_parts[0]

        for score_part in score_parts[1:]:
            score_expression = (
                score_expression + score_part
            )

        return score_expression

    @classmethod
    def _search_location_rows(
        cls,
        db: Session,
        *,
        base_filters: list[Any],
        district: str | None,
        keywords: list[str],
        limit: int,
    ) -> list[Location]:
        """공통 조건으로 locations 테이블을 검색한다."""

        filters = list(base_filters)

        if district:
            district_pattern = cls._like_pattern(
                district
            )

            filters.append(
                or_(
                    Location.addr1.ilike(
                        district_pattern,
                        escape="\\",
                    ),
                    Location.addr2.ilike(
                        district_pattern,
                        escape="\\",
                    ),
                )
            )

        (
            keyword_conditions,
            score_parts,
        ) = cls._build_location_keyword_parts(
            keywords=keywords,
        )

        if keyword_conditions:
            # 키워드 중 하나 이상이 일치하는 결과를 조회하고,
            # 여러 키워드에 일치할수록 위로 정렬한다.
            filters.append(
                or_(*keyword_conditions)
            )

        statement = select(Location)

        if filters:
            statement = statement.where(
                *filters
            )

        score_expression = cls._sum_score_parts(
            score_parts
        )

        if score_expression is not None:
            statement = statement.order_by(
                score_expression.desc(),
                Location.title.asc(),
            )
        else:
            statement = statement.order_by(
                Location.title.asc(),
            )

        statement = statement.limit(
            cls._normalize_limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @classmethod
    def search_locations(
        cls,
        db: Session,
        *,
        category: str | None,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[Location]:
        """관광지·문화시설·숙박 등 일반 지역정보를 검색한다."""

        base_filters: list[Any] = []

        if category:
            content_type_id = (
                CONTENT_TYPE_BY_CATEGORY.get(
                    category
                )
            )

            if content_type_id:
                base_filters.append(
                    or_(
                        Location.category == category,
                        Location.content_type_id
                        == content_type_id,
                    )
                )
            else:
                base_filters.append(
                    Location.category == category
                )

        return cls._search_location_rows(
            db=db,
            base_filters=base_filters,
            district=district,
            keywords=keywords,
            limit=limit,
        )

    @classmethod
    def search_festivals(
        cls,
        db: Session,
        *,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[Location]:
        """축제·공연·행사 지역정보를 검색한다.

        현재 Location 모델에는 실제 행사 시작일과 종료일 필드가 없다.
        따라서 이 메서드는 축제 목록과 위치만 검색하며,
        source_created_at/source_modified_at을 행사 일정으로 사용하지 않는다.
        """

        festival_filter = or_(
            Location.content_type_id == "15",
            Location.category == "축제공연행사",
            Location.category.ilike(
                "%축제%",
                escape="\\",
            ),
            Location.category.ilike(
                "%공연%",
                escape="\\",
            ),
            Location.category.ilike(
                "%행사%",
                escape="\\",
            ),
        )

        return cls._search_location_rows(
            db=db,
            base_filters=[festival_filter],
            district=district,
            keywords=keywords,
            limit=limit,
        )

    @classmethod
    def search_model_restaurants(
        cls,
        db: Session,
        *,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[Location]:
        """DB에서 모범음식점으로 확인 가능한 장소만 검색한다.

        일반 음식점을 모범음식점으로 잘못 안내하지 않도록,
        카테고리·원본 파일명·분류명·장소명 중 하나에
        '모범' 표시가 있는 데이터만 반환한다.
        """

        restaurant_filter = or_(
            Location.content_type_id == "39",
            Location.category == "음식점",
            Location.category.ilike(
                "%모범%",
                escape="\\",
            ),
        )

        model_restaurant_marker = or_(
            Location.category.ilike(
                "%모범%",
                escape="\\",
            ),
            Location.title.ilike(
                "%모범%",
                escape="\\",
            ),
            Location.source_file.ilike(
                "%모범%",
                escape="\\",
            ),
            Location.class_system1.ilike(
                "%모범%",
                escape="\\",
            ),
            Location.class_system2.ilike(
                "%모범%",
                escape="\\",
            ),
            Location.class_system3.ilike(
                "%모범%",
                escape="\\",
            ),
        )

        return cls._search_location_rows(
            db=db,
            base_filters=[
                restaurant_filter,
                model_restaurant_marker,
            ],
            district=district,
            keywords=keywords,
            limit=limit,
        )

    @classmethod
    def search_posts(
        cls,
        db: Session,
        *,
        category: str | None,
        district: str | None,
        keywords: list[str],
        limit: int = 5,
    ) -> list[Post]:
        """게시글 제목·내용·카테고리·태그를 검색한다."""

        filters: list[Any] = []

        if category:
            filters.append(
                Post.category == category
            )

        search_terms = list(keywords)

        # 게시글에는 별도 주소 필드가 없으므로,
        # 자치구 이름도 제목·본문·태그에서 검색한다.
        if district:
            search_terms.append(district)

        normalized_terms = cls._normalize_keywords(
            search_terms
        )

        term_conditions: list[Any] = []
        score_parts: list[Any] = []

        for keyword in normalized_terms:
            pattern = cls._like_pattern(keyword)

            title_match = Post.title.ilike(
                pattern,
                escape="\\",
            )

            content_match = Post.content.ilike(
                pattern,
                escape="\\",
            )

            category_match = Post.category.ilike(
                pattern,
                escape="\\",
            )

            tag_match = Post.tags.any(
                PostTag.tag.ilike(
                    pattern,
                    escape="\\",
                )
            )

            term_condition = or_(
                title_match,
                content_match,
                category_match,
                tag_match,
            )

            term_conditions.append(
                term_condition
            )

            score_parts.append(
                case(
                    (title_match, 4),
                    else_=0,
                )
                + case(
                    (tag_match, 3),
                    else_=0,
                )
                + case(
                    (content_match, 2),
                    else_=0,
                )
                + case(
                    (category_match, 1),
                    else_=0,
                )
            )

        if term_conditions:
            filters.append(
                or_(*term_conditions)
            )

        statement = select(Post).options(
            selectinload(Post.tags)
        )

        if filters:
            statement = statement.where(
                *filters
            )

        score_expression = cls._sum_score_parts(
            score_parts
        )

        if score_expression is not None:
            statement = statement.order_by(
                score_expression.desc(),
                Post.view_count.desc(),
                Post.created_at.desc(),
            )
        else:
            statement = statement.order_by(
                Post.created_at.desc(),
            )

        statement = statement.limit(
            cls._normalize_limit(limit)
        )

        return list(
            db.scalars(statement)
            .unique()
            .all()
        )