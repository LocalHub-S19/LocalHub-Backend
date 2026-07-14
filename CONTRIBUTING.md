# LocalHub 협업 및 Git 규칙

이 문서는 LocalHub 프로젝트의 브랜치, 커밋, Merge Request 및 협업 규칙을 정의합니다.

프론트엔드와 백엔드 저장소에 동일한 규칙을 적용합니다.

---

## 1. 저장소 구성

LocalHub는 프론트엔드와 백엔드를 별도의 GitLab 저장소로 관리합니다.

```text
LocalHub/
├── LocalHub-Frontend/    # Vue.js 3, Netlify 배포
└── LocalHub-Backend/     # FastAPI, SQLite, Render 배포
```

상위 `LocalHub` 폴더는 두 저장소를 함께 열기 위한 로컬 작업 폴더이며 Git 저장소로 만들지 않습니다.

```text
LocalHub/.git/                    # 생성하지 않음
LocalHub-Frontend/.git/           # 프론트엔드 저장소
LocalHub-Backend/.git/            # 백엔드 저장소
```

---

## 2. 기본 협업 원칙

1. `main` 브랜치에는 직접 Push하지 않습니다.
2. 모든 작업은 기능별 브랜치에서 진행합니다.
3. 작업을 시작하기 전에 `main` 브랜치를 최신 상태로 갱신합니다.
4. 하나의 브랜치에서는 하나의 기능 또는 수정사항만 다룹니다.
5. 하나의 커밋에는 하나의 논리적인 변경을 포함합니다.
6. 작업 완료 후 Merge Request를 통해 `main`에 병합합니다.
7. 다른 담당자의 파일을 수정해야 할 때는 먼저 해당 담당자에게 알립니다.
8. API 요청·응답 형식을 변경할 때는 프론트엔드·백엔드 담당자 모두에게 공유합니다.
9. `.env`, API Key, 비밀번호 등 민감정보는 절대 커밋하지 않습니다.
10. 실행되지 않는 코드나 충돌이 해결되지 않은 상태로 Merge Request를 생성하지 않습니다.

---

## 3. 브랜치 운영 방식

3일 프로젝트이므로 `develop` 브랜치를 별도로 만들지 않습니다.

```text
main
├── feature/*
├── fix/*
├── refactor/*
├── docs/*
├── chore/*
└── deploy/*
```

`main`은 항상 실행 및 배포 가능한 상태를 유지합니다.

---

## 4. 브랜치 이름 규칙

### 기본 형식

```text
type/작업명
```

작업명은 영문 소문자와 하이픈을 사용합니다.

```text
feature/chat-api
feature/festival-calendar
fix/post-password
docs/api-spec
```

### 브랜치 Type

| Type | 용도 |
|---|---|
| `feature` | 새로운 기능 개발 |
| `fix` | 오류 수정 |
| `refactor` | 기능 변화 없는 코드 구조 개선 |
| `docs` | README, API 명세 등 문서 작업 |
| `chore` | 프로젝트 환경설정 및 패키지 관리 |
| `deploy` | Netlify 또는 Render 배포 설정 |
| `test` | 테스트 코드 작성 |

### 백엔드 브랜치 예시

```text
feature/database
feature/location-api
feature/map-api
feature/community-api
feature/festival-api
feature/weather-api
feature/chat-api
fix/chat-empty-response
fix/post-password
docs/api-spec
deploy/render
```

### 프론트엔드 브랜치 예시

```text
feature/common-layout
feature/home-page
feature/place-list
feature/place-map
feature/festival-calendar
feature/weather-card
feature/community-ui
feature/chatbot-ui
fix/mobile-layout
docs/readme
deploy/netlify
```

---

## 5. 작업 시작 방법

### 1단계: `main` 최신화

```bash
git switch main
git pull origin main
```

### 2단계: 기능 브랜치 생성

```bash
git switch -c feature/기능명
```

예시:

