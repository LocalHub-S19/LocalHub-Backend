from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


PostCategory = Literal[
    "관광지",
    "문화시설",
    "축제공연행사",
    "여행코스",
    "레포츠",
    "숙박",
    "쇼핑",
    "음식점",
    "자유",
]


def normalize_text(value: str) -> str:
    """문자열의 앞뒤 공백을 제거한다."""

    return value.strip()


def normalize_tags(value: Any) -> list[str]:
    """
    태그 값을 정리한다.

    처리 내용:
    - None이면 빈 목록으로 변환
    - 문자열이면 쉼표 기준으로 분리
    - 앞뒤 공백 제거
    - 맨 앞의 # 제거
    - 빈 태그 제거
    - 중복 태그 제거
    """

    if value is None:
        return []

    if isinstance(value, str):
        raw_tags = value.split(",")
    elif isinstance(value, list):
        raw_tags = value
    else:
        raise ValueError("태그는 문자열 배열이어야 합니다.")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw_tag in raw_tags:
        if not isinstance(raw_tag, str):
            raise ValueError("각 태그는 문자열이어야 합니다.")

        tag = raw_tag.strip()

        if tag.startswith("#"):
            tag = tag[1:].strip()

        if not tag:
            continue

        duplicate_key = tag.casefold()

        if duplicate_key in seen:
            continue

        seen.add(duplicate_key)
        normalized.append(tag)

    return normalized


class PostCreateRequest(BaseModel):
    """게시글 작성 요청."""

    category: PostCategory = Field(
        description="게시글 카테고리",
        examples=["관광지"],
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="게시글 제목",
        examples=["남산 야경 방문 후기"],
    )

    content: str = Field(
        min_length=1,
        max_length=10000,
        description="게시글 내용",
        examples=["평일 저녁에 방문했는데 야경이 좋았습니다."],
    )

    password: str = Field(
        min_length=4,
        max_length=100,
        description="게시글 수정·삭제용 비밀번호",
        examples=["1234"],
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="사용자가 입력한 자유 태그 목록",
        examples=[["남산", "야경", "데이트"]],
    )

    @field_validator(
        "title",
        "content",
        "password",
        mode="before",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: Any,
    ) -> Any:
        """필수 문자열의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "tags",
        mode="before",
    )
    @classmethod
    def validate_tags(
        cls,
        value: Any,
    ) -> list[str]:
        """태그의 공백과 중복을 정리한다."""

        return normalize_tags(value)

    @field_validator("tags")
    @classmethod
    def validate_tag_count_and_length(
        cls,
        tags: list[str],
    ) -> list[str]:
        """태그 개수와 각 태그 길이를 검사한다."""

        if len(tags) > 5:
            raise ValueError("태그는 최대 5개까지 입력할 수 있습니다.")

        for tag in tags:
            if len(tag) > 15:
                raise ValueError(
                    f"태그는 15자 이하로 입력해야 합니다: {tag}"
                )

        return tags


class PostUpdateRequest(BaseModel):
    """게시글 수정 요청."""

    category: PostCategory = Field(
        description="수정할 게시글 카테고리",
        examples=["관광지"],
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="수정할 게시글 제목",
        examples=["남산 야경 방문 후기 수정"],
    )

    content: str = Field(
        min_length=1,
        max_length=10000,
        description="수정할 게시글 내용",
        examples=["평일 저녁에 방문하는 것을 추천합니다."],
    )

    password: str = Field(
        min_length=4,
        max_length=100,
        description="작성 당시 등록한 비밀번호",
        examples=["1234"],
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="수정할 자유 태그 목록",
        examples=[["남산", "야경", "평일"]],
    )

    @field_validator(
        "title",
        "content",
        "password",
        mode="before",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: Any,
    ) -> Any:
        """필수 문자열의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "tags",
        mode="before",
    )
    @classmethod
    def validate_tags(
        cls,
        value: Any,
    ) -> list[str]:
        """태그의 공백과 중복을 정리한다."""

        return normalize_tags(value)

    @field_validator("tags")
    @classmethod
    def validate_tag_count_and_length(
        cls,
        tags: list[str],
    ) -> list[str]:
        """태그 개수와 각 태그 길이를 검사한다."""

        if len(tags) > 5:
            raise ValueError("태그는 최대 5개까지 입력할 수 있습니다.")

        for tag in tags:
            if len(tag) > 15:
                raise ValueError(
                    f"태그는 15자 이하로 입력해야 합니다: {tag}"
                )

        return tags


