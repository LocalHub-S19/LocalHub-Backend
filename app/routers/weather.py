from fastapi import APIRouter

from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherService


router = APIRouter(
    prefix="/weather",
    tags=["날씨"],
)


@router.get(
    "/current",
    response_model=WeatherResponse,
    summary="서울 현재 날씨 조회",
    description=(
        "서울의 현재 기온, 체감온도, 습도, 강수량, 풍속과 "
        "여행 적합도를 조회합니다."
    ),
    responses={
        502: {
            "description": "외부 날씨 API 호출 실패",
        },
        503: {
            "description": "날씨 API 설정 누락 또는 서비스 이용 불가",
        },
    },
)
async def get_current_weather() -> WeatherResponse:
    """서울의 현재 날씨와 여행 적합도를 반환한다."""

    service = WeatherService()

    return await service.get_current_weather()