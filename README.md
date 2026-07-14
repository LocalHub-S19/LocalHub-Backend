# LocalHub Backend

| [🏠 README](./README.md) | [🤝 협업 및 Git 규칙](./CONTRIBUTING.md) |
|---|---|

서울 공공데이터를 기반으로 지역정보, 익명 커뮤니티, 축제 캘린더, 날씨 및 챗봇 기능을 제공하는 LocalHub의 백엔드 프로젝트입니다.

FastAPI 기반 REST API 서버로 구성되며, SQLAlchemy와 SQLite를 사용하여 데이터를 관리합니다.

---

## 📌 프로젝트 소개

LocalHub는 서울의 관광지, 문화시설, 레포츠, 쇼핑, 숙박, 여행코스, 축제공연행사 정보를 한곳에서 확인할 수 있는 지역정보 공유 서비스입니다.

백엔드는 다음 기능을 담당합니다.

- 서울 지역정보 JSON 데이터 적재 및 조회
- 지도 마커용 위치 데이터 제공
- 축제 일정 조회
- 외부 날씨 API 연동
- 여행 적합도 계산
- 익명 커뮤니티 게시글 CRUD
- OpenAI API 기반 지역정보 챗봇
- SQLite 데이터베이스 관리
- 프론트엔드에서 사용할 REST API 제공

---

## ✨ 주요 기능

### 서울 지역정보

- 관광지
- 문화시설
- 레포츠
- 쇼핑
- 숙박
- 여행코스
- 축제공연행사
- 카테고리별 목록 및 상세 조회
- 제목·주소 기반 검색
- 지도 마커용 좌표 조회

### 익명 커뮤니티

- 게시글 목록 조회
- 게시글 상세 조회
- 게시글 작성
- 게시글 수정
- 게시글 삭제
- 수정용 비밀번호 검증
- 게시글 검색
- 조회수 관리

### 축제 캘린더

- 기간별 축제 일정 조회
- 월별 축제 일정 제공
- 다가오는 축제 목록 제공
- 지역정보 상세 페이지 연결용 콘텐츠 ID 제공

### 날씨 및 여행 적합도

- 서울 현재 날씨 조회
- 기온, 체감온도, 습도, 강수량, 풍속 제공
- 날씨 조건 기반 여행 적합도 계산
- 외부 날씨 API 오류 및 타임아웃 처리
- 불필요한 외부 호출을 줄이기 위한 캐시 적용

### 챗봇

- `POST /api/chat` 엔드포인트 제공
- 서울 지역정보 검색
- 축제 일정 검색
- 커뮤니티 게시글 검색
- 현재 날씨를 활용한 답변
- 검색 결과 기반 OpenAI 응답 생성
- 답변에 활용한 출처 데이터 반환

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| Framework | FastAPI |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite |
| Validation | Pydantic |
| AI | OpenAI API |
| Weather | 외부 날씨 API |
| Deployment | Render |
| IDE | Visual Studio Code |

---

## 📁 프로젝트 구조

> 프로젝트 폴더 구조는 팀 협의 후 확정하여 작성할 예정입니다.

```text

```

---

## ✅ 사전 요구사항

프로젝트 실행 전 다음 프로그램이 설치되어 있어야 합니다.

- Python 3.11 이상 권장
- Git
- Visual Studio Code

설치 여부를 확인합니다.

```sh
python --version
git --version
```

Windows에서 `python` 명령이 동작하지 않는 경우 다음 명령을 사용합니다.

```powershell
py --version
```

---

## 🚀 Project Setup

### 1. 저장소 Clone

```sh
git clone <LocalHub-Backend GitLab URL>
cd LocalHub-Backend
```

---

### 2. Python 가상환경 생성

Windows PowerShell:

```powershell
py -m venv .venv
```

가상환경을 실행합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShell 실행 정책 오류가 발생하는 경우 현재 터미널에만 다음 설정을 적용합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS 또는 Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

가상환경이 정상적으로 활성화되면 터미널 앞에 다음과 같이 표시됩니다.

