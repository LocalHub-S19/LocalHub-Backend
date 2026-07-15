"""실제 OpenAI API로 자연어 질문 유형 분류만 확인하는 수동 테스트."""

from __future__ import annotations

import argparse
import asyncio

from openai import AsyncOpenAI

from app.core.config import settings
from app.db.database import SessionLocal
from app.services.chat_service import ChatService


CASES: dict[str, tuple[str, str]] = {
    "location": (
        "종로 쪽에서 아이랑 가기 좋은 박물관 세 곳만 골라줘",
        "location_search",
    ),
    "festival": (
        "이번 주말 마포에서 볼 만한 행사 있어?",
        "festival_search",
    ),
    "model_restaurant": (
        "강남에서 공공기관이 모범으로 지정한 믿을 만한 식당 위치를 찾고 있어",
        "model_restaurant_search",
    ),
    "post": (
        "남산에 다녀온 사람들이 뭐라고 썼는지 찾아봐",
        "post_search",
    ),
    "weather": (
        "오늘 서울에서 우산 없이 돌아다녀도 괜찮을까?",
        "weather",
    ),
    "general": (
        "여기서 어떤 정보를 물어볼 수 있어?",
        "general",
    ),
    "unsupported": (
        "파이썬 정렬 알고리즘을 설명해줘",
        "unsupported",
    ),
}


async def run_case(case_name: str) -> bool:
    question, expected_intent = CASES[case_name]
    db = SessionLocal()

    try:
        service = ChatService(db)
        conversation_text = f"사용자: {question}"

        async with AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=60.0,
        ) as client:
            analysis = await service._analyze_query(
                client=client,
                conversation_text=conversation_text,
                current_message=question,
            )

        passed = analysis.intent == expected_intent
        print("=" * 70)
        print(f"케이스: {case_name}")
        print(f"질문: {question}")
        print(f"예상 intent: {expected_intent}")
        print(f"실제 intent: {analysis.intent}")
        print(analysis.model_dump_json(indent=2))
        print(f"결과: {'PASS' if passed else 'FAIL'}")
        return passed

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
    print(f"통과: {sum(results)}/{len(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
