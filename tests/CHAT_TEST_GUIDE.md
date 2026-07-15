# LocalHub 챗봇 테스트 가이드

## 1. 테스트 대상 기능

1. 요청·응답 검증: 공백 제거, 빈 질문 차단, 대화 히스토리 검증
2. AI 질문 유형 분석: 지역정보, 축제, 모범음식점, 게시글, 날씨, 안내, 미지원 질문
3. SQLite 지역정보 검색: 카테고리·자치구·핵심어·결과 개수
4. 축제 검색: 축제 데이터만 검색하고 실제 일정 필드 부재를 명시
5. 모범음식점 검색: DB에서 `모범` 표시가 확인되는 음식점만 반환
6. 커뮤니티 검색: 제목·본문·카테고리·태그·자치구 표현 검색
7. 경량 RAG 근거 생성: DB 결과를 컨텍스트와 `references`로 변환
8. 보안 확인: 게시글 수정 비밀번호가 컨텍스트나 응답에 포함되지 않음
9. 날씨 연결: WeatherService 결과를 챗봇 근거로 사용
10. FastAPI 통합: 실제 `POST /api/chat` 요청과 응답 확인

## 2. 가장 먼저 실행할 명령

프로젝트 최상위 폴더에서 실행한다.

```bash
python -m compileall app tests
python -m unittest discover -s tests -p "test_chat_*_unit.py" -v
```

이 명령은 OpenAI API와 운영 DB를 사용하지 않는 단위 테스트다.

## 3. 실제 DB 데이터 점검

```bash
python tests/test_chat_data_precheck.py
```

확인할 내용:

- `locations`가 0건이면 JSON 적재가 필요함
- `posts`가 0건이면 게시글 검색 결과는 비어 있음
- 축제 데이터가 0건이면 축제 검색 결과는 비어 있음
- `모범` 표시 데이터가 0건이면 모범음식점 검색 결과는 비어 있음

## 4. AI 질문 유형 분류만 테스트

한 건씩 실행하는 것을 권장한다. 각 실행은 OpenAI API를 1회 사용한다.

```bash
python tests/test_chat_intent_live.py --case location
python tests/test_chat_intent_live.py --case festival
python tests/test_chat_intent_live.py --case model_restaurant
python tests/test_chat_intent_live.py --case post
python tests/test_chat_intent_live.py --case weather
python tests/test_chat_intent_live.py --case general
python tests/test_chat_intent_live.py --case unsupported
```

전체 실행:

```bash
python tests/test_chat_intent_live.py --all
```

## 5. 실제 DB + OpenAI 경량 RAG 테스트

```bash
python tests/test_chat_rag_live.py --case location
python tests/test_chat_rag_live.py --case festival
python tests/test_chat_rag_live.py --case festival_date
python tests/test_chat_rag_live.py --case model_restaurant
python tests/test_chat_rag_live.py --case post
python tests/test_chat_rag_live.py --case weather
python tests/test_chat_rag_live.py --case general
python tests/test_chat_rag_live.py --case unsupported
python tests/test_chat_rag_live.py --case history
```

전체 실행은 OpenAI 호출 횟수가 많으므로 필요할 때만 사용한다.

```bash
python tests/test_chat_rag_live.py --all
```

검색형 질문에서 `references`가 비어 있으면 코드 오류일 수도 있지만, 실제 DB에 일치하는 데이터가 없는 경우도 있다. 먼저 데이터 점검을 실행한다.

## 6. FastAPI 엔드포인트 테스트

첫 번째 터미널:

```bash
python -m uvicorn app.main:app --reload
```

두 번째 터미널:

```bash
python tests/test_chat_api_live.py --case location
python tests/test_chat_api_live.py --case post
python tests/test_chat_api_live.py --case weather
python tests/test_chat_api_live.py --case history
```

전체 API 케이스:

```bash
python tests/test_chat_api_live.py --all
```

## 7. 브라우저·Swagger에서 직접 물어볼 질문

| 기능 | 질문 | 확인할 결과 |
|---|---|---|
| 일반 지역정보 | `종로구에 있는 박물관 3곳 추천해줘` | `references`가 `location`, 종로구·문화시설 결과 |
| 자연어 지역정보 | `아이와 조용히 둘러볼 만한 종로 쪽 전시 공간을 찾아줘` | 정확한 단어가 없어도 `location_search`로 분류 |
| 축제 목록 | `마포구에서 볼 수 있는 축제나 공연을 알려줘` | 축제·공연·행사 데이터만 반환 |
| 축제 일정 제한 | `이번 주말 마포구 축제 일정 알려줘` | 실제 시작일·종료일이 없다는 제한 안내 |
| 모범음식점 | `강남구에 있는 모범음식점 위치를 알려줘` | `모범` 표시가 확인된 장소만 반환 |
| 의미 기반 모범음식점 | `공공기관이 모범으로 지정한 믿을 만한 식당을 찾고 있어` | `model_restaurant_search`로 분류 |
| 게시글 | `남산 야경에 다녀온 사람들이 올린 글을 찾아줘` | `references`가 `post`, 제목·본문·태그 검색 |
| 의미 기반 게시글 | `경복궁에 대해 다른 이용자들이 뭐라고 했는지 보여줘` | `post_search`로 분류 |
| 날씨 | `오늘 서울 관광하기 좋은 날씨야?` | 현재 날씨와 여행 적합도 안내 |
| 기능 안내 | `LocalHub에서 어떤 정보를 물어볼 수 있어?` | 지원 기능 안내, DB 결과를 만들지 않음 |
| 미지원 질문 | `C++ 퀵정렬 코드를 작성해줘` | LocalHub 지원 범위 안내 |
| 히스토리 | 이전 질문 `종로구 박물관을 찾고 있어`, 현재 질문 `그중 세 곳만 추천해줘` | 이전 대화 조건을 반영 |
| 결과 없음 | `서울에서 존재하지않는장소XYZ 찾아줘` | 일반 지식으로 만들지 않고 검색 실패 안내 |

## 8. 성공 기준

- 검색형 답변의 장소명·게시글 제목이 `references`와 일치함
- 검색 결과가 없을 때 존재하지 않는 장소를 임의로 만들지 않음
- 축제 날짜 필드가 없는데 날짜를 단정하지 않음
- 일반 음식점을 모범음식점으로 바꾸어 안내하지 않음
- 게시글의 `edit_password`가 터미널 로그·답변·references에 나타나지 않음
- `history`를 포함한 후속 질문이 앞선 대화 조건을 반영함