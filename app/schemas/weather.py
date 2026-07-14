from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TravelGrade = Literal[
    "매우 좋음",
    "좋음",
    "보통",
    "주의",
    "나쁨",
]


class WeatherResponse(BaseModel):
    """서울 현재 날씨 및 여행 적합도 응답."""

    region: str = Field(
        default="서울",
        description="날씨 조회 지역",
        examples=["서울"],
    )

    observed_at: datetime = Field(
        description="날씨 관측 또는 조회 시각",
    )

    temperature: float = Field(
        description="현재 기온, 섭씨",
        examples=[26.4],
    )

    feels_like: float | None = Field(
        default=None,
        description="체감온도, 섭씨",
        examples=[27.1],
    )

    humidity: int = Field(
        ge=0,
        le=100,
        description="현재 습도, 퍼센트",
        examples=[65],
    )

    precipitation: float = Field(
        ge=0,
        description="현재 강수량 또는 최근 1시간 강수량, mm",
        examples=[0.0],
    )

    wind_speed: float = Field(
        ge=0,
        description="현재 풍속, m/s",
        examples=[2.1],
    )

    weather_condition: str = Field(
        description="현재 날씨 상태",
        examples=["맑음"],
    )

    travel_score: int = Field(
        ge=0,
        le=100,
        description="현재 날씨 기반 여행 적합도 점수",
        examples=[85],
    )

    travel_grade: TravelGrade = Field(
        description="여행 적합도 등급",
        examples=["매우 좋음"],
    )

    recommendation: str = Field(
        description="현재 날씨에 따른 여행 안내 문구",
        examples=["야외 관광을 즐기기 좋은 날씨입니다."],
    )