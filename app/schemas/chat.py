from __future__ import annotations

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
        description="답변 생성에 참고한 지역정보 및 게시글",
    )