```text
(.venv)
```

---

### 3. 패키지 설치

```sh
pip install -r requirements.txt
```

필요한 경우 pip를 먼저 업데이트합니다.

```sh
python -m pip install --upgrade pip
```

---

### 4. 환경변수 설정

프로젝트 루트의 `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS 또는 Linux:

```sh
cp .env.example .env
```

`.env` 예시:

```env
APP_NAME=LocalHub API
DATABASE_URL=sqlite:///./localhub.db

OPENAI_API_KEY=
WEATHER_API_KEY=

CORS_ORIGINS=http://localhost:5173
```

실제 API Key는 개인의 `.env` 파일에 입력합니다.

> `.env` 파일은 Git에 올리지 않습니다.  
> 실제 API Key, 인증정보 및 비밀번호를 소스코드에 직접 작성하지 않습니다.

---

## 🔐 환경변수

| 환경변수 | 설명 | 필수 여부 |
|---|---|---:|
| `APP_NAME` | FastAPI 서비스 이름 | 선택 |
| `DATABASE_URL` | SQLite 데이터베이스 경로 | 필수 |
| `OPENAI_API_KEY` | OpenAI API 호출 Key | 필수 |
| `WEATHER_API_KEY` | 외부 날씨 API Key | 필수 |
| `CORS_ORIGINS` | 요청을 허용할 프론트엔드 주소 | 필수 |

로컬 개발 환경의 CORS 주소:

```env
CORS_ORIGINS=http://localhost:5173
```

배포 환경에서는 Netlify URL을 등록합니다.

```env
CORS_ORIGINS=https://프론트엔드-서비스명.netlify.app
```

여러 주소를 허용하는 방식은 백엔드 구현 규칙에 따라 쉼표로 구분할 수 있습니다.

```env
CORS_ORIGINS=http://localhost:5173,https://프론트엔드-서비스명.netlify.app
```

---

## 🗄️ 데이터베이스 설정

LocalHub는 SQLite를 사용합니다.

기본 데이터베이스 주소:

```env
DATABASE_URL=sqlite:///./localhub.db
```

### 데이터베이스 초기화

프로젝트에서 제공하는 초기화 스크립트를 실행합니다.

```sh
python scripts/init_db.py
```

### 서울 지역정보 적재

제공받은 서울 JSON 데이터를 SQLite에 적재합니다.

```sh
python scripts/load_locations.py
```

스크립트 파일명과 실행 방법은 실제 구현에 따라 변경될 수 있습니다.

---

## 📂 원본 데이터

서울 지역정보 원본 JSON은 고객사가 제공한 파일을 사용합니다.

대상 데이터:

```text
서울_관광지.json
서울_레포츠.json
서울_문화시설.json
서울_쇼핑.json
서울_숙박.json
서울_여행코스.json
서울_축제공연행사.json
```

원본 데이터는 임의로 수정하지 않고, 필요한 필드만 SQLite에 적재합니다.

### 주요 데이터 처리 규칙

- `contentid`는 지역정보 고유 식별자로 사용
- `contenttypeid`는 콘텐츠 유형 구분에 사용
- `mapx`는 경도로 변환
- `mapy`는 위도로 변환
- 빈 문자열 주소는 `null` 또는 정보 없음으로 처리
- 빈 이미지 URL은 `null` 또는 기본 이미지로 처리
- 원본 데이터의 등록일과 수정일은 축제 개최일로 사용하지 않음
- 축제 시작일·종료일은 별도의 일정 필드가 확인된 경우에만 사용

---

## ▶️ 개발 서버 실행

다음 명령으로 FastAPI 개발 서버를 실행합니다.

```sh
uvicorn app.main:app --reload
```

또는 프로젝트 설정에 따라 다음 명령을 사용할 수 있습니다.

```sh
fastapi dev app/main.py
```

기본 접속 주소:

```text
API Server: http://localhost:8000
Swagger:    http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
```

서버를 종료하려면 실행 중인 터미널에서 `Ctrl + C`를 입력합니다.

---

## ❤️ Health Check

서버가 정상적으로 실행되는지 확인합니다.

```http
GET /api/health
```

응답 예시:

```json
{
  "status": "ok"
}
```

---

## 📡 주요 API

### 시스템

| 기능 | Method | Endpoint |
|---|---|---|
| 서버 상태 확인 | GET | `/api/health` |

### 지역정보 및 지도

| 기능 | Method | Endpoint |
|---|---|---|
| 지역정보 목록 | GET | `/api/locations` |
| 지도 마커 목록 | GET | `/api/locations/map` |
| 지역정보 상세 | GET | `/api/locations/{content_id}` |

### 축제

| 기능 | Method | Endpoint |
|---|---|---|
| 기간별 축제 일정 | GET | `/api/festivals/calendar` |
| 다가오는 축제 | GET | `/api/festivals/upcoming` |

### 날씨

| 기능 | Method | Endpoint |
|---|---|---|
| 현재 날씨 및 여행 적합도 | GET | `/api/weather/current` |

### 커뮤니티

| 기능 | Method | Endpoint |
|---|---|---|
| 게시글 목록 | GET | `/api/posts` |
| 게시글 작성 | POST | `/api/posts` |
| 게시글 상세 | GET | `/api/posts/{post_id}` |
| 게시글 수정 | PUT | `/api/posts/{post_id}` |
| 게시글 삭제 | DELETE | `/api/posts/{post_id}` |

### 챗봇

| 기능 | Method | Endpoint |
|---|---|---|
| 지역정보 챗봇 | POST | `/api/chat` |

세부 요청 및 응답 형식은 Swagger 또는 별도의 API 명세 문서를 참고합니다.

---

## 💬 챗봇 요청 예시

```http
POST /api/chat
Content-Type: application/json
```

```json
{
  "message": "이번 달 서울 축제를 알려줘",
  "history": []
}
```

응답 예시:

```json
{
  "answer": "이번 달 서울에서 확인할 수 있는 축제는 다음과 같습니다.",
  "sources": [
    {
      "type": "festival",
      "id": "123456",
      "title": "서울 여름 문화축제",
      "category": "축제공연행사",
      "address": "서울특별시 종로구"
    }
  ]
}
```

챗봇은 전체 JSON을 OpenAI API에 직접 전달하지 않고, SQLite에서 관련 데이터를 먼저 조회한 뒤 필요한 결과만 전달합니다.

---

## 🌤️ 여행 적합도

현재 날씨 데이터를 기준으로 여행 적합도 점수를 계산합니다.

주요 판단 기준:

- 현재 기온
- 강수량
- 습도
- 풍속

결과 등급 예시:

| 점수 | 등급 | 설명 |
|---:|---|---|
| 70~100 | 좋음 | 야외 활동에 적합 |
| 40~69 | 보통 | 일부 날씨 요소 주의 |
| 0~39 | 주의 | 실내 일정 권장 |

여행 적합도는 OpenAI가 임의로 생성하지 않고 백엔드의 고정된 규칙으로 계산합니다.

---

## 🧪 테스트

구현한 API는 Swagger에서 우선 테스트합니다.

```text
http://localhost:8000/docs
```

기능별 확인 항목:

- 정상 요청의 응답 형식
- 필수 입력값 누락 처리
- 존재하지 않는 데이터 조회 처리
- 게시글 비밀번호 불일치 처리
- 좌표가 없는 지역정보 처리
- 축제 일정이 없는 기간 처리
- 외부 날씨 API 오류 처리
- OpenAI API 오류 및 타임아웃 처리
- 응답에 게시글 비밀번호가 포함되지 않는지 확인

테스트 코드 실행 명령은 테스트 환경이 구성된 후 작성합니다.

```sh
pytest
```

---

## 🔗 프론트엔드 연결

로컬 개발 환경:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
```