```bash
git switch -c feature/chat-api
```

### 3단계: 현재 브랜치 확인

```bash
git branch
git status
```

현재 작업 브랜치 앞에 `*`가 표시되어야 합니다.

```text
* feature/chat-api
  main
```

---

## 6. Commit Message 규칙

### 기본 형식

```text
type(scope): 작업 내용
```

예시:

```text
feat(chat): 챗봇 API 엔드포인트 구현
fix(weather): 외부 날씨 API 오류 처리
docs(readme): 프로젝트 실행 방법 추가
```

`scope`는 변경한 기능이나 영역을 작성합니다. 범위를 특정하기 어려운 경우에는 생략할 수 있습니다.

```text
chore: 프로젝트 초기 환경 설정
```

---

## 7. Commit Type

| Type | 사용 시점 | 예시 |
|---|---|---|
| `feat` | 새로운 기능 추가 | `feat(post): 게시글 작성 API 구현` |
| `fix` | 오류 수정 | `fix(map): 좌표 없는 마커 제외` |
| `refactor` | 동작 변화 없는 구조 개선 | `refactor(chat): 검색 로직 분리` |
| `style` | CSS, UI, 포맷 수정 | `style(home): 날씨 카드 간격 수정` |
| `docs` | README, 명세, 주석 수정 | `docs(api): 챗봇 응답 명세 추가` |
| `chore` | 환경설정, 패키지 변경 | `chore(config): env 예시 추가` |
| `test` | 테스트 추가·수정 | `test(post): 게시글 삭제 테스트 추가` |
| `build` | 빌드 관련 설정 | `build(vite): 배포 빌드 설정 수정` |
| `deploy` | 배포 설정 변경 | `deploy(render): 서버 실행 명령 추가` |
| `perf` | 성능 개선 | `perf(map): 지도 조회 결과 제한` |
| `revert` | 이전 작업 되돌리기 | `revert: 챗봇 응답 형식 변경 취소` |

---

## 8. Scope 권장 목록

### 공통 Scope

| Scope | 대상 |
|---|---|
| `config` | 환경변수 및 프로젝트 설정 |
| `docs` | README, 명세서 |
| `deploy` | 배포 |
| `common` | 공통 모듈 및 컴포넌트 |

### 백엔드 Scope

| Scope | 대상 |
|---|---|
| `db` | SQLite, SQLAlchemy, 데이터 적재 |
| `location` | 서울 지역정보 |
| `map` | 지도 마커 데이터 API |
| `festival` | 축제 일정 API |
| `weather` | 날씨 및 여행 적합도 |
| `post` | 커뮤니티 게시글 |
| `chat` | 챗봇 API |

### 프론트엔드 Scope

| Scope | 대상 |
|---|---|
| `router` | Vue Router |
| `home` | 홈 화면 |
| `location` | 지역정보 목록 및 상세 |
| `map` | 지도 화면 |
| `festival` | 축제 캘린더 |
| `weather` | 날씨 카드 |
| `community` | 커뮤니티 화면 |
| `chat` | 챗봇 UI |

---

## 9. Commit 작성 규칙

1. 작업 내용을 한 줄로 명확하게 작성합니다.
2. 제목 끝에는 마침표를 사용하지 않습니다.
3. 커밋 메시지는 한글로 작성해도 됩니다.
4. `수정`, `작업`, `완료`처럼 내용이 불분명한 표현은 사용하지 않습니다.
5. 하나의 커밋에 서로 관련 없는 기능을 함께 넣지 않습니다.
6. 파일 전체를 무조건 `git add .` 하기 전에 변경 목록을 확인합니다.
7. 실행 가능한 단위로 커밋합니다.
8. 실제 API Key나 비밀번호가 포함되었는지 반드시 확인합니다.

### 좋은 예시

