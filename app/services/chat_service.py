from __future__ import annotations

from fastapi import HTTPException, status
from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """OpenAI API를 이용해 챗봇 답변을 생성하는 서비스."""

    def __init__(self, db: Session) -> None:
        """
        ChatService를 초기화한다.

        현재 단계에서는 DB 세션을 보관만 한다.
        이후 서울 지역정보와 게시글 검색에 사용한다.
        """

        self.db = db

    async def ask(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """사용자의 질문과 이전 대화 내역을 이용해 답변을 생성한다."""

        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPENAI_API_KEY가 설정되지 않았습니다.",
            )

        if not settings.openai_model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPENAI_MODEL이 설정되지 않았습니다.",
            )

        conversation_lines: list[str] = []

        for message in request.history:
            if message.role == "user":
                role_name = "사용자"
            else:
                role_name = "챗봇"

            conversation_lines.append(
                f"{role_name}: {message.content}"
            )

        conversation_lines.append(
            f"사용자: {request.message}"
        )

        conversation_text = "\n".join(
            conversation_lines
        )

        try:
            async with AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=30.0,
            ) as client:
                response = await client.responses.create(
                    model=settings.openai_model,
                    instructions=(
                        "당신은 서울 지역정보 서비스 LocalHub의 챗봇입니다. "
                        "사용자의 질문에 한국어로 친절하고 간결하게 답변하세요. "
                        "현재는 OpenAI API 연결 테스트 단계입니다. "
                        "확실하지 않은 정보는 임의로 만들어내지 말고 "
                        "확인하기 어렵다고 설명하세요."
                    ),
                    input=conversation_text,
                    max_output_tokens=800,
                )

            answer = response.output_text.strip()

            if not answer:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="OpenAI API 응답 내용이 비어 있습니다.",
                )

            return ChatResponse(
                answer=answer,
                references=[],
            )

        except AuthenticationError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API 키 인증에 실패했습니다.",
            ) from error

        except RateLimitError as error:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "OpenAI API 요청 한도를 초과했거나 "
                    "사용 가능한 API 잔액이 없습니다."
                ),
            ) from error

        except APIConnectionError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OpenAI API 서버에 연결하지 못했습니다.",
            ) from error

        except APIStatusError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "OpenAI API 호출에 실패했습니다. "
                    f"상태 코드: {error.status_code}"
                ),
            ) from error

        except HTTPException:
            raise

        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "챗봇 응답 생성 중 예상하지 못한 "
                    f"오류가 발생했습니다: {type(error).__name__}"
                ),
            ) from error