프론트엔드의 `.env`에는 다음 주소를 사용합니다.

```env
VITE_API_BASE_URL=http://localhost:8000
```

배포 환경에서는 Render에서 생성된 백엔드 URL을 사용합니다.

```env
VITE_API_BASE_URL=https://백엔드-서비스명.onrender.com
```

---

## 🤝 협업 규칙

브랜치, 커밋, Merge Request 및 민감정보 관리 규칙은 별도 문서를 참고합니다.

[협업 및 Git 규칙 보기](./CONTRIBUTING.md)

주요 원칙:

- `main` 브랜치에 직접 Push하지 않습니다.
- 기능별 브랜치에서 작업합니다.
- 작업 시작 전 `main`을 최신화합니다.
- 커밋 메시지는 `type(scope): 작업 내용` 형식을 사용합니다.
- 작업 완료 후 Merge Request를 생성합니다.
- `.env`, API Key 및 비밀번호를 커밋하지 않습니다.
- API 요청·응답 형식 변경 전 팀원과 공유합니다.

---

## 🔐 보안 규칙

다음 파일과 정보는 Git에 올리지 않습니다.

```text
.env
.venv/
venv/
__pycache__/
*.db
*.sqlite
*.sqlite3
실제 API Key
비밀번호 및 인증정보
```

