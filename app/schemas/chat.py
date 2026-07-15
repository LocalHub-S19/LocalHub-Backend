"""
[수정 파일] 챗봇 요청·응답 스키마

변경 사항
1. [유지] 기존 message, history, answer, references 구조
2. [유지] 참고 장소의 전화번호·좌표 필드
3. [추가] 참고 장소의 대표 이미지 URL 필드
4. [유지] 참고 게시글의 본문 요약·태그·작성 시각 필드
5. [유지] 기존 프론트엔드가 사용하던 type, id, title,
   category, address 필드는 그대로 유지
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


ChatRole = Literal[
    "user",
    "assistant",
]


ChatReferenceType = Literal[
    "location",
    "post",
]


class ChatMessage(BaseModel):
    """챗봇 이전 대화 메시지."""

    role: ChatRole = Field(
        description="메시지 작성 주체",
        examples=["user"],
    )

    content: str = Field(
        min_length=1,
        max_length=2000,
        description="이전 대화 메시지 내용",
        examples=["비 오는 날 가기 좋은 곳을 찾고 있어"],
    )

    @field_validator(
        "content",
        mode="before",
    )
    @classmethod
    def strip_content(
        cls,
        value: object,
    ) -> object:
        """대화 메시지의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value


class ChatRequest(BaseModel):
    """챗봇 질문 요청."""

    message: str = Field(
        min_length=1,
        max_length=1000,
        description="현재 사용자의 질문",
        examples=["서울에서 비 오는 날 가기 좋은 문화시설을 추천해줘"],
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
        description="이전 대화 내역",
    )

    @field_validator(
        "message",
        mode="before",
    )
    @classmethod
    def strip_message(
        cls,
        value: object,
    ) -> object:
        """현재 질문의 앞뒤 공백을 제거한다."""

        if isinstance(value, str):
            return value.strip()

        return value


class ChatReference(BaseModel):
    """챗봇 답변 생성에 참고한 지역정보 또는 게시글."""

    type: ChatReferenceType = Field(
        description="참고 데이터 유형",
        examples=["location"],
    )

    id: str = Field(
        description="지역정보 콘텐츠 ID 또는 게시글 ID",
        examples=["126508"],
    )

    title: str = Field(
        description="참고 데이터 제목",
        examples=["서울역사박물관"],
    )

    category: str | None = Field(
        default=None,
        description="지역정보 또는 게시글 카테고리",
        examples=["문화시설"],
    )

    address: str | None = Field(
        default=None,
        description="지역정보의 주소",
        examples=["서울특별시 종로구 새문안로 55"],
    )

    # [추가] 장소 검색 결과를 프론트에서 바로 활용할 수 있는 정보
    tel: str | None = Field(
        default=None,
        description="지역정보의 전화번호",
        examples=["02-1234-5678"],
    )

    # [추가] 챗봇 장소 카드에 표시할 대표 이미지 URL
    image_url: str | None = Field(
        default=None,
        description="지역정보의 대표 이미지 또는 썸네일 URL",
        examples=["https://tong.visitkorea.or.kr/cms/resource/..."],
    )

    latitude: float | None = Field(
        default=None,
        description="지역정보의 위도",
        examples=[37.5704],
    )

    longitude: float | None = Field(
        default=None,
        description="지역정보의 경도",
        examples=[126.9779],
    )

    # [추가] 게시글 검색 결과를 프론트에서 보여줄 때 사용하는 정보
    snippet: str | None = Field(
        default=None,
        description="게시글 본문 일부",
        examples=["평일 저녁에 방문했는데 야경이 좋았습니다."],
    )

    tags: list[str] = Field(
        default_factory=list,
        description="게시글에 연결된 태그 목록",
        examples=[["남산", "야경"]],
    )

    created_at: datetime | None = Field(
        default=None,
        description="게시글 작성 시각",
    )


class ChatResponse(BaseModel):
    """챗봇 답변 응답."""

    answer: str = Field(
        description="OpenAI API가 생성한 자연어 답변",
        examples=[
            "비 오는 날에는 서울역사박물관과 국립중앙박물관을 추천합니다."
        ],
    )

    references: list[ChatReference] = Field(
        default_factory=list,
        description="답변 생성에 실제로 참고한 지역정보 및 게시글",
    )