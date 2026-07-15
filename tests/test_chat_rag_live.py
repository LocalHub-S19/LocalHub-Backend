"""실제 DB와 OpenAI API를 사용해 ChatService 전체 흐름을 확인한다."""

from __future__ import annotations

import argparse
import asyncio

from app.core.config import settings
from app.db.database import SessionLocal
from app.schemas.chat import ChatMessage, ChatRequest
from app.services.chat_service import ChatService


CASES: dict[str, ChatRequest] = {
    "location": ChatRequest(
        message="종로구에 있는 박물관 3곳 추천해줘",
        history=[],
    ),
    "festival": ChatRequest(
        message="마포구에서 볼 수 있는 축제나 공연을 알려줘",
        history=[],
    ),
    "festival_date": ChatRequest(
        message="이번 주말 마포구 축제 일정 알려줘",
        history=[],
    ),
    "model_restaurant": ChatRequest(
        message="강남구에 있는 모범음식점 위치를 알려줘",
        history=[],
    ),
    "post": ChatRequest(
        message="남산 야경에 다녀온 사람들이 올린 글을 찾아줘",
        history=[],
    ),
    "weather": ChatRequest(
        message="오늘 서울 관광하기 좋은 날씨야?",
        history=[],
    ),
    "general": ChatRequest(
        message="LocalHub에서 어떤 정보를 물어볼 수 있어?",
        history=[],
    ),
    "unsupported": ChatRequest(
        message="C++ 퀵정렬 코드를 작성해줘",
        history=[],
    ),
    "history": ChatRequest(
        message="그중에서 세 곳만 추천해줘",
        history=[
            ChatMessage(role="user", content="종로구 박물관을 찾고 있어"),
            ChatMessage(role="assistant", content="원하는 조건을 더 알려주세요."),
        ],
    ),
}


async def run_case(case_name: str) -> bool:
    request = CASES[case_name]
    db = SessionLocal()

    try:
        service = ChatService(db)
        response = await service.ask(request)

        print("=" * 80)
        print(f"케이스: {case_name}")
        print(f"질문: {request.message}")
        print("\n[답변]")
        print(response.answer)
        print(f"\n[references 개수] {len(response.references)}")

        for index, reference in enumerate(response.references, start=1):
            print(f"{index}. {reference.model_dump_json()}")

        search_cases = {
            "location",
            "festival",
            "festival_date",
            "model_restaurant",
            "post",
            "history",
        }

        if case_name in search_cases and not response.references:
            print("[주의] 검색 결과가 없습니다. 데이터 점검 스크립트를 먼저 실행하세요.")
            return True

        if case_name == "post":
            type_ok = all(ref.type == "post" for ref in response.references)
        elif case_name in {"location", "festival", "festival_date", "model_restaurant", "history"}:
            type_ok = all(ref.type == "location" for ref in response.references)
        else:
            return bool(response.answer.strip())

        mentioned_titles = [
            ref.title for ref in response.references if ref.title in response.answer
        ]
        if not mentioned_titles:
            print("[주의] 답변 본문에서 reference 제목을 찾지 못했습니다. 직접 확인하세요.")

        if case_name == "festival_date" and not any(
            word in response.answer
            for word in ("일정", "시작일", "종료일", "확인", "제공 데이터")
        ):
            print("[주의] 축제 날짜 필드 부재에 대한 제한 안내가 명확하지 않습니다.")

        return type_ok

    finally:
        db.close()


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES), default="location")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if not settings.openai_api_key:
        print("[실패] .env의 OPENAI_API_KEY를 확인하세요.")
        return 1

    case_names = list(CASES) if args.all else [args.case]
    results = [await run_case(case_name) for case_name in case_names]

    print("\n[요약]")
    print(f"실행 성공: {sum(results)}/{len(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
