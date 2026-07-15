"""ChatService의 대화 구성·분류 예비 처리·근거 생성 단위 테스트."""

from __future__ import annotations

import unittest
from datetime import datetime
import sys
import types

# 테스트 실행 환경에 openai 패키지가 없을 때만 최소 스텁을 사용한다.
# 실제 프로젝트의 .venv에 openai가 설치되어 있으면 이 코드는 실행되지 않는다.
try:
    import openai  # noqa: F401
except ModuleNotFoundError:
    openai_stub = types.ModuleType("openai")

    class _OpenAIError(Exception):
        pass

    class AsyncOpenAI:  # pragma: no cover - 단위 테스트에서는 호출하지 않음
        pass

    openai_stub.APIConnectionError = _OpenAIError
    openai_stub.APIStatusError = _OpenAIError
    openai_stub.AsyncOpenAI = AsyncOpenAI
    openai_stub.AuthenticationError = _OpenAIError
    openai_stub.RateLimitError = _OpenAIError
    sys.modules["openai"] = openai_stub

from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

from app.db.models.location import Location
from app.db.models.post import Post
from app.schemas.chat import ChatMessage, ChatRequest
from app.schemas.chat_intent import ChatIntentAnalysis
from app.schemas.weather import WeatherResponse
from app.services.chat_service import ChatService
from app.services.weather_service import WeatherService
from tests.chat_test_support import create_test_session, seed_chat_test_data


class ChatServiceUnitTest(unittest.IsolatedAsyncioTestCase):
    """OpenAI를 호출하지 않고 경량 RAG 내부 로직을 확인한다."""

    def setUp(self) -> None:
        self.db, self.engine = create_test_session()
        seed_chat_test_data(self.db)
        self.service = ChatService(self.db)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_build_conversation_text_keeps_history_order(self) -> None:
        request = ChatRequest(
            message="그중 세 곳만 알려줘",
            history=[
                ChatMessage(role="user", content="종로구 박물관을 찾고 있어"),
                ChatMessage(role="assistant", content="원하는 조건이 있나요?"),
            ],
        )

        text = self.service._build_conversation_text(request)

        self.assertEqual(
            text,
            "사용자: 종로구 박물관을 찾고 있어\n"
            "챗봇: 원하는 조건이 있나요?\n"
            "사용자: 그중 세 곳만 알려줘",
        )

    def test_fallback_analysis_classifies_major_intents(self) -> None:
        cases = {
            "종로구 박물관 추천해줘": "location_search",
            "이번 주말 마포구 축제 알려줘": "festival_search",
            "강남구 모범 한식당 알려줘": "model_restaurant_search",
            "남산에 다녀온 사람들이 쓴 글 찾아줘": "post_search",
            "오늘 서울 날씨 어때": "weather",
            "여기서 뭘 할 수 있어": "general",
        }

        for question, expected_intent in cases.items():
            with self.subTest(question=question):
                result = self.service._fallback_analysis(question)
                self.assertEqual(result.intent, expected_intent)

    def test_location_grounding_creates_reference(self) -> None:
        location = self.db.get(Location, "loc-museum-1")
        self.assertIsNotNone(location)

        grounding = self.service._build_location_grounding(
            [location],
            heading="[테스트 지역정보]",
        )

        self.assertIn("서울역사박물관", grounding.context)
        self.assertEqual(len(grounding.references), 1)
        reference = grounding.references[0]
        self.assertEqual(reference.type, "location")
        self.assertEqual(reference.id, "loc-museum-1")
        self.assertEqual(reference.address, "서울특별시 종로구 새문안로 55")

    def test_post_grounding_excludes_edit_password(self) -> None:
        post = self.db.query(Post).filter(Post.title == "남산 야경 방문 후기").one()

        grounding = self.service._build_post_grounding([post])

        self.assertIn("남산 야경 방문 후기", grounding.context)
        self.assertNotIn("test-password-1", grounding.context)
        self.assertEqual(grounding.references[0].type, "post")
        self.assertCountEqual(grounding.references[0].tags, ["남산", "야경"])

    async def test_retrieve_grounding_routes_location_festival_restaurant_and_post(self) -> None:
        analyses = [
            ChatIntentAnalysis(
                intent="location_search",
                district="종로구",
                category="문화시설",
                keywords=["박물관"],
                date_expression=None,
                limit=5,
                reason="문화시설 검색",
            ),
            ChatIntentAnalysis(
                intent="festival_search",
                district="영등포구",
                category=None,
                keywords=["한강"],
                date_expression="이번 주말",
                limit=5,
                reason="축제 검색",
            ),
            ChatIntentAnalysis(
                intent="model_restaurant_search",
                district="종로구",
                category=None,
                keywords=["한식"],
                date_expression=None,
                limit=5,
                reason="모범음식점 검색",
            ),
            ChatIntentAnalysis(
                intent="post_search",
                district=None,
                category=None,
                keywords=["남산"],
                date_expression=None,
                limit=5,
                reason="게시글 검색",
            ),
        ]

        expected_types = ["location", "location", "location", "post"]

        for analysis, expected_type in zip(analyses, expected_types, strict=True):
            with self.subTest(intent=analysis.intent):
                grounding = await self.service._retrieve_grounding(analysis)
                self.assertGreater(len(grounding.references), 0)
                self.assertEqual(grounding.references[0].type, expected_type)

        festival_grounding = await self.service._retrieve_grounding(analyses[1])
        self.assertIn("시작일", festival_grounding.limitation or "")
        self.assertIn("종료일", festival_grounding.limitation or "")

    async def test_weather_grounding_uses_weather_service(self) -> None:
        fake_weather = WeatherResponse(
            region="서울",
            observed_at=datetime(2026, 7, 15, 10, 0, tzinfo=ZoneInfo("Asia/Seoul")),
            temperature=25.0,
            feels_like=26.0,
            humidity=60,
            precipitation=0.0,
            wind_speed=2.0,
            weather_condition="맑음",
            travel_score=90,
            travel_grade="매우 좋음",
            recommendation="야외 관광과 산책을 즐기기 좋은 날씨입니다.",
        )
        analysis = ChatIntentAnalysis(
            intent="weather",
            district=None,
            category=None,
            keywords=[],
            date_expression=None,
            limit=5,
            reason="현재 날씨 질문",
        )

        with patch.object(
            WeatherService,
            "get_current_weather",
            new=AsyncMock(return_value=fake_weather),
        ):
            grounding = await self.service._retrieve_grounding(analysis)

        self.assertIn("기온: 25.0℃", grounding.context)
        self.assertIn("여행 적합도: 90점", grounding.context)
        self.assertEqual(grounding.references, [])

    def test_empty_and_unsupported_responses_do_not_invent_data(self) -> None:
        empty_analysis = ChatIntentAnalysis(
            intent="post_search",
            district=None,
            category=None,
            keywords=["존재하지않는검색어"],
            date_expression=None,
            limit=5,
            reason="게시글 검색",
        )
        empty_response = self.service._empty_search_response(empty_analysis)
        unsupported = self.service._unsupported_response()

        self.assertIsNotNone(empty_response)
        self.assertEqual(empty_response.references, [])
        self.assertIn("찾지 못했습니다", empty_response.answer)
        self.assertEqual(unsupported.references, [])
        self.assertIn("LocalHub", unsupported.answer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