```text
feat(location): 지역정보 목록 조회 API 구현
feat(map): 카테고리별 지도 마커 필터 추가
feat(festival): 월별 축제 캘린더 조회 구현
feat(weather): 서울 현재 날씨 조회 API 구현
feat(chat): 검색 결과 기반 챗봇 답변 구현
fix(post): 비밀번호 불일치 시 게시글 삭제 방지
fix(festival): 종료일이 없는 축제 일정 처리
refactor(chat): 프롬프트 생성 로직 분리
style(home): 메인 화면 반응형 레이아웃 수정
docs(api): 날씨 API 응답 예시 추가
chore(config): 환경변수 예시 파일 생성
deploy(netlify): SPA 리다이렉트 설정 추가
```

### 피해야 할 예시

```text
수정
작업함
완료
최종
진짜 최종
버그 수정
코드 변경
feat: 이것저것 추가
```

---

## 10. Commit 순서

### 변경사항 확인

```bash
git status
git diff
```

### 필요한 파일만 추가

```bash
git add app/routers/chat.py
git add app/schemas/chat.py
```

프론트엔드 예시:

```bash
git add src/components/chatbot
git add src/api/chatApi.js
```

### Commit

```bash
git commit -m "feat(chat): 챗봇 API 엔드포인트 구현"
```

### 원격 브랜치에 Push

```bash
git push -u origin feature/chat-api
```

두 번째 Push부터는 다음 명령만 사용해도 됩니다.

```bash
git push
```

---

## 11. 작업 중 `main` 변경사항 반영

다른 팀원의 코드가 `main`에 병합된 경우 다음 순서로 반영합니다.

현재 작업을 먼저 커밋합니다.

```bash
git status
git add <변경 파일>
git commit -m "feat(chat): 챗봇 요청 스키마 구현"
```

`main`을 최신화합니다.

```bash
git switch main
git pull origin main
```

다시 작업 브랜치로 이동하여 `main`을 병합합니다.

```bash
git switch feature/chat-api
git merge main
```

초보 팀의 혼란을 줄이기 위해 별도 합의가 없다면 `rebase`보다 `merge` 방식을 사용합니다.

---

## 12. Merge Request 규칙

작업이 끝나면 GitLab에서 Merge Request를 생성합니다.

```text
Source branch: feature/기능명
Target branch: main
```

### Merge Request 제목

커밋 메시지와 같은 형식을 사용합니다.

```text
feat(chat): 지역정보 검색 기반 챗봇 구현
```

### Merge Request 설명 양식

```markdown
## 구현 내용

- 구현한 기능 1
- 구현한 기능 2
- 예외 처리 내용

## 변경 파일

- `변경한 파일 경로`
- `변경한 파일 경로`

## 테스트 방법

1. 서버 또는 프론트엔드 실행
2. 테스트할 페이지나 API 접속
3. 정상 응답 확인

## 관련 API

- `GET /api/...`
- `POST /api/...`

## 확인 요청 사항

- 리뷰어가 중점적으로 확인할 내용

## 체크리스트

- [ ] 로컬에서 정상 실행됨
- [ ] 기존 기능이 정상 동작함
- [ ] `.env`와 API Key가 포함되지 않음
- [ ] 불필요한 로그와 주석을 제거함
- [ ] API 변경사항을 팀원에게 공유함
```

---

## 13. Merge 전 확인

Merge Request를 병합하기 전에 다음 내용을 확인합니다.

- 코드가 정상적으로 실행되는가
- Merge 충돌이 없는가
- 기존 기능이 깨지지 않았는가
- 프론트엔드와 백엔드의 API 형식이 일치하는가
- 실제 API Key가 포함되지 않았는가
- 불필요한 `console.log()`와 `print()`가 남아 있지 않은가
- README 또는 API 명세 수정이 필요한가

가능하면 본인이 아닌 팀원 한 명이 확인한 뒤 Merge합니다.

Merge가 완료되면 사용한 기능 브랜치를 삭제합니다.

---

## 14. 충돌 해결 규칙

