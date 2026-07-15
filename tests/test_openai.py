from __future__ import annotations

import sys
from pathlib import Path

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.core.config import settings


def main() -> int:
    """OpenAI API 연결과 모델 응답을 확인한다."""

    if not settings.openai_api_key:
        print("[실패] OPENAI_API_KEY가 설정되지 않았습니다.")
        print("프로젝트 루트의 .env 파일을 확인해주세요.")
        return 1

    if not settings.openai_model:
        print("[실패] OPENAI_MODEL이 설정되지 않았습니다.")
        return 1

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=30.0,
    )

    try:
        response = client.responses.create(
            model=settings.openai_model,
            instructions=(
                "당신은 서울 지역정보 서비스 LocalHub의 챗봇입니다. "
                "현재는 API 연결 테스트 중입니다. "
                "답변은 한국어로 간단하게 작성하세요."
            ),
            input="연결 테스트입니다. 서울 쇼핑지 중 한 곳을 예시로 말해주세요.",
            max_output_tokens=300,
        )

        answer = response.output_text.strip()

        if not answer:
            print("[실패] API 요청은 성공했지만 응답 텍스트가 비어 있습니다.")
            return 1

        print("[성공] OpenAI API 연결 성공")
        print(f"사용 모델: {settings.openai_model}")
        print()
        print("[응답]")
        print(answer)

        return 0

    except AuthenticationError:
        print("[실패] OpenAI API 키 인증에 실패했습니다.")
        print("OPENAI_API_KEY가 올바른지 확인해주세요.")
        return 1

    except RateLimitError as error:
        print("[실패] 요청 한도 또는 API 잔액 문제가 발생했습니다.")
        print(f"오류: {error}")
        return 1

    except APIConnectionError as error:
        print("[실패] OpenAI 서버에 연결하지 못했습니다.")
        print(f"오류: {error}")
        return 1

    except APIStatusError as error:
        print("[실패] OpenAI API가 오류 상태를 반환했습니다.")
        print(f"상태 코드: {error.status_code}")
        print(f"오류: {error}")
        return 1

    except Exception as error:
        print("[실패] 예상하지 못한 오류가 발생했습니다.")
        print(f"오류 유형: {type(error).__name__}")
        print(f"오류 내용: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())