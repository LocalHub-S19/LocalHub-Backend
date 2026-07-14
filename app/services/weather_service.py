from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.weather import WeatherResponse


class WeatherService:
    """Open-Meteo를 이용해 서울 현재 날씨를 조회한다."""

    SEOUL_LATITUDE = 37.5665
    SEOUL_LONGITUDE = 126.9780
    SEOUL_TIMEZONE = ZoneInfo("Asia/Seoul")

    @staticmethod
    def _require_number(
        data: dict,
        key: str,
    ) -> float:
        """응답 데이터에서 필수 숫자 값을 가져온다."""

        value = data.get(key)

        if isinstance(value, bool):
            raise ValueError(
                f"{key} 값이 올바른 숫자가 아닙니다."
            )

        if isinstance(value, (int, float)):
            return float(value)

        raise ValueError(
            f"Open-Meteo 응답에 {key} 값이 없습니다."
        )

    @staticmethod
    def _parse_observed_at(
        value: object,
    ) -> datetime:
        """Open-Meteo의 관측 시각 문자열을 datetime으로 변환한다."""

        if not isinstance(value, str):
            raise ValueError(
                "Open-Meteo 응답에 관측 시각이 없습니다."
            )

        observed_at = datetime.fromisoformat(
            value
        )

        # timezone=Asia/Seoul 요청 시 반환되는 시각에
        # timezone 정보가 없을 수 있으므로 한국 시간대를 설정한다.
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(
                tzinfo=WeatherService.SEOUL_TIMEZONE
            )

        return observed_at

    @staticmethod
    def _weather_condition(
        weather_code: int,
    ) -> str:
        """WMO 날씨 코드를 한글 설명으로 변환한다."""

        condition_map: dict[int, str] = {
            0: "맑음",
            1: "대체로 맑음",
            2: "부분적으로 흐림",
            3: "흐림",
            45: "안개",
            48: "서리 안개",
            51: "약한 이슬비",
            53: "이슬비",
            55: "강한 이슬비",
            56: "약한 어는 이슬비",
            57: "강한 어는 이슬비",
            61: "약한 비",
            63: "비",
            65: "강한 비",
            66: "약한 어는 비",
            67: "강한 어는 비",
            71: "약한 눈",
            73: "눈",
            75: "강한 눈",
            77: "싸락눈",
            80: "약한 소나기",
            81: "소나기",
            82: "강한 소나기",
            85: "약한 눈 소나기",
            86: "강한 눈 소나기",
            95: "뇌우",
            96: "약한 우박을 동반한 뇌우",
            99: "강한 우박을 동반한 뇌우",
        }

        return condition_map.get(
            weather_code,
            "알 수 없음",
        )

    @staticmethod
    def _calculate_travel_score(
        temperature: float,
        humidity: int,
        precipitation: float,
        wind_speed: float,
        weather_code: int,
    ) -> int:
        """
        현재 날씨를 기준으로 여행 적합도 점수를 계산한다.

        이 점수는 LocalHub에서 자체적으로 정한 안내용 지표다.
        """

        score = 100

        # 기온
        if temperature < -5 or temperature > 35:
            score -= 35
        elif temperature < 5 or temperature > 30:
            score -= 20
        elif temperature < 10 or temperature > 28:
            score -= 10

        # 강수량
        if precipitation >= 10:
            score -= 40
        elif precipitation >= 3:
            score -= 30
        elif precipitation > 0:
            score -= 15

        # 풍속
        if wind_speed >= 14:
            score -= 30
        elif wind_speed >= 8:
            score -= 15

        # 습도
        if humidity >= 90:
            score -= 10
        elif humidity >= 80:
            score -= 5

        # 날씨 현상
        if weather_code in {95, 96, 99}:
            score -= 30
        elif weather_code in {
            65,
            67,
            75,
            82,
            86,
        }:
            score -= 20
        elif weather_code in {
            45,
            48,
            51,
            53,
            55,
            56,
            57,
            61,
            63,
            66,
            71,
            73,
            77,
            80,
            81,
            85,
        }:
            score -= 10

        return max(
            0,
            min(100, score),
        )

    @staticmethod
    def _travel_grade(
        score: int,
    ) -> str:
        """점수를 여행 적합도 등급으로 변환한다."""

        if score >= 85:
            return "매우 좋음"

        if score >= 70:
            return "좋음"

        if score >= 50:
            return "보통"

        if score >= 30:
            return "주의"

        return "나쁨"

    @staticmethod
    def _recommendation(
        grade: str,
        precipitation: float,
        weather_code: int,
    ) -> str:
        """여행 적합도에 따른 안내 문구를 생성한다."""

        if weather_code in {95, 96, 99}:
            return (
                "뇌우 가능성이 있어 야외 활동을 피하고 "
                "실내 관광지를 이용하는 것이 좋습니다."
            )

        if precipitation > 0:
            return (
                "비가 내리고 있어 우산을 준비하고 "
                "박물관·미술관 등 실내 관광지를 추천합니다."
            )

        if grade == "매우 좋음":
            return (
                "야외 관광과 산책을 즐기기 좋은 날씨입니다."
            )

        if grade == "좋음":
            return (
                "전반적으로 관광하기 좋은 날씨입니다."
            )

        if grade == "보통":
            return (
                "관광은 가능하지만 기온과 바람을 확인하고 "
                "외출 준비를 하는 것이 좋습니다."
            )

        if grade == "주의":
            return (
                "야외 활동 시 주의가 필요하며 "
                "실내 관광지도 함께 고려해주세요."
            )

        return (
            "야외 관광에 적합하지 않은 날씨입니다. "
            "가능하면 실내 활동을 추천합니다."
        )

    async def get_current_weather(
        self,
    ) -> WeatherResponse:
        """서울 현재 날씨와 여행 적합도를 반환한다."""

        if not settings.weather_api_base_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WEATHER_API_BASE_URL이 설정되지 않았습니다.",
            )

        params = {
            "latitude": self.SEOUL_LATITUDE,
            "longitude": self.SEOUL_LONGITUDE,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "timezone": "Asia/Seoul",
            "forecast_days": 1,
        }

        try:
            async with httpx.AsyncClient(
                timeout=10.0,
            ) as client:
                response = await client.get(
                    settings.weather_api_base_url,
                    params=params,
                )

                response.raise_for_status()

                payload = response.json()

        except httpx.TimeoutException as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="날씨 API 응답 시간이 초과되었습니다.",
            ) from error

        except httpx.HTTPStatusError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "날씨 API가 오류를 반환했습니다. "
                    f"상태 코드: {error.response.status_code}"
                ),
            ) from error

        except httpx.RequestError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="날씨 API 서버에 연결하지 못했습니다.",
            ) from error

        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="날씨 API 응답을 JSON으로 해석하지 못했습니다.",
            ) from error

        try:
            current = payload.get("current")

            if not isinstance(current, dict):
                raise ValueError(
                    "Open-Meteo 응답에 current 데이터가 없습니다."
                )

            observed_at = self._parse_observed_at(
                current.get("time")
            )

            temperature = self._require_number(
                current,
                "temperature_2m",
            )

            feels_like = self._require_number(
                current,
                "apparent_temperature",
            )

            humidity = int(
                round(
                    self._require_number(
                        current,
                        "relative_humidity_2m",
                    )
                )
            )

            precipitation = self._require_number(
                current,
                "precipitation",
            )

            wind_speed = self._require_number(
                current,
                "wind_speed_10m",
            )

            weather_code = int(
                round(
                    self._require_number(
                        current,
                        "weather_code",
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"날씨 API 응답 형식이 올바르지 않습니다: {error}",
            ) from error

        weather_condition = self._weather_condition(
            weather_code
        )

        travel_score = self._calculate_travel_score(
            temperature=temperature,
            humidity=humidity,
            precipitation=precipitation,
            wind_speed=wind_speed,
            weather_code=weather_code,
        )

        travel_grade = self._travel_grade(
            travel_score
        )

        recommendation = self._recommendation(
            grade=travel_grade,
            precipitation=precipitation,
            weather_code=weather_code,
        )

        return WeatherResponse(
            region=settings.target_region,
            observed_at=observed_at,
            temperature=temperature,
            feels_like=feels_like,
            humidity=humidity,
            precipitation=max(0.0, precipitation),
            wind_speed=max(0.0, wind_speed),
            weather_condition=weather_condition,
            travel_score=travel_score,
            travel_grade=travel_grade,
            recommendation=recommendation,
        )