Merge 충돌이 발생하면 임의로 상대방 코드를 삭제하지 않습니다.

1. 충돌이 발생한 파일의 담당자를 확인합니다.
2. 해당 담당자와 변경 의도를 공유합니다.
3. 두 코드 중 필요한 내용을 함께 반영합니다.
4. 로컬 실행 후 Commit합니다.

```bash
git status
git add <충돌 해결 파일>
git commit -m "fix: merge 충돌 해결"
```

충돌 해결이 어려우면 무리하게 Push하지 않고 팀원에게 공유합니다.

---

## 15. API 변경 협업 규칙

API 경로 또는 요청·응답 형식이 변경되면 다음 내용을 팀원에게 공유합니다.

```text
변경 API:
변경 전:
변경 후:
변경 이유:
프론트엔드 영향:
백엔드 영향:
```

예시:

```text
변경 API: POST /api/chat

변경 전:
{
  "message": "질문"
}

변경 후:
{
  "message": "질문",
  "history": []
}

변경 이유:
대화 히스토리 전달 필요

프론트엔드 영향:
history 배열 추가 필요
```

API 변경사항은 가능하면 코드 수정 전에 합의합니다.

---

## 16. 커밋 금지 파일

다음 파일과 폴더는 Git에 올리지 않습니다.

### 프론트엔드

```text
.env
.env.local
node_modules/
dist/
실제 API Key
```

### 백엔드

```text
.env
.venv/
venv/
__pycache__/
*.db
*.sqlite
*.sqlite3
실제 API Key
```

커밋 전 다음 명령으로 확인합니다.

```bash
git status
```

---

## 17. 민감정보가 추적된 경우

`.gitignore`에 추가했더라도 이미 Git이 추적 중인 파일은 자동으로 제외되지 않습니다.

```bash
git rm --cached .env
git commit -m "chore(config): 환경변수 파일 추적 제외"
```

폴더인 경우:

```bash
git rm -r --cached node_modules
git rm -r --cached .venv
```

실제 API Key가 원격 저장소에 Push됐다면 파일만 삭제하지 않고 해당 Key를 폐기한 뒤 새로 발급합니다.

---

## 18. 담당별 주요 브랜치

### 프론트엔드 담당

```text
feature/common-layout
feature/home-page
feature/place-map
feature/festival-calendar
feature/weather-card
feature/community-ui
feature/chatbot-ui
deploy/netlify
```

### 백엔드 담당

```text
feature/database
feature/location-api
feature/map-api
feature/community-api
feature/festival-api
feature/weather-api
deploy/render
```

### 챗봇 담당

챗봇 기능은 백엔드 저장소에서 작업합니다.

```text
feature/chat-api
```

필요한 경우 프론트 담당자와 협의하여 프론트 저장소에서 다음 브랜치를 사용할 수 있습니다.

```text
feature/chatbot-ui
```

---

## 19. 작업 완료 체크리스트

### 공통

- [ ] `main` 최신 상태에서 브랜치를 생성했는가
- [ ] 기능별 브랜치에서 작업했는가
- [ ] 커밋 메시지 규칙을 지켰는가
- [ ] 로컬에서 정상 실행되는가
- [ ] 민감정보가 포함되지 않았는가
- [ ] Merge Request를 생성했는가

### 프론트엔드

- [ ] 페이지 이동이 정상 동작하는가
- [ ] API 로딩과 오류 상태를 처리했는가
- [ ] 모바일 화면이 깨지지 않는가
- [ ] 새로고침 및 직접 URL 접근이 가능한가

### 백엔드

- [ ] Swagger에서 API를 테스트했는가
- [ ] 성공·실패 상태 코드를 처리했는가
- [ ] DB 데이터가 정상적으로 저장되는가
- [ ] API 응답에 비밀번호가 포함되지 않는가
- [ ] 환경변수 없이 민감정보를 직접 작성하지 않았는가