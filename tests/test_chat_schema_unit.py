"""챗봇 요청 및 질문 분석 스키마 단위 테스트."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.schemas.chat import ChatMessage, ChatRequest
from app.schemas.chat_intent import ChatIntentAnalysis


class ChatSchemaUnitTest(unittest.TestCase):
    """Pydantic 검증·정규화 동작을 확인한다."""

    def test_chat_request_strips_whitespace(self) -> None:
        request = ChatRequest(
            message="  종로구 박물관 추천해줘  ",
            history=[
                ChatMessage(
                    role="user",
                    content="  아이와 갈 곳을 찾고 있어  ",
                )
            ],
        )

        self.assertEqual(request.message, "종로구 박물관 추천해줘")
        self.assertEqual(request.history[0].content, "아이와 갈 곳을 찾고 있어")

    def test_chat_request_rejects_empty_message(self) -> None:
        with self.assertRaises(ValidationError):
            ChatRequest(message="   ", history=[])

    def test_district_and_keywords_are_normalized(self) -> None:
        analysis = ChatIntentAnalysis(
            intent="location_search",
            district="서울 종로",
            category="문화시설",
            keywords=[
                " 추천 ",
                "박물관",
                "박물관",
                "종로구",
                "아이",
            ],
            date_expression="이번 주말",
            limit=3,
            reason="  문화시설 검색 요청  ",
        )

        self.assertEqual(analysis.district, "종로구")
        self.assertEqual(analysis.category, "문화시설")
        self.assertEqual(analysis.keywords, ["박물관", "아이"])
        self.assertIsNone(analysis.date_expression)
        self.assertEqual(analysis.reason, "문화시설 검색 요청")

    def test_unknown_district_is_removed(self) -> None:
        analysis = ChatIntentAnalysis(
            intent="location_search",
            district="수원시",
            category="관광지",
            keywords=[],
            date_expression=None,
            limit=5,
            reason="서울 외 지역",
        )

        self.assertIsNone(analysis.district)

    def test_festival_intent_forces_category_and_keeps_date(self) -> None:
        analysis = ChatIntentAnalysis(
            intent="festival_search",
            district="마포",
            category=None,
            keywords=["재즈"],
            date_expression="이번 주말",
            limit=5,
            reason="축제 일정 질문",
        )

        self.assertEqual(analysis.district, "마포구")
        self.assertEqual(analysis.category, "축제공연행사")
        self.assertEqual(analysis.date_expression, "이번 주말")

    def test_model_restaurant_intent_forces_food_category(self) -> None:
        analysis = ChatIntentAnalysis(
            intent="model_restaurant_search",
            district="강남구",
            category=None,
            keywords=["한식"],
            date_expression=None,
            limit=5,
            reason="모범음식점 질문",
        )

        self.assertEqual(analysis.category, "음식점")

    def test_weather_clears_search_category_and_date(self) -> None:
        analysis = ChatIntentAnalysis(
            intent="weather",
            district="종로구",
            category="관광지",
            keywords=["산책"],
            date_expression="오늘",
            limit=5,
            reason="현재 날씨 질문",
        )

        self.assertIsNone(analysis.category)
        self.assertIsNone(analysis.date_expression)

    def test_extra_field_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ChatIntentAnalysis.model_validate(
                {
                    "intent": "general",
                    "district": None,
                    "category": None,
                    "keywords": [],
                    "date_expression": None,
                    "limit": 5,
                    "reason": "기능 안내",
                    "sql": "SELECT * FROM locations",
                }
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