커밋 전 반드시 확인합니다.

```sh
git status
```

`.env`가 표시되는 경우 `.gitignore`를 확인합니다.

```gitignore
.env
.env.local
.env.*.local
!.env.example
```

민감정보가 이미 원격 저장소에 Push된 경우 파일만 삭제하지 않고 해당 API Key를 폐기한 뒤 새로 발급해야 합니다.

---

## 🚢 Deployment

백엔드는 Render를 통해 배포합니다.

### Render 기본 설정

| 설정 | 값 |
|---|---|
| Branch | `main` |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Render 환경변수

```text
DATABASE_URL
OPENAI_API_KEY
WEATHER_API_KEY
CORS_ORIGINS
```

실제 값은 Render의 Environment 설정에서 등록하며 Git 저장소에 작성하지 않습니다.

### 배포 후 확인

- Render 서비스 URL 정상 접속
- `/api/health` 정상 응답
- `/docs` 접속 가능 여부
- 지역정보 API 정상 동작
- 게시글 CRUD 정상 동작
- 축제 일정 API 정상 동작
- 날씨 API 정상 동작
- 챗봇 API 정상 동작
- Netlify 프론트엔드에서 CORS 오류 없이 호출되는지 확인

---

## ⚠️ SQLite 배포 주의사항

SQLite는 파일 기반 데이터베이스입니다.

Render 환경이 재시작되거나 다시 배포될 경우 실행 중 추가된 데이터가 유지되지 않을 수 있으므로 다음 사항을 고려합니다.

- 서버 시작 시 DB가 없으면 테이블 자동 생성
- 지역정보 초기 데이터가 없으면 JSON 재적재
- 최종 발표 전 불필요한 재배포 지양
- 제출용 SQLite DB 파일은 별도 산출물로 관리
- 게시글 영구 보존 한계는 기능 명세서에 작성

---

## 👥 Team

| 역할 | 담당자 | 주요 업무 |
|---|---|---|
| Backend |  | FastAPI, SQLite, 지역정보 및 게시글 API |
| Frontend |  | Vue 화면 및 API 연동 |
| Chatbot |  | OpenAI API, 검색 및 프롬프트 |
| PM·문서 |  | 일정, 명세서, 발표 자료 |

---

## 📄 Data Source and License

본 서비스는 한국관광공사 TourAPI 4.0의 서울 지역 데이터를 활용합니다.

```text
데이터 제공기관: 한국관광공사
데이터명: 국문 관광정보 서비스 TourAPI 4.0
수집 지역: 서울
라이선스: 공공누리 제3유형
```

서비스 화면과 기능 명세서에 데이터 출처 및 라이선스를 표시합니다.

외부 날씨 API를 사용하는 경우 다음 내용을 별도로 기록합니다.

```text
날씨 데이터 제공기관
API명
데이터 제공 범위
라이선스 또는 이용 조건
API 조회 시각
```