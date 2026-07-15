"""실행 중인 FastAPI의 POST /api/chat 엔드포인트를 터미널에서 확인한다."""

from __future__ import annotations

import argparse
import json

import httpx


CASES: dict[str, dict[str, object]] = {
    "location": {
        "message": "종로구에 있는 박물관 3곳 추천해줘",
        "history": [],
    },
    "festival": {
        "message": "마포구에서 볼 수 있는 축제나 공연을 알려줘",
        "history": [],
    },
    "festival_date": {
        "message": "이번 주말 마포구 축제 일정 알려줘",
        "history": [],
    },
    "model_restaurant": {
        "message": "강남구에 있는 모범음식점 위치를 알려줘",
        "history": [],
    },
    "post": {
        "message": "남산 야경에 다녀온 사람들이 올린 글을 찾아줘",
        "history": [],
    },
    "weather": {
        "message": "오늘 서울 관광하기 좋은 날씨야?",
        "history": [],
    },
    "general": {
        "message": "LocalHub에서 어떤 정보를 물어볼 수 있어?",
        "history": [],
    },
    "unsupported": {
        "message": "C++ 퀵정렬 코드를 작성해줘",
        "history": [],
    },
    "history": {
        "message": "그중에서 세 곳만 추천해줘",
        "history": [
            {"role": "user", "content": "종로구 박물관을 찾고 있어"},
            {"role": "assistant", "content": "원하는 조건을 더 알려주세요."},
        ],
    },
}


def run_case(base_url: str, case_name: str) -> bool:
    endpoint = f"{base_url.rstrip('/')}/api/chat"
    payload = CASES[case_name]

    print("=" * 80)
    print(f"케이스: {case_name}")
    print(f"POST {endpoint}")
    print("[요청]")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    try:
        response = httpx.post(endpoint, json=payload, timeout=90.0)
    except httpx.RequestError as error:
        print(f"[실패] FastAPI 서버에 연결할 수 없습니다: {error}")
        print("먼저 python -m uvicorn app.main:app --reload 를 실행하세요.")
        return False

    print(f"\n[HTTP 상태] {response.status_code}")

    try:
        body = response.json()
        print(json.dumps(body, ensure_ascii=False, indent=2))
    except ValueError:
        print(response.text)
        return False

    return response.status_code == 200


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--case", choices=sorted(CASES), default="location")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    case_names = list(CASES) if args.all else [args.case]
    results = [run_case(args.base_url, case_name) for case_name in case_names]

    print("\n[요약]")
    print(f"HTTP 200 성공: {sum(results)}/{len(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
