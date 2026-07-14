from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["챗봇"],
)


@router.post(
    "",
    response_model=ChatResponse,
    summary="챗봇 질문하기",
    description=(
        "사용자의 질문과 이전 대화 내역을 입력받아 "
        "서울 지역정보와 커뮤니티 게시글을 검색하고 "
        "OpenAI API를 이용해 자연어 답변을 생성합니다."
    ),
    responses={
        422: {
            "description": "입력값 검증 실패",
        },
        502: {
            "description": "OpenAI API 호출 실패",
        },
        503: {
            "description": "OpenAI API 설정 누락 또는 서비스 이용 불가",
        },
    },
)
async def ask_chatbot(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """서울 지역정보와 게시글을 기반으로 챗봇 답변을 생성한다."""

    service = ChatService(db)

    return await service.ask(
        request=request,
    )