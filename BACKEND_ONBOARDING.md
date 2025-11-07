# HWP Report Generator - 백엔드 온보딩

본 문서는 FastAPI 기반 백엔드(core: backend/)의 구조, 실행, API, 데이터 모델, 개발 가이드, 테스트, 트러블슈팅을 최신 v2(채팅 기반 보고서 생성 플로우)에 맞추어 정리한 온보딩 문서입니다. 기존 v1(단일 요청으로 HWPX 생성) 경로는 호환을 위해 유지되지만 신규 개발은 v2 중심으로 진행합니다.

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [아키텍처 개요](#아키텍처-개요)
4. [프로젝트 구조](#프로젝트-구조)
5. [개발 환경 설정](#개발-환경-설정)
6. [환경 변수 설정](#환경-변수-설정)
7. [데이터베이스 스키마](#데이터베이스-스키마)
8. [표준 API 응답 규격](#표준-api-응답-규격)
9. [핵심 API 설계](#핵심-api-설계)
10. [보고서 생성 프로세스](#보고서-생성-프로세스)
11. [주요 컴포넌트](#주요-컴포넌트)
12. [테스트 가이드](#테스트-가이드)
13. [개발 가이드라인](#개발-가이드라인)
14. [트러블슈팅](#트러블슈팅)

---

## 프로젝트 개요

HWP Report Generator는 사용자가 주제를 입력하면 Claude API를 활용해 금융 보고서(요약/배경/주요내용/결론)를 Markdown으로 생성하고, 필요 시 HWPX로 변환/다운로드하도록 지원하는 시스템입니다.

### 핵심 기능

- 사용자 인증 및 권한 관리 (JWT 기반)
- **대화형 보고서 생성** - 주제(Topic) 기반 채팅 시스템
- Claude AI를 활용한 보고서 내용 생성 (Markdown 형식)
- Markdown → HWPX 파일 변환
- 아티팩트(Artifact) 관리 - 생성된 파일 추적 및 버전 관리
- AI 사용량 추적 (메시지별)
- 관리자 대시보드

### 비즈니스 플로우

**v2.0 (대화형 시스템 - 현재):**

1. 사용자가 Topic(대화 주제) 생성
2. 사용자가 메시지를 입력하여 Claude AI와 대화
3. Claude API가 Markdown 형식의 보고서 내용 생성
4. Markdown 파일이 아티팩트로 저장 (버전 관리)
5. 사용자 요청 시 Markdown → HWPX 변환
6. 변환된 HWPX 파일 다운로드 제공
7. AI 사용량 데이터 자동 추적

**v1.0 (단일 요청 시스템 - Deprecated):**

1. 사용자가 보고서 주제 입력
2. Claude API가 구조화된 보고서 내용 생성
3. HWP Handler가 HWPX 템플릿의 XML을 수정하여 내용 삽입
4. 생성된 HWPX 파일을 다운로드 제공

⚠️ **v1.0 API는 Deprecated되었으며 향후 제거 예정입니다. 신규 개발은 v2.0 API를 사용하세요.**

---

## 기술 스택

### 백엔드 프레임워크
- **FastAPI** 0.104.1 - 고성능 비동기 웹 프레임워크
- **Uvicorn** 0.24.0 - ASGI 서버
- **Python** 3.12+

### 데이터베이스
- **SQLite** - 경량 관계형 데이터베이스
- 파일 위치: `backend/data/hwp_reports.db`

### AI/ML
- **Anthropic Claude API** (`anthropic==0.71.0`)
- 모델: `claude-sonnet-4-5-20250929`

### 인증/보안
- **python-jose[cryptography]** 3.3.0 - JWT 토큰 생성/검증
- **passlib[bcrypt]** 1.7.4 - 비밀번호 해싱

### 파일 처리
- **olefile** 0.47 - OLE 파일 형식 처리
- **zipfile** (표준 라이브러리) - HWPX 압축/해제

### 기타
- **Pydantic** 2.5.0+ - 데이터 검증 및 설정 관리
- **python-dotenv** 1.0.0 - 환경 변수 관리
- **aiofiles** 23.2.1 - 비동기 파일 I/O

---

## 아키텍처 개요

### 계층 구조

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI Routes)     │
│   auth, topics, messages, artifacts │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Business Logic Layer            │
│  ClaudeClient, HWPHandler, Auth    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Data Access Layer (Database)    │
│  user_db, topic_db, message_db, etc│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│          SQLite Database            │
│         hwp_reports.db              │
└─────────────────────────────────────┘
```

### 데이터 플로우 (v2)

1. 사용자가 Topic 생성 또는 Ask 호출로 입력
2. 컨텍스트 구성(이전 메시지, 선택한/최신 MD Artifact 내용 포함)
3. Claude chat completion 호출 → Assistant 답변(MD)
4. 메시지/AI 사용량/Artifact(MD) 기록 → 필요 시 MD→HWPX 변환 아티팩트 추가

---

## 프로젝트 구조

```
hwp-report-generator/
├── backend/                         # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py                 # FastAPI 앱 엔트리, 라우터 등록, 초기화
│   │   ├── routers/                # API 라우트 핸들러
│   │   │   ├── auth.py            # 인증 API (회원가입, 로그인, 로그아웃)
│   │   │   ├── admin.py           # 관리자 API (사용자 관리, 통계)
│   │   │   ├── topics.py          # ✨ 주제 API (생성, 조회, 수정, 삭제, ask)
│   │   │   ├── messages.py        # ✨ 메시지 API (생성, 조회)
│   │   │   ├── artifacts.py       # ✨ 아티팩트 API (조회, 다운로드, 변환)
│   │   │   └── reports.py         # 보고서 API (Deprecated)
│   │   ├── models/                # Pydantic 모델
│   │   │   ├── user.py            # 사용자 모델
│   │   │   ├── topic.py           # ✨ 주제 모델
│   │   │   ├── message.py         # ✨ 메시지 모델
│   │   │   ├── artifact.py        # ✨ 아티팩트 모델
│   │   │   ├── ai_usage.py        # ✨ AI 사용량 모델
│   │   │   ├── transformation.py  # ✨ 변환 추적 모델 (MD→HWPX 등)
│   │   │   ├── token_usage.py     # 토큰 사용량 모델 (Deprecated)
│   │   │   └── report.py          # 보고서 모델 (Deprecated)
│   │   ├── database/              # 데이터베이스 레이어
│   │   │   ├── connection.py     # DB 연결 및 초기화
│   │   │   ├── user_db.py         # 사용자 CRUD
│   │   │   ├── topic_db.py        # ✨ 주제 CRUD
│   │   │   ├── message_db.py      # ✨ 메시지 CRUD
│   │   │   ├── artifact_db.py     # ✨ 아티팩트 CRUD
│   │   │   ├── ai_usage_db.py     # ✨ AI 사용량 CRUD
│   │   │   ├── transformation_db.py # ✨ 변환 추적 CRUD
│   │   │   ├── token_usage_db.py  # 토큰 사용량 CRUD (Deprecated)
│   │   │   └── report_db.py       # 보고서 CRUD (Deprecated)
│   │   └── utils/                 # 유틸리티 함수
│   │       ├── response_helper.py # ✨ API 표준 응답 헬퍼
│   │       ├── prompts.py         # ✨ 시스템 프롬프트 중앙 관리 (v2.1)
│   │       ├── claude_client.py   # Claude API 클라이언트
│   │       ├── hwp_handler.py     # HWPX 파일 처리
│   │       ├── artifact_manager.py # ✨ 아티팩트 파일 저장/관리 추상화
│   │       ├── md_handler.py      # ✨ Markdown 파일 처리 유틸
│   │       ├── markdown_parser.py # ✨ Markdown 파싱 (동적 섹션 추출)
│   │       ├── markdown_builder.py# ✨ Markdown 생성
│   │       ├── file_utils.py      # ✨ 파일/버전 유틸
│   │       └── auth.py            # JWT 인증 및 비밀번호 해싱
│   ├── templates/                 # HWPX 템플릿
│   │   └── report_template.hwpx
│   ├── artifacts/                 # ✨ 생성된 파일 저장 (MD, HWPX)
│   │   └── topics/                # 주제별 디렉토리
│   ├── output/                    # 레거시 보고서 저장 (Deprecated)
│   ├── temp/                      # 임시 파일
│   ├── data/                      # SQLite 데이터베이스
│   │   └── hwp_reports.db
│   ├── doc/                       # ✨ 개발 문서
│   │   ├── 01.대화형(채팅)서비스 전환을 위한 도메인구조변경.md
│   │   ├── 02.generateTopic.md
│   │   ├── 03.hwpxDownload.md
│   │   ├── 04.messageChaining.md
│   │   ├── 05.downloadApi.md
│   │   ├── 06.WebSearchAPI.md    # ✨ 웹 검색 API 설계 (v2.1)
│   │   └── 07.PromptIntegrate.md # ✨ 프롬프트 통합 가이드 (v2.1)
│   ├── tests/                     # ✨ 테스트 파일
│   │   ├── conftest.py            # pytest fixtures
│   │   ├── test_routers_*.py      # API 테스트
│   │   └── test_utils_*.py        # 유틸리티 테스트
│   ├── requirements.txt           # 프로덕션 의존성
│   ├── requirements-dev.txt       # ✨ 개발/테스트 의존성
│   ├── pytest.ini                 # ✨ pytest 설정
│   ├── init_db.py                 # DB 초기화 스크립트
│   ├── migrate_db.py              # DB 마이그레이션 스크립트
│   ├── BACKEND_TEST.md            # ✨ 테스트 상세 가이드
│   ├── MIGRATION_GUIDE.md         # ✨ v1 → v2 마이그레이션 가이드
│   ├── CLAUDE.md                  # ✨ 백엔드 개발 가이드라인
│   └── .env                       # 환경 변수
│
├── shared/                        # ✨ 공유 모듈
│   ├── models/                    # 공유 데이터 모델
│   │   └── api_response.py       # API 응답 표준 모델
│   ├── types/                     # 공유 타입
│   │   └── enums.py              # MessageRole, ArtifactKind, TransformOperation 등
│   ├── constants.py               # 공유 상수 (Python)
│   ├── constants.ts               # 공유 상수 (TypeScript)
│   ├── constants.properties       # 공유 상수 원본
│   └── README.md                  # 공유 상수 사용 가이드
│
├── CLAUDE.md                      # 프로젝트 전체 문서
├── BACKEND_ONBOARDING.md          # 이 문서
└── README.md                      # 프로젝트 README
```

**✨ 표시**: v2.0에서 새로 추가된 파일/디렉토리

### 참고 문서
- CLAUDE 개요: `CLAUDE.md`, `backend/CLAUDE.md`
- 메시지 체이닝 설계: `backend/doc/04.messageChaining.md`
- 테스트 가이드: `backend/BACKEND_TEST.md`

---

## 개발 환경 설정

### 사전 요구사항

- Python 3.12+
- uv (권장) 또는 pip
- Git

### 저장소 클론

```bash
git clone <repository-url>
cd hwp-report-generator
```

### 가상환경 및 패키지 설치

**uv 사용 (권장):**
```bash
cd backend
uv venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

uv pip install -r requirements.txt
```

**pip 사용:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 데이터베이스 초기화

```bash
cd backend
uv run python init_db.py
```

이 스크립트는:
- `data/` 디렉토리 생성
- SQLite 데이터베이스 생성
- 테이블 및 인덱스 생성
- 관리자 계정 생성

### 개발 서버 실행

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 접속 확인

- 메인: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 중요: PATH_PROJECT_HOME 설정

⚠️ **`PATH_PROJECT_HOME` 환경 변수가 설정되지 않으면 서버가 시작되지 않습니다.**

`.env` 파일에 프로젝트 루트의 절대 경로를 반드시 지정하세요.

---

## 환경 변수 설정

`backend/.env` 파일 생성:

```env
# Claude API 설정
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# JWT 인증 설정
JWT_SECRET_KEY=your-secret-key-change-this-to-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 관리자 계정 설정
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123!@#
ADMIN_USERNAME=관리자

# 프로젝트 루트 (반드시 실제 경로로 설정)
PATH_PROJECT_HOME=D:\\WorkSpace\\hwp-report\\hwp-report-generator
```

### 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 않습니다
- `JWT_SECRET_KEY`는 안전한 랜덤 문자열로 변경하세요
- 프로덕션 환경에서는 강력한 비밀번호를 사용하세요

---

## 데이터베이스 스키마

### ERD (v2.0)

```
┌────────────────────┐
│      users         │
├────────────────────┤
│ id (PK)            │◄──────────────┐
│ email (UNIQUE)     │               │
│ username           │               │
│ hashed_password    │               │
│ is_active          │               │
│ is_admin           │               │
│ password_reset_req │               │
│ created_at         │               │
│ updated_at         │               │
└────────────────────┘               │
                                     │
         ┌───────────────────────────┘
         │
         ▼
┌────────────────────┐         ┌────────────────────┐
│      topics        │         │     messages       │
├────────────────────┤         ├────────────────────┤
│ id (PK)            │◄───┐    │ id (PK)            │
│ user_id (FK)       │    │    │ topic_id (FK)      │
│ input_prompt       │    └────│ role               │
│ generated_title    │         │ content            │
│ language           │         │ seq_no             │
│ status             │    ┌────│ created_at         │
│ created_at         │    │    └────────────────────┘
│ updated_at         │    │             │
└────────────────────┘    │             │
         │                │             ▼
         │                │    ┌────────────────────┐
         │                │    │    ai_usage        │
         │                │    ├────────────────────┤
         │                └───►│ id (PK)            │
         │                     │ topic_id (FK)      │
         │                     │ message_id (FK)    │
         │                     │ model              │
         │                     │ input_tokens       │
         │                     │ output_tokens      │
         │                     │ total_tokens       │
         │                     │ latency_ms         │
         │                     │ created_at         │
         │                     └────────────────────┘
         │
         ▼
┌────────────────────┐         ┌────────────────────────┐
│     artifacts      │         │   transformations      │
├────────────────────┤         ├────────────────────────┤
│ id (PK)            │◄───┐    │ id (PK)                │
│ topic_id (FK)      │    ├────│ from_artifact_id (FK)  │
│ message_id (FK)    │    └────│ to_artifact_id (FK)    │
│ kind               │         │ operation              │
│ locale             │         │ params_json            │
│ version            │         │ created_at             │
│ filename           │         └────────────────────────┘
│ file_path          │
│ file_size          │
│ sha256             │
│ created_at         │
└────────────────────┘
```

### 테이블 상세

#### users - 사용자 계정

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 사용자 고유 ID |
| email | TEXT | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| username | TEXT | NOT NULL | 사용자 이름 |
| hashed_password | TEXT | NOT NULL | 해시된 비밀번호 |
| is_active | BOOLEAN | DEFAULT 0 | 활성화 여부 (관리자 승인) |
| is_admin | BOOLEAN | DEFAULT 0 | 관리자 권한 |
| password_reset_required | BOOLEAN | DEFAULT 0 | 비밀번호 재설정 필요 |
| created_at | TIMESTAMP | DEFAULT NOW | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT NOW | 수정 시각 |

#### topics - 대화 주제 (v2.0)

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 주제 고유 ID |
| user_id | INTEGER | FK, NOT NULL | 생성자 사용자 ID |
| input_prompt | TEXT | NOT NULL | 초기 주제/프롬프트 |
| generated_title | TEXT | NULL | AI 생성 대화 제목 |
| language | TEXT | DEFAULT 'ko' | 언어 코드 |
| status | TEXT | DEFAULT 'active' | active/archived/deleted |
| created_at | TIMESTAMP | DEFAULT NOW | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT NOW | 수정 시각 |

#### messages - 대화 메시지 (v2.0)

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 메시지 고유 ID |
| topic_id | INTEGER | FK, NOT NULL | 메시지가 속한 주제 ID |
| role | TEXT | NOT NULL | user/assistant/system |
| content | TEXT | NOT NULL | 메시지 내용 |
| seq_no | INTEGER | NOT NULL | 주제 내 순번 (0부터) |
| created_at | TIMESTAMP | DEFAULT NOW | 생성 시각 |

**제약 조건:** UNIQUE (topic_id, seq_no)

#### artifacts - 생성 파일 (v2.0)

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 아티팩트 고유 ID |
| topic_id | INTEGER | FK, NOT NULL | 주제 ID |
| message_id | INTEGER | FK, NOT NULL | 생성한 메시지 ID |
| kind | TEXT | NOT NULL | md/hwpx |
| locale | TEXT | DEFAULT 'ko' | 파일 언어 |
| version | INTEGER | DEFAULT 1 | 파일 버전 |
| filename | TEXT | NOT NULL | 파일명 |
| file_path | TEXT | NOT NULL | 파일 경로 |
| file_size | INTEGER | DEFAULT 0 | 파일 크기 (바이트) |
| sha256 | TEXT | NULL | 파일 해시 (무결성 검증) |
| created_at | TIMESTAMP | DEFAULT NOW | 생성 시각 |

#### ai_usage - AI 사용량 (v2.0)

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 사용량 기록 ID |
| topic_id | INTEGER | FK, NOT NULL | 주제 ID |
| message_id | INTEGER | FK, NOT NULL | 메시지 ID |
| model | TEXT | NOT NULL | 사용된 AI 모델명 |
| input_tokens | INTEGER | DEFAULT 0 | 입력 토큰 수 |
| output_tokens | INTEGER | DEFAULT 0 | 출력 토큰 수 |
| total_tokens | INTEGER | DEFAULT 0 | 총 토큰 수 |
| latency_ms | INTEGER | DEFAULT 0 | API 응답 시간 (ms) |
| created_at | TIMESTAMP | DEFAULT NOW | 기록 시각 |

#### transformations - 파일 변환 추적 (v2.0)

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 변환 기록 ID |
| from_artifact_id | INTEGER | FK, NOT NULL | 원본 아티팩트 ID |
| to_artifact_id | INTEGER | FK, NOT NULL | 변환 결과 아티팩트 ID |
| operation | TEXT | NOT NULL | convert/translate |
| params_json | TEXT | NULL | 변환 파라미터 (JSON) |
| created_at | TIMESTAMP | DEFAULT NOW | 변환 시각 |

**인덱스:**
- `idx_transformations_from` - from_artifact_id
- `idx_transformations_to` - to_artifact_id

**사용 사례:**
- MD → HWPX 변환 이력 추적
- 향후 언어 번역 이력 추적 (KO → EN)
- 변환 체인 추적 (MD → HWPX → PDF)

#### reports, token_usage - 레거시 (Deprecated)

v1.0 호환성 유지를 위해 존재하며 향후 제거 예정입니다.

스키마/인덱스는 `backend/app/database/connection.py` 초기화 로직을 참고하세요.

---

## 표준 API 응답 규격

v2.0부터 모든 API 엔드포인트는 표준화된 응답 형식을 따릅니다.

### Success Response

```json
{
  "success": true,
  "data": { /* 실제 데이터 */ },
  "error": null,
  "meta": { "requestId": "uuid" },
  "feedback": []
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DOMAIN.DETAIL",
    "httpStatus": 404,
    "message": "에러 메시지",
    "details": { /* 추가 정보 */ },
    "traceId": "uuid",
    "hint": "해결 방법"
  },
  "meta": { "requestId": "uuid" },
  "feedback": []
}
```

### 주요 필드

- `success`: 요청 성공/실패 여부
- `data`: 실제 응답 데이터 (실패 시 null)
- `error`: 에러 상세 정보 (성공 시 null)
- `meta.requestId`: 요청 추적용 UUID
- `error.traceId`: 에러 추적용 UUID
- `feedback`: 선택적 사용자 피드백 배열

### 구현

**헬퍼 함수** (`utils/response_helper.py`):
```python
from app.utils.response_helper import success_response, error_response, ErrorCode

# 성공 응답
return success_response({
    "id": 123,
    "name": "example"
})

# 에러 응답
return error_response(
    code=ErrorCode.TOPIC_NOT_FOUND,
    http_status=404,
    message="토픽을 찾을 수 없습니다.",
    hint="토픽 ID를 확인해주세요."
)
```

자세한 내용은 프로젝트 루트의 `CLAUDE.md` 파일의 "API Response Standard" 섹션을 참조하세요.

---

## 핵심 API 설계

### 인증 API (`/api/auth`)

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인 (JWT 발급)
- `GET /api/auth/me` - 내 정보 조회
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/change-password` - 비밀번호 변경

### 주제 API (`/api/topics`) - v2.0

- `POST /api/topics` - 토픽 생성
- `POST /api/topics/generate` - 입력 한 번에 MD 산출 (토픽/메시지/아티팩트 동시 생성)
- `GET /api/topics` - 내 토픽 목록 (페이징)
- `GET /api/topics/{topic_id}` - 단건 조회
- `PATCH /api/topics/{topic_id}` - 수정 (제목/상태)
- `DELETE /api/topics/{topic_id}` - 삭제
- `POST /api/topics/{topic_id}/ask` - 메시지 체이닝 (컨텍스트 기반 답변 + MD 아티팩트)

### 메시지 API (`/api/topics/{topic_id}/messages`) - v2.0

- `POST /api/topics/{topic_id}/messages` - 메시지 생성
- `GET /api/topics/{topic_id}/messages` - 메시지 목록
- `GET /api/topics/{topic_id}/messages/{message_id}` - 메시지 단건

### 아티팩트 API (`/api/artifacts`) - v2.0

- `GET /api/artifacts/{artifact_id}` - 메타 조회
- `GET /api/artifacts/{artifact_id}/content` - 내용 조회 (MD만)
- `GET /api/artifacts/{artifact_id}/download` - 파일 다운로드 (MD/HWPX)
- `POST /api/artifacts/{artifact_id}/convert` - MD → HWPX 변환
- `GET /api/artifacts/messages/{message_id}/hwpx/download` - 메시지 기반 HWPX 다운로드 (필요 시 자동 변환)

### 관리자 API (`/api/admin`)

- `GET /api/admin/users` - 사용자 목록
- `POST /api/admin/users/{user_id}/approve` - 사용자 승인
- `POST /api/admin/users/{user_id}/reject` - 사용자 거부
- `POST /api/admin/users/{user_id}/reset-password` - 비밀번호 초기화
- `GET /api/admin/token-usage` - 전체 토큰 사용량
- `GET /api/admin/token-usage/{user_id}` - 사용자별 토큰 사용량

### 레거시 보고서 API (`/api/reports`) - Deprecated

- `POST /api/reports/generate` - HWPX 생성 (단일 요청)
- `GET /api/reports/my-reports` - 내 보고서 목록
- `GET /api/reports/download/{report_id}` - 보고서 다운로드

⚠️ **Deprecated: 신규 개발 시 사용하지 마세요. v2.0 Topics/Messages/Artifacts API를 사용하세요.**

### 권한

모든 v2 API는 기본적으로 JWT 인증이 필요합니다. `get_current_active_user`/`get_current_admin_user` 의존성으로 확인합니다.

---

## 보고서 생성 프로세스

### v2.0 메시지 체이닝 개요

(`backend/doc/04.messageChaining.md` 상세)

1. **사용자 입력** → `POST /api/topics/{topic_id}/ask`
2. **컨텍스트 구성**:
   - 동일 토픽의 user 메시지들
   - 옵션에 따라 최신/지정 MD 내용
   - assistant는 참조 문서를 생성한 1건만 포함
3. **Claude chat completion 호출** → Assistant 응답 (Markdown)
4. **DB 기록**:
   - user/assistant 메시지
   - AiUsage
   - Artifact (MD, 버전 증가)
5. **HWPX 변환** (필요 시): `POST /api/artifacts/{artifact_id}/convert`

### 권장 포맷

- Markdown 헤더/섹션:
  - `# 제목`
  - `## 요약`
  - `## 배경 및 목적`
  - `## 주요 내용`
  - `## 결론 및 제언`
- HWPX 변환 시 템플릿(`backend/templates/report_template.hwpx`)의 플레이스홀더에 매핑

### 플로우 다이어그램

```
User Input → Ask API → Context Build → Claude API
                                           ↓
                                      MD Response
                                           ↓
                            Save: Message + Artifact + AI Usage
                                           ↓
                                    (Optional) MD → HWPX
```

---

## 주요 컴포넌트

### 1. Response Helper (`utils/response_helper.py`)

API 응답 표준화를 위한 헬퍼 함수 모음.

**주요 함수:**
- `success_response(data, feedback)` - 성공 응답 생성
- `error_response(code, http_status, message, details, hint)` - 에러 응답 생성

**ErrorCode 클래스:**
```python
ErrorCode.AUTH_INVALID_TOKEN
ErrorCode.TOPIC_NOT_FOUND
ErrorCode.MESSAGE_CREATION_FAILED
ErrorCode.ARTIFACT_DOWNLOAD_FAILED
ErrorCode.VALIDATION_REQUIRED_FIELD
ErrorCode.SERVER_DATABASE_ERROR
```

### 2. System Prompts (`utils/prompts.py`) - v2.1

시스템 프롬프트 중앙 관리 모듈.

**주요 상수:**
- `FINANCIAL_REPORT_SYSTEM_PROMPT` - 금융 보고서 작성용 시스템 프롬프트 (통합)
- `TOPIC_CONTEXT_TEMPLATE` - 주제 컨텍스트 메시지 템플릿 (데이터와 분리)

**설계 원칙:**
- 시스템 프롬프트는 순수 지시사항만 포함 (데이터 제외)
- 주제/컨텍스트는 메시지 배열로 전달
- 중복 방지를 위한 단일 소스 원칙

### 3. Claude Client (`utils/claude_client.py`)

Claude API 통신 클라이언트.

**주요 메서드:**
- `generate_report(topic)` - **Markdown 문자열 반환** (v2.1에서 Dict → str 변경)
- `chat_completion(messages, system_prompt)` - 대화형 응답 + 토큰 사용량 추적

**v2.1 변경사항:**
- `generate_report()`가 Markdown 문자열을 직접 반환 (파싱 제거)
- 파싱은 호출자가 `parse_markdown_to_content()` 사용
- `FINANCIAL_REPORT_SYSTEM_PROMPT` 사용

### 4. HWP Handler (`utils/hwp_handler.py`)

HWPX 파일 처리.

**주요 기능:**
- HWPX 템플릿 unzip/컨텐츠 치환/rezip
- 템플릿 미존재 시 기본 템플릿 생성 (`main.py`)
- 줄바꿈 처리 (`\n\n` → 새 문단, `\n` → `<hp:lineBreak/>`)

### 5. Markdown 파서/빌더 (`utils/markdown_parser.py`, `markdown_builder.py`)

Markdown 파일 파싱 및 생성.

**주요 함수 (markdown_parser.py):**
- `parse_markdown_to_content(md_text)` - Markdown을 HWP content dict로 변환
- `extract_all_h2_sections(md_text)` - 모든 H2 섹션 추출 (제목 + 내용)
- `classify_section(section_title)` - 키워드 기반 섹션 분류
  - 요약: "요약", "summary", "핵심", "개요"
  - 배경: "배경", "목적", "background", "추진"
  - 주요내용: "주요", "내용", "분석", "결과"
  - 결론: "결론", "제언", "conclusion", "향후", "계획"

**v2.1 변경사항:**
- 동적 섹션 제목 추출 (하드코딩 제거)
- 키워드 우선순위 조정 (결론 > 배경)
- H2 섹션 자동 분류 및 매핑

### 6. 파일/버전 유틸 (`utils/file_utils.py`)

버전 산정, 경로 생성, SHA256 해시 등.

### 7. 인증 유틸 (`utils/auth.py`)

JWT 발급/검증, bcrypt 비밀번호 해싱.

**주요 함수:**
- `hash_password(password)` - 비밀번호 해싱
- `verify_password(plain, hashed)` - 비밀번호 검증
- `create_access_token(data)` - JWT 생성
- `decode_access_token(token)` - JWT 디코딩
- `get_current_user(token)` - 현재 사용자 추출
- `get_current_active_user()` - 활성 사용자 확인
- `get_current_admin_user()` - 관리자 확인

### 8. Artifact Manager (`utils/artifact_manager.py`)

아티팩트 파일 저장/관리를 위한 추상화 레이어. 로컬 파일 시스템 지원 (향후 S3, Azure Blob 등 확장 가능).

**주요 메서드:**
- `generate_artifact_path(topic_id, message_id, filename)` - 아티팩트 저장 경로 생성
- `store_artifact(content, filepath, is_binary)` - 파일 저장 (텍스트/바이너리)
- `retrieve_artifact(filepath, is_binary)` - 파일 읽기
- `delete_artifact(filepath)` - 파일 삭제
- `calculate_sha256(filepath)` - 파일 해시 계산 (무결성 검증)
- `get_extension_for_kind(kind)` - ArtifactKind에 맞는 확장자 반환
- `generate_filename(topic_id, kind, version, locale)` - 표준 파일명 생성

**저장 구조:**
```
artifacts/
└── topics/
    └── topic_{id}/
        └── messages/
            └── msg_{message_id}_{filename}
```

### 9. Markdown Handler (`utils/md_handler.py`)

Markdown 파일 생성, 읽기, 포맷팅 유틸리티.

**주요 메서드:**
- `save_md_file(content, filepath)` - Markdown 파일 저장 (UTF-8)
- `read_md_file(filepath)` - Markdown 파일 읽기
- `format_report_as_md(report_data)` - 보고서 데이터를 Markdown 포맷으로 변환
- `parse_md_report(md_content)` - Markdown을 구조화된 데이터로 파싱
- `get_file_size(filepath)` - 파일 크기 조회
- `delete_md_file(filepath)` - 파일 삭제

**보고서 구조:**
- `# 제목`
- `## 요약`
- `## 배경 및 목적`
- `## 주요 내용`
- `## 결론 및 제언`

### 10. Transformation Tracking (`models/transformation.py`, `database/transformation_db.py`)

파일 변환 및 번역 추적 시스템. 아티팩트 간 변환 관계를 기록하여 변환 이력 추적 가능.

**지원 작업:**
- `TransformOperation.CONVERT` - 포맷 변환 (MD → HWPX)
- `TransformOperation.TRANSLATE` - 언어 번역 (KO → EN)

**주요 필드:**
- `from_artifact_id` - 원본 아티팩트 ID
- `to_artifact_id` - 변환 결과 아티팩트 ID
- `operation` - 변환 작업 타입
- `params_json` - 변환 파라미터 (JSON)
- `created_at` - 변환 시각

**주요 함수:**
- `create_transformation(transform_data)` - 변환 기록 생성
- `get_transformations_from_artifact(artifact_id)` - 특정 아티팩트에서 파생된 변환 조회
- `get_transformations_to_artifact(artifact_id)` - 특정 아티팩트를 생성한 변환 조회

---

## 테스트 가이드

### 테스트 환경

**테스트 프레임워크:**
- pytest 8.3.4
- pytest-cov 6.0.0 (코드 커버리지)
- pytest-asyncio 0.24.0 (비동기 테스트)
- pytest-mock 3.14.0 (모킹)
- httpx 0.27.2 (FastAPI TestClient)

### 의존성 설치

```bash
cd backend
uv pip install -r requirements-dev.txt
```

### 테스트 실행

**전체 테스트:**
```bash
cd backend
uv run pytest tests/ -v
```

**커버리지 포함:**
```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

**HTML 리포트:**
```bash
uv run pytest tests/ --cov=app --cov-report=html
# htmlcov/index.html 생성
```

**특정 파일:**
```bash
uv run pytest tests/test_routers_auth.py -v
```

**디버그 출력:**
```bash
uv run pytest tests/ -v -s
```

### 테스트 마커

```bash
# 유닛 테스트만
uv run pytest -m unit -v

# API 테스트만
uv run pytest -m api -v

# 인증 관련만
uv run pytest -m auth -v

# 통합 테스트 제외
uv run pytest -m "not integration" -v
```

### 주요 Fixtures (`conftest.py`)

- `test_db` - 임시 SQLite DB (자동 정리)
- `client` - FastAPI TestClient
- `test_user_data` / `test_admin_data` - 테스트 데이터
- `create_test_user` / `create_test_admin` - 테스트 사용자 생성
- `auth_headers` / `admin_auth_headers` - JWT 인증 헤더
- `temp_dir` - 임시 디렉토리 (자동 정리)

### 테스트 커버리지 (v2.0)

**전체 커버리지:** 70%+ ✅

**주요 모듈:**
- `app/utils/claude_client.py`: 100% ✅
- `app/utils/connection.py`: 100% ✅
- `app/utils/markdown_builder.py`: 100% ✅
- `app/utils/file_utils.py`: 96% ✅
- `app/utils/response_helper.py`: 95% ✅
- `app/database/topic_db.py`: 94% ✅
- `app/routers/topics.py`: 87% ✅
- `app/utils/auth.py`: 87% ✅
- `app/utils/hwp_handler.py`: 83% ✅

### 테스트 작성 예시

```python
import pytest
from app.utils.auth import hash_password, verify_password

@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    def test_hash_password(self):
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_password_success(self):
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
```

### 모킹 원칙

- 외부 API (Claude)는 반드시 mock 처리
- 모듈 사용 지점 기준 패치: `@patch('app.utils.claude_client.Anthropic')`

자세한 테스트 가이드는 `backend/BACKEND_TEST.md` 참고.

---

## 개발 가이드라인

### 1. 코드 스타일

- **PEP 8** 준수
- 함수/변수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_CASE`
- Docstring: Google 스타일 권장

### 2. 에러 핸들링

- v2.0 API는 `error_response()` 사용 (표준 응답 규격)
- `ErrorCode` 클래스 상수 사용 (하드코딩 금지)
- 로깅을 통한 에러 추적

**예시:**
```python
from app.utils.response_helper import error_response, ErrorCode

if not user:
    return error_response(
        code=ErrorCode.AUTH_INVALID_CREDENTIALS,
        http_status=401,
        message="이메일 또는 비밀번호가 올바르지 않습니다.",
        hint="입력 정보를 다시 확인해주세요."
    )
```

### 3. 로깅

- `logging` 모듈 사용
- 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL
- 중요한 이벤트 및 에러는 반드시 로깅

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"보고서 생성 완료: {report_id}")
logger.error(f"Claude API 호출 실패: {str(e)}")
```

### 4. 비동기 프로그래밍

- FastAPI는 비동기 함수 지원
- I/O 바운드 작업에 `async`/`await` 사용
- 파일 작업: `aiofiles` 권장

### 5. 데이터 검증

- Pydantic 모델로 요청/응답 검증
- 모든 입력 데이터는 검증 필수

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)
```

### 6. 보안

- 환경 변수로 민감 정보 관리 (`.env`)
- 비밀번호는 반드시 해싱 후 저장
- JWT 토큰 만료 시간 설정
- CORS 설정 확인
- SQL Injection 방지 (파라미터화 쿼리)

### 7. API 응답 표준

⚠️ **모든 신규 API 엔드포인트는 표준 응답 형식을 사용해야 합니다.**

- ✅ `success_response()` / `error_response()` 사용
- ✅ `ErrorCode` 클래스 상수 사용
- ❌ `HTTPException` 직접 사용 금지
- ❌ 에러 코드 하드코딩 금지

**참조 구현:** `backend/app/routers/topics.py`

---

## 트러블슈팅

### 1. 서버 시작 즉시 종료

**원인:** `PATH_PROJECT_HOME` 미설정

**해결:**
- `.env`에 `PATH_PROJECT_HOME` 실제 루트 경로로 설정

### 2. Claude 호출 실패/타임아웃

**원인:** API 키 문제 또는 네트워크 이슈

**해결:**
- `CLAUDE_API_KEY` 유효성 확인
- 모델명 확인 (`claude-sonnet-4-5-20250929`)
- 네트워크 접근성 점검

### 3. 401/403 인증 오류

**원인:** JWT 문제 또는 사용자 비활성

**해결:**
- JWT 설정/만료 확인
- 사용자 `is_active` 상태 확인
- 토큰 형식 확인 (`Bearer <token>`)

### 4. HWPX 변환 실패

**원인:** 템플릿 파일 문제

**해결:**
- `backend/templates/report_template.hwpx` 존재 확인
- 파서 오류 로그 확인
- 플레이스홀더 철자 확인

### 5. 파일 다운로드 404

**원인:** 파일 경로 문제

**해결:**
- Artifact/Report 레코드의 파일 경로 실재 여부 확인
- `artifacts/` 또는 `output/` 디렉토리 권한 확인

### 6. 데이터베이스 연결 오류

**증상:** `database is locked`

**해결:**
- SQLite는 단일 쓰기 잠금 사용
- 연결 후 반드시 `conn.close()` 호출
- Context manager 사용 권장

### 7. 한글 인코딩 문제

**증상:** 한글 깨짐

**해결:**
- Python 파일: UTF-8
- XML 파일: UTF-8
- Windows: `PYTHONIOENCODING=utf-8` 환경 변수

---

## 추가 참고 자료

### 공식 문서

- [FastAPI](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLite](https://www.sqlite.org/docs.html)

### 프로젝트 문서

- `CLAUDE.md` - 프로젝트 전체 개요 및 가이드
- `README.md` - 빠른 시작 가이드
- `backend/BACKEND_TEST.md` - 테스트 상세 가이드
- `backend/MIGRATION_GUIDE.md` - v1 → v2 마이그레이션

### 유용한 명령어

```bash
# DB 초기화
uv run python init_db.py

# 개발 서버
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 패키지 업데이트
uv pip install -r requirements.txt --upgrade

# 환경 변수 확인
cat .env  # Linux/Mac
type .env  # Windows
```

---

## 주요 변경사항

### v2.1 (2025-11-04)

#### 프롬프트 통합 및 아키텍처 개선

**새로운 파일:**
- `app/utils/prompts.py` - 시스템 프롬프트 중앙 관리
  - `FINANCIAL_REPORT_SYSTEM_PROMPT` - 통합 금융 보고서 프롬프트
  - `TOPIC_CONTEXT_TEMPLATE` - 주제 컨텍스트 메시지 템플릿

**아키텍처 변경:**
1. **ClaudeClient 반환 타입 변경**
   - `generate_report()`: `Dict[str, str]` → `str` (Markdown)
   - 파싱 로직 제거 (호출자로 이동)
   - 시스템 프롬프트에서 주제 정보 제거

2. **Markdown 파서 개선**
   - 동적 섹션 제목 추출 (하드코딩 제거)
   - 키워드 기반 섹션 분류 강화
   - 분류 우선순위 조정 (결론 > 배경)

3. **관심사 분리 (Separation of Concerns)**
   - ClaudeClient: AI 호출 및 원시 응답 반환
   - markdown_parser: Markdown → 구조화 데이터 변환
   - 호출자: 비즈니스 로직 및 데이터 흐름 제어

**테스트 개선:**
- 19개 실패 테스트 수정 완료
- 9개 deprecated 테스트 스킵 처리
- 테스트 커버리지 유지: 70%+

**참고 문서:**
- `backend/doc/07.PromptIntegrate.md` - 프롬프트 통합 가이드

### v2.0 (2025-10-31)

#### 시스템 아키텍처

- **단일 요청 → 대화형 시스템**
- **파일 형식**: 직접 HWPX 생성 → Markdown 생성 후 HWPX 변환

#### 새로운 기능

- `topics` - 대화 주제/스레드
- `messages` - 사용자 및 AI 메시지
- `artifacts` - 생성된 파일 (MD, HWPX) + 버전 관리
- `ai_usage` - 메시지별 AI 사용량 추적

#### 새로운 API

- `/api/topics` - 주제 CRUD + ask (메시지 체이닝)
- `/api/topics/{topic_id}/messages` - 메시지 관리
- `/api/artifacts` - 아티팩트 조회 및 변환
- `/api/artifacts/messages/{message_id}/hwpx/download` - 메시지 단위 HWPX 다운로드

#### API Response Standard

모든 API 엔드포인트가 표준화된 응답 형식 사용 (100% compliance)

#### 테스트 커버리지 개선

- 48% → 70%+ (+22%)
- claude_client: 14% → 100%
- hwp_handler: 15% → 83%

#### Deprecated

- `/api/reports` - v1.0 호환성 유지, 향후 제거 예정
- `reports`, `token_usage` 테이블 - v1.0 호환성 유지

#### 새로운 유틸리티 컴포넌트

- `app/utils/artifact_manager.py` - 아티팩트 파일 저장/관리 추상화 레이어
- `app/utils/md_handler.py` - Markdown 파일 처리 유틸리티

#### Transformation 추적

- `transformations` 테이블 - 파일 변환 이력 추적
- `TransformOperation` enum - `CONVERT`, `TRANSLATE`
- 변환 체인 지원 (MD → HWPX → PDF)

#### Shared 모듈 확장

- `shared/types/enums.py` - `TransformOperation` 추가
- `shared/constants.py/.ts/.properties` - 공유 상수 관리
- Frontend/Backend 간 상수 동기화

---

**마지막 업데이트:** 2025-11-04
**버전:** 2.1
**담당자:** Backend Development Team

---
