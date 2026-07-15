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
        """DB 세션을 저장한다."""

        self.db = db

    @staticmethod
    def _build_conversation_text(
        request: ChatRequest,
    ) -> str:
        """이전 대화와 현재 질문을 하나의 문자열로 구성한다."""

        conversation_lines: list[str] = []

        for history_message in request.history:
            if history_message.role == "user":
                role_name = "사용자"
            else:
                role_name = "챗봇"

            conversation_lines.append(
                f"{role_name}: {history_message.content}"
            )

        conversation_lines.append(
            f"사용자: {request.message}"
        )

        return "\n".join(conversation_lines)

    @staticmethod
    def _extract_output_text(response: object) -> str:
        """
        Responses API 응답에서 텍스트를 추출한다.

        일반적으로 response.output_text를 사용하고,
        값이 비어 있으면 response.output 내부를 다시 확인한다.
        """

        output_text = getattr(
            response,
            "output_text",
            "",
        )

        if isinstance(output_text, str):
            output_text = output_text.strip()

            if output_text:
                return output_text

        output_items = getattr(
            response,
            "output",
            [],
        )

        extracted_texts: list[str] = []

        for output_item in output_items:
            item_type = getattr(
                output_item,
                "type",
                None,
            )

            if item_type != "message":
                continue

            contents = getattr(
                output_item,
                "content",
                [],
            )

            for content_item in contents:
                content_type = getattr(
                    content_item,
                    "type",
                    None,
                )

                text = getattr(
                    content_item,
                    "text",
                    None,
                )

                if (
                    content_type == "output_text"
                    and isinstance(text, str)
                    and text.strip()
                ):
                    extracted_texts.append(
                        text.strip()
                    )

        return "\n".join(extracted_texts)

    @staticmethod
    def _print_response_debug(
        response: object,
    ) -> None:
        """개발 중 OpenAI 응답 상태를 터미널에 출력한다."""

        response_status = getattr(
            response,
            "status",
            None,
        )

        incomplete_details = getattr(
            response,
            "incomplete_details",
            None,
        )

        usage = getattr(
            response,
            "usage",
            None,
        )

        output_items = getattr(
            response,
            "output",
            [],
        )

        output_types = [
            getattr(item, "type", "unknown")
            for item in output_items
        ]

        print()
        print("[OpenAI 응답 확인]")
        print(f"status: {response_status}")
        print(
            f"incomplete_details: "
            f"{incomplete_details}"
        )
        print(f"output types: {output_types}")
        print(f"usage: {usage}")
        print()

    async def ask(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """사용자의 질문에 대한 챗봇 답변을 생성한다."""

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

        conversation_text = self._build_conversation_text(
            request=request,
        )

        try:
            async with AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=60.0,
            ) as client:
                response = await client.responses.create(
                    model=settings.openai_model,
                    instructions=(
                        "당신은 서울 지역정보 서비스 LocalHub의 "
                        "한국어 챗봇입니다. "
                        "사용자의 질문에 친절하고 간결하게 답변하세요. "
                        "현재는 API 연결 테스트 단계이므로 "
                        "일반적인 서울 관광정보를 안내하세요. "
                        "확실하지 않은 정보는 임의로 만들어내지 말고 "
                        "확인하기 어렵다고 설명하세요. "
                        "반드시 사용자에게 보여줄 최종 답변을 작성하세요."
                    ),
                    input=conversation_text,

                    # GPT-5 mini의 추론 토큰 사용량을 줄인다.
                    reasoning={
                        "effort": "low",
                    },

                    # 추론 토큰과 실제 출력 토큰이 함께 포함된다.
                    max_output_tokens=2000,
                )

            self._print_response_debug(
                response=response,
            )

            response_status = getattr(
                response,
                "status",
                None,
            )

            incomplete_details = getattr(
                response,
                "incomplete_details",
                None,
            )

            if response_status == "incomplete":
                incomplete_reason = getattr(
                    incomplete_details,
                    "reason",
                    "unknown",
                )

                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "OpenAI 응답 생성이 완료되지 않았습니다. "
                        f"원인: {incomplete_reason}"
                    ),
                )

            answer = self._extract_output_text(
                response=response,
            )

            if not answer:
                output_types = [
                    getattr(item, "type", "unknown")
                    for item in getattr(
                        response,
                        "output",
                        [],
                    )
                ]

                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "OpenAI API 응답에서 최종 텍스트를 "
                        "찾지 못했습니다. "
                        f"응답 상태: {response_status}, "
                        f"출력 유형: {output_types}"
                    ),
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
                    f"오류가 발생했습니다: "
                    f"{type(error).__name__}"
                ),
            ) from error