class PostDeleteRequest(BaseModel):
    """게시글 삭제 요청."""

    password: str = Field(
        min_length=4,
        max_length=100,
        description="작성 당시 등록한 수정·삭제용 비밀번호",
        examples=["1234"],
    )

    @field_validator(
        "password",
        mode="before",
    )
    @classmethod
    def strip_password(
        cls,
        value: Any,
    ) -> Any:
        """비밀번호의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value


class PostListItemResponse(BaseModel):
    """게시글 목록에서 사용하는 응답."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int = Field(
        description="게시글 ID",
        examples=[1],
    )

    category: str = Field(
        description="게시글 카테고리",
        examples=["관광지"],
    )

    title: str = Field(
        description="게시글 제목",
        examples=["남산 야경 방문 후기"],
    )

    tags: list[str] = Field(
        default_factory=list,
        description="게시글 태그 목록",
        examples=[["남산", "야경", "데이트"]],
    )

    view_count: int = Field(
        ge=0,
        description="게시글 조회수",
        examples=[15],
    )

    created_at: datetime = Field(
        description="게시글 작성 시각",
    )

    updated_at: datetime = Field(
        description="게시글 마지막 수정 시각",
    )

    @field_validator(
        "tags",
        mode="before",
    )
    @classmethod
    def convert_tag_objects(
        cls,
        value: Any,
    ) -> list[str]:
        """
        SQLAlchemy PostTag 객체 목록을 문자열 태그 목록으로 변환한다.
        """

        if value is None:
            return []

        converted: list[str] = []

        for item in value:
            if isinstance(item, str):
                converted.append(item)
                continue

            tag_value = getattr(item, "tag", None)

            if isinstance(tag_value, str):
                converted.append(tag_value)

        return converted


class PostDetailResponse(BaseModel):
    """게시글 상세조회 응답."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int = Field(
        description="게시글 ID",
        examples=[1],
    )

    category: str = Field(
        description="게시글 카테고리",
        examples=["관광지"],
    )

    title: str = Field(
        description="게시글 제목",
        examples=["남산 야경 방문 후기"],
    )

    content: str = Field(
        description="게시글 내용",
        examples=["평일 저녁에 방문했는데 야경이 좋았습니다."],
    )

    tags: list[str] = Field(
        default_factory=list,
        description="게시글 태그 목록",
        examples=[["남산", "야경", "데이트"]],
    )

    view_count: int = Field(
        ge=0,
        description="게시글 조회수",
        examples=[15],
    )

    created_at: datetime = Field(
        description="게시글 작성 시각",
    )

    updated_at: datetime = Field(
        description="게시글 마지막 수정 시각",
    )

    @field_validator(
        "tags",
        mode="before",
    )
    @classmethod
    def convert_tag_objects(
        cls,
        value: Any,
    ) -> list[str]:
        """
        SQLAlchemy PostTag 객체 목록을 문자열 태그 목록으로 변환한다.
        """

        if value is None:
            return []

        converted: list[str] = []

        for item in value:
            if isinstance(item, str):
                converted.append(item)
                continue

            tag_value = getattr(item, "tag", None)

            if isinstance(tag_value, str):
                converted.append(tag_value)

        return converted


class PostListResponse(BaseModel):
    """게시글 목록과 페이지네이션 정보 응답."""

    items: list[PostListItemResponse] = Field(
        default_factory=list,
        description="게시글 목록",
    )

    total: int = Field(
        ge=0,
        description="검색 조건에 해당하는 전체 게시글 수",
        examples=[45],
    )

    page: int = Field(
        ge=1,
        description="현재 페이지 번호",
        examples=[1],
    )

    size: int = Field(
        ge=1,
        description="페이지당 게시글 수",
        examples=[20],
    )

    total_pages: int = Field(
        ge=0,
        description="전체 페이지 수",
        examples=[3],
    )