"""
[신규 파일] 챗봇 질문 분석 결과 스키마

변경 사항
1. [추가] OpenAI가 사용자 질문을 분류할 질문 유형 정의
2. [추가] 서울 자치구, 카테고리, 검색 키워드, 날짜 표현 추출 구조 정의
3. [추가] Structured Outputs에서 사용할 수 있도록 추가 필드를 금지
4. [추가] 자치구·키워드·질문 유형별 값 정규화
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


ChatIntentType = Literal[
    "location_search",
    "festival_search",
    "model_restaurant_search",
    "post_search",
    "weather",
    "general",
    "unsupported",
]


LocationCategoryType = Literal[
    "관광지",
    "문화시설",
    "축제공연행사",
    "여행코스",
    "레포츠",
    "숙박",
    "쇼핑",
    "음식점",
]


SEOUL_DISTRICTS: tuple[str, ...] = (
    "강남구",
    "강동구",
    "강북구",
    "강서구",
    "관악구",
    "광진구",
    "구로구",
    "금천구",
    "노원구",
    "도봉구",
    "동대문구",
    "동작구",
    "마포구",
    "서대문구",
    "서초구",
    "성동구",
    "성북구",
    "송파구",
    "양천구",
    "영등포구",
    "용산구",
    "은평구",
    "종로구",
    "중구",
    "중랑구",
)


# 검색 조건으로 사용해도 의미가 거의 없는 일반 표현이다.
# AI가 제거하도록 지시하지만, 한 번 더 코드에서 정리한다.
GENERIC_KEYWORDS: set[str] = {
    "서울",
    "서울시",
    "서울특별시",
    "관광",
    "관광지",
    "장소",
    "곳",
    "추천",
    "검색",
    "조회",
    "위치",
    "주소",
    "정보",
    "알려줘",
    "찾아줘",
    "보여줘",
    "축제",
    "공연",
    "행사",
    "일정",
    "모범음식점",
    "음식점",
    "식당",
    "커뮤니티",
    "게시글",
    "게시물",
    "글",
    "후기",
    "날씨",
}


class ChatIntentAnalysis(BaseModel):
    """AI가 사용자 질문에서 추출한 검색 의도와 검색 조건."""

    model_config = ConfigDict(
        extra="forbid",
    )

    intent: ChatIntentType = Field(
        description=(
            "사용자 질문 유형. 지역정보 검색은 location_search, "
            "축제·공연·행사는 festival_search, 모범음식점은 "
            "model_restaurant_search, 커뮤니티 글은 post_search, "
            "현재 날씨는 weather, 서비스 안내·인사는 general, "
            "지원 범위 밖 질문은 unsupported"
        ),
    )

    district: str | None = Field(
        description=(
            "질문에 포함된 서울 자치구 이름. 예: 종로구. "
            "자치구가 없거나 확실하지 않으면 null"
        ),
    )

    category: LocationCategoryType | None = Field(
        description=(
            "검색할 지역정보 또는 게시글 카테고리. "
            "카테고리를 특정할 수 없으면 null"
        ),
    )

    keywords: list[str] = Field(
        max_length=8,
        description=(
            "DB 제목·주소·본문·태그에서 찾을 핵심어 목록. "
            "서울, 추천, 위치, 관광지처럼 일반적인 표현은 제외"
        ),
    )

    date_expression: str | None = Field(
        description=(
            "사용자가 말한 날짜 또는 기간 표현. 예: 이번 주말, "
            "7월, 2026-07-20. 날짜 표현이 없으면 null"
        ),
    )

    limit: int = Field(
        ge=1,
        le=10,
        description="사용자가 원하는 결과 수. 별도 요청이 없으면 5",
    )

    reason: str = Field(
        min_length=1,
        max_length=300,
        description="해당 질문 유형과 검색 조건으로 판단한 짧은 이유",
    )

    @field_validator(
        "district",
        mode="before",
    )
    @classmethod
    def normalize_district(
        cls,
        value: object,
    ) -> str | None:
        """서울 자치구 표현을 공식 자치구 이름으로 정규화한다."""

        if value is None:
            return None

        if not isinstance(value, str):
            return None

        normalized = value.strip()

        if not normalized:
            return None

        # "서울특별시 종로구", "서울 종로구"처럼 긴 표현에서도
        # 공식 자치구 이름을 먼저 찾아 반환한다.
        for district in SEOUL_DISTRICTS:
            if district in normalized:
                return district

        normalized = re.sub(
            r"^(서울특별시|서울시|서울)\s*",
            "",
            normalized,
        ).strip()

        if normalized in SEOUL_DISTRICTS:
            return normalized

        district_candidate = f"{normalized}구"

        if district_candidate in SEOUL_DISTRICTS:
            return district_candidate

        # 서울 서비스이므로 확인되지 않은 지역명은 DB 필터로 쓰지 않는다.
        return None

    @field_validator(
        "keywords",
        mode="before",
    )
    @classmethod
    def normalize_keywords(
        cls,
        value: object,
    ) -> list[str]:
        """검색 키워드의 공백과 중복을 정리한다."""

        if value is None:
            return []

        if isinstance(value, str):
            raw_keywords = re.split(
                r"[,|/]",
                value,
            )
        elif isinstance(value, list):
            raw_keywords = value
        else:
            return []

        normalized_keywords: list[str] = []
        seen: set[str] = set()

        for raw_keyword in raw_keywords:
            if not isinstance(raw_keyword, str):
                continue

            keyword = raw_keyword.strip()

            if not keyword:
                continue

            if keyword in GENERIC_KEYWORDS:
                continue

            if len(keyword) > 50:
                keyword = keyword[:50].strip()

            duplicate_key = keyword.casefold()

            if duplicate_key in seen:
                continue

            seen.add(duplicate_key)
            normalized_keywords.append(keyword)

            if len(normalized_keywords) >= 8:
                break

        return normalized_keywords

    @field_validator(
        "date_expression",
        mode="before",
    )
    @classmethod
    def normalize_date_expression(
        cls,
        value: object,
    ) -> str | None:
        """빈 날짜 표현을 null로 정리한다."""

        if value is None:
            return None

        if not isinstance(value, str):
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized[:100]

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def normalize_reason(
        cls,
        value: object,
    ) -> object:
        """분석 이유의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value

    @model_validator(mode="after")
    def normalize_by_intent(
        self,
    ) -> ChatIntentAnalysis:
        """질문 유형에 맞춰 카테고리와 키워드를 최종 정리한다."""

        if self.intent == "festival_search":
            self.category = "축제공연행사"

        elif self.intent == "model_restaurant_search":
            self.category = "음식점"

        elif self.intent in {
            "weather",
            "general",
            "unsupported",
        }:
            self.category = None

        # 자치구와 카테고리 자체는 별도 필터로 사용하므로
        # 검색 키워드 목록에서는 제거한다.
        values_to_remove = {
            value.casefold()
            for value in (
                self.district,
                self.category,
            )
            if value
        }

        self.keywords = [
            keyword
            for keyword in self.keywords
            if keyword.casefold() not in values_to_remove
        ]

        if self.intent != "festival_search":
            self.date_expression = None

        return self