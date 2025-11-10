# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고하는 가이드입니다.

## 프로젝트 개요

**HWP Report Generator**: Claude AI를 활용하여 한글(HWP) 형식의 금융 보고서를 자동 생성하는 FastAPI 기반 웹 시스템. 사용자가 주제를 입력하면 은행 내부 양식에 맞춰 완전한 보고서를 생성합니다.

## 기술 스택

- **Backend**: FastAPI (Python 3.12), SQLite
- **패키지 관리**: uv (권장) 또는 pip
- **AI**: Claude API (anthropic==0.71.0) - Model: claude-sonnet-4-5-20250929
- **HWP 처리**: olefile, zipfile (HWPX 형식)
- **Frontend**: React 18 + TypeScript + Vite
- **인증**: JWT (python-jose, passlib)

## 아키텍처

### 핵심 컴포넌트

**Backend** (`backend/app/`):

1. **main.py**: FastAPI 앱 진입점, 라우터 등록
2. **routers/**: API 라우트 핸들러 (auth, topics, messages, artifacts, admin, reports-deprecated)
3. **models/**: Pydantic 모델 (request/response 검증)
4. **database/**: SQLite 연결 및 CRUD 작업
5. **utils/**:
   - `prompts.py`: 시스템 프롬프트 중앙 관리 (v2.1)
   - `claude_client.py`: Claude API 통합 (Markdown 생성)
   - `markdown_parser.py`: Markdown → 구조화 데이터 변환 (동적 섹션 추출)
   - `hwp_handler.py`: HWPX 파일 조작 (unzip → XML 수정 → rezip)
   - `response_helper.py`: API 표준 응답 헬퍼
   - `auth.py`: JWT 인증 및 비밀번호 해싱

**Frontend** (`frontend/src/`):

1. **components/**: 재사용 가능한 React 컴포넌트
2. **pages/**: 페이지 컴포넌트
3. **services/**: API 클라이언트 서비스
4. **types/api.ts**: TypeScript 타입 정의

### 데이터 플로우 (v2.0+)

1. 사용자가 Topic(대화 주제) 생성 → `/api/topics`
2. 사용자 메시지 입력 → `/api/topics/{topic_id}/ask`
3. 컨텍스트 구성 (이전 메시지 + 최신/선택된 MD 내용)
4. Claude API 호출 → Markdown 응답
5. `markdown_parser.parse_markdown_to_content()`로 구조화
6. Message + Artifact(MD) + AI Usage 저장
7. 필요 시 MD → HWPX 변환 → `/api/artifacts/{id}/convert`

### 프롬프트 아키텍처 (v2.1)

**설계 원칙:**

- 시스템 프롬프트: 순수 지시사항만 (데이터 제외)
- 주제/컨텍스트: 메시지 배열로 전달
- 중앙 관리: `utils/prompts.py`

**주요 상수:**

```python
# utils/prompts.py
FINANCIAL_REPORT_SYSTEM_PROMPT = """당신은 금융 기관의 전문 보고서 작성자입니다.
다음 구조로 Markdown 보고서를 작성하세요:

# [보고서 제목]
## [요약 섹션 제목]
[요약 내용]
## [배경 섹션 제목]
[배경 내용]
## [주요 내용 섹션 제목]
[주요 내용]
## [결론 섹션 제목]
[결론 내용]
"""
```

**주제 컨텍스트 전달:**

```python
# 주제는 시스템 프롬프트가 아닌 메시지로 전달
messages = [
    {"role": "user", "content": f"다음 주제로 보고서를 작성해주세요:\n\n{topic}"}
]
```

### Markdown 파싱 (v2.1)

**동적 섹션 추출:**

```python
# markdown_parser.py
def parse_markdown_to_content(md_text: str) -> Dict[str, str]:
    """
    Markdown을 HWP content dict로 변환
    - H1: 제목 추출
    - H2 섹션: 키워드 기반 자동 분류
      - 요약: "요약", "summary", "핵심"
      - 배경: "배경", "목적", "background", "추진"
      - 주요내용: "주요", "내용", "분석", "결과"
      - 결론: "결론", "제언", "향후", "계획" (우선순위 높음)
    - 동적 제목 추출: 각 섹션의 실제 H2 제목을 title_xxx로 반환
    """
```

**우선순위 조정 (v2.1):**

- "향후 추진 계획"처럼 "추진"(배경)과 "향후"(결론) 키워드가 겹치는 경우
- 결론 키워드 체크를 배경보다 먼저 수행하여 올바르게 분류

## 환경 설정

`backend/.env` 파일:

```env
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# JWT 설정
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 관리자 계정
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123!@#
ADMIN_USERNAME=관리자

# 프로젝트 루트 (필수!)
PATH_PROJECT_HOME=D:\\WorkSpace\\hwp-report\\hwp-report-generator
```

**보안**: `.env` 파일은 절대 Git에 커밋하지 마세요.

## 개발 명령어

### Backend

```bash
cd backend

# 의존성 설치 (uv 권장)
uv pip install -r requirements.txt

# DB 초기화
uv run python init_db.py

# 개발 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 테스트 실행
uv run pytest tests/ -v

# 커버리지 포함 테스트
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버
npm run dev

# 프로덕션 빌드
npm run build
```

### 접속

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## API 응답 표준

### ⚠️ 필수 준수 규칙

**모든 신규 API 엔드포인트는 표준 응답 형식을 사용해야 합니다.**

- ✅ **필수**: `success_response()` / `error_response()` 사용 (`utils/response_helper.py`)
- ✅ **필수**: `ErrorCode` 클래스 상수 사용
- ❌ **금지**: `HTTPException` 직접 사용
- ❌ **금지**: 에러 코드 하드코딩

### 표준 응답 구조

**성공:**

```json
{
  "success": true,
  "data": {
    /* 실제 데이터 */
  },
  "error": null,
  "meta": { "requestId": "uuid" },
  "feedback": []
}
```

**실패:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DOMAIN.DETAIL",
    "httpStatus": 404,
    "message": "에러 메시지",
    "details": {},
    "traceId": "uuid",
    "hint": "해결 방법"
  },
  "meta": { "requestId": "uuid" },
  "feedback": []
}
```

### 구현 예시

```python
from app.utils.response_helper import success_response, error_response, ErrorCode

# 성공
return success_response({
    "id": 123,
    "name": "example"
})

# 실패
return error_response(
    code=ErrorCode.TOPIC_NOT_FOUND,
    http_status=404,
    message="토픽을 찾을 수 없습니다.",
    hint="토픽 ID를 확인해주세요."
)
```

### 현재 구현 상태

| Router    | 준수율  | 상태                   |
| --------- | ------- | ---------------------- |
| Topics    | 100% ✅ | 참조 구현              |
| Messages  | 100% ✅ | 완전 준수              |
| Artifacts | 100% ✅ | 완전 준수              |
| Auth      | 100% ✅ | 완전 준수              |
| Admin     | 100% ✅ | 완전 준수              |
| Reports   | 100% ✅ | 완전 준수 (Deprecated) |

**전체 준수율**: 100% (28/28 활성 엔드포인트) ✨

## HWP 파일 처리

- **형식**: HWPX (HWP가 아님). HWPX는 XML 파일을 포함한 ZIP 아카이브
- **처리**: Unzip → XML 파싱/수정 → Rezip
- **호환성**: HWPX 형식은 크로스 플랫폼 호환성 보장
- **인코딩**: 한글 텍스트는 UTF-8 필수
- **자동 템플릿**: `templates/report_template.hwpx`가 없으면 첫 보고서 생성 시 자동 생성

### 줄바꿈 처리

1. **문단 분리**: `\n\n` → 별도 `<hp:p>` 태그
2. **줄바꿈**: `\n` → `<hp:lineBreak/>` XML 태그
3. **레이아웃 정리**: 불완전한 `<hp:linesegarray>` 요소 자동 제거
4. **자동 계산**: 한글 워드프로세서가 파일 열 때 레이아웃 정보 자동 재계산

### HWPX 템플릿 플레이스홀더

**컨텐츠:**

- `{{TITLE}}` - 보고서 제목
- `{{DATE}}` - 생성 날짜
- `{{SUMMARY}}` - 요약 내용
- `{{BACKGROUND}}` - 배경 내용
- `{{MAIN_CONTENT}}` - 주요 내용
- `{{CONCLUSION}}` - 결론 내용

**섹션 제목 (동적 추출 - v2.1):**

- `{{TITLE_SUMMARY}}` - 요약 섹션 제목
- `{{TITLE_BACKGROUND}}` - 배경 섹션 제목
- `{{TITLE_MAIN_CONTENT}}` - 주요 내용 섹션 제목
- `{{TITLE_CONCLUSION}}` - 결론 섹션 제목

## 주요 API 엔드포인트

### 인증 (`/api/auth`)

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인 (JWT 발급)
- `GET /api/auth/me` - 내 정보
- `POST /api/auth/logout` - 로그아웃

### 주제 (`/api/topics`) - v2.0

- `POST /api/topics` - 토픽 생성
- `POST /api/topics/generate` - 한 번에 MD 생성 (토픽+메시지+아티팩트)
- `GET /api/topics` - 내 토픽 목록
- `GET /api/topics/{topic_id}` - 단건 조회
- `POST /api/topics/{topic_id}/ask` - **메시지 체이닝** (컨텍스트 기반 대화)

### 메시지 (`/api/topics/{topic_id}/messages`)

- `POST /api/topics/{topic_id}/messages` - 메시지 생성
- `GET /api/topics/{topic_id}/messages` - 메시지 목록

### 아티팩트 (`/api/artifacts`)

- `GET /api/artifacts/{artifact_id}` - 메타 조회
- `GET /api/artifacts/{artifact_id}/content` - 내용 조회 (MD만)
- `GET /api/artifacts/{artifact_id}/download` - 파일 다운로드
- `POST /api/artifacts/{artifact_id}/convert` - MD → HWPX 변환
- `GET /api/artifacts/messages/{message_id}/hwpx/download` - 메시지 기반 HWPX 다운로드 (자동 변환)

### 관리자 (`/api/admin`)

- `GET /api/admin/users` - 사용자 목록
- `POST /api/admin/users/{user_id}/approve` - 승인
- `GET /api/admin/token-usage` - 토큰 사용량

### 레거시 (`/api/reports`) - Deprecated

- ⚠️ v1.0 호환성 유지, 향후 제거 예정
- 신규 개발은 `/api/topics` 사용

## 주요 변경사항

### v2.2 (2025-11-10) - /ask 아티팩트 마크다운 파싱 수정 + 동적 프롬프트 템플릿 통합

**버그 수정:**

- **문제**: `/api/topics/{topic_id}/ask` 엔드포인트에서 Claude 응답 전체가 artifact로 저장
- **원인**: 마크다운 파싱 및 빌드 로직 누락
- **해결**: `parse_markdown_to_content()` + `build_report_md()` 추가로 파싱된 마크다운만 저장
- **결과**: `/ask`와 `generate_topic_report` 처리 방식 일관성 확보 ✅

**동적 프롬프트 템플릿 통합:**

- **Template 기반 동적 System Prompt**: Placeholder 기반으로 맞춤형 프롬프트 자동 생성
- **우선순위**: custom prompt > template_id > default prompt
- **권한 관리**: Template 소유자만 접근 가능
- **에러 처리**: TEMPLATE_NOT_FOUND, TEMPLATE_NOT_FOUND 에러 코드 추가

**테스트 개선:**

- `/ask` 관련 마크다운 파싱 3개 신규 테스트 추가
- 전체 topics 테스트: 28/28 통과 (100%)
- 커버리지: 52% (topics.py 78% 달성)

**참고:**
- `backend/doc/specs/20251110_fix_ask_artifact_markdown_parsing.md` - Unit Spec
- `backend/doc/07.PromptIntegrate.md` - 프롬프트 통합 가이드

### v2.1 (2025-11-04) - 프롬프트 통합

**새로운 파일:**

- `app/utils/prompts.py` - 시스템 프롬프트 중앙 관리

**아키텍처 변경:**

1. **ClaudeClient 반환 타입**: `Dict[str, str]` → `str` (Markdown)
2. **파싱 로직 분리**: ClaudeClient에서 제거, 호출자가 `parse_markdown_to_content()` 사용
3. **프롬프트 순수성**: 시스템 프롬프트에서 주제 제거, 메시지로 전달
4. **동적 섹션 추출**: 하드코딩된 제목 제거, 키워드 기반 자동 분류
5. **관심사 분리**: ClaudeClient(AI 호출) / markdown_parser(파싱) / 호출자(비즈니스 로직)

**테스트:**

- 19개 실패 테스트 수정
- 9개 deprecated 테스트 스킵
- 커버리지 유지: 70%+

**참고:** `backend/doc/07.PromptIntegrate.md`

### v2.0 (2025-10-31) - 대화형 시스템

**시스템 전환:**

- 단일 요청 → 대화형 시스템 (Topics + Messages)
- 직접 HWPX 생성 → Markdown 생성 후 변환

**새 기능:**

- Topics (대화 주제/스레드)
- Messages (사용자/AI 메시지)
- Artifacts (MD, HWPX 버전 관리)
- AI Usage (메시지별 사용량 추적)
- Transformations (변환 이력)

**API 표준:**

- 모든 엔드포인트 표준 응답 형식 (100% compliance)

**테스트:**

- 커버리지 48% → 70%+ (+22%)
- claude_client: 14% → 100%
- hwp_handler: 15% → 83%

## 에러 코드

에러 코드는 `DOMAIN.DETAIL` 형식:

**인증 (`AUTH.*`):**

- `AUTH.INVALID_TOKEN` - 유효하지 않은 토큰
- `AUTH.INVALID_CREDENTIALS` - 잘못된 이메일/비밀번호
- `AUTH.UNAUTHORIZED` - 권한 부족

**주제 (`TOPIC.*`):**

- `TOPIC.NOT_FOUND` - 주제를 찾을 수 없음
- `TOPIC.UNAUTHORIZED` - 접근 권한 없음
- `TOPIC.CREATION_FAILED` - 생성 실패

**메시지 (`MESSAGE.*`):**

- `MESSAGE.NOT_FOUND` - 메시지를 찾을 수 없음
- `MESSAGE.CREATION_FAILED` - 생성 실패

**아티팩트 (`ARTIFACT.*`):**

- `ARTIFACT.NOT_FOUND` - 아티팩트를 찾을 수 없음
- `ARTIFACT.DOWNLOAD_FAILED` - 다운로드 실패

**검증 (`VALIDATION.*`):**

- `VALIDATION.REQUIRED_FIELD` - 필수 필드 누락
- `VALIDATION.INVALID_FORMAT` - 잘못된 형식

**서버 (`SERVER.*`):**

- `SERVER.INTERNAL_ERROR` - 내부 서버 오류
- `SERVER.DATABASE_ERROR` - 데이터베이스 오류

## 프로젝트 구조

```
hwp-report-generator/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/        # auth, topics, messages, artifacts, admin, reports
│   │   ├── models/         # Pydantic 모델
│   │   ├── database/       # SQLite CRUD
│   │   └── utils/
│   │       ├── prompts.py         # ✨ 시스템 프롬프트 (v2.1)
│   │       ├── claude_client.py   # Claude API (Markdown 반환)
│   │       ├── markdown_parser.py # ✨ 동적 파싱 (v2.1)
│   │       ├── hwp_handler.py     # HWPX 처리
│   │       ├── response_helper.py # API 표준 응답
│   │       └── auth.py            # JWT
│   ├── templates/          # report_template.hwpx
│   ├── artifacts/          # 생성 파일 (MD, HWPX)
│   ├── data/               # hwp_reports.db
│   ├── doc/                # 개발 문서
│   ├── tests/              # pytest 테스트
│   └── .env
│
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/api.ts
│   └── package.json
│
├── CLAUDE.md              # 이 파일
├── BACKEND_ONBOARDING.md  # 백엔드 상세 가이드
└── README.md
```

## Unit Spec Workflow

**⚠️ MANDATORY: Before implementing ANY feature or fix, Claude Code MUST create a Unit Spec document.**

### Workflow

1. **User Request** → Feature/bug description
2. **Unit Spec Creation** → Claude creates `spec following template
3. **User Review** → User reviews and approves
4. **Implementation** → Implement per spec
5. **Testing** → Verify test cases\ in spec

### Unit Spec Template

Each spec includes:

1. **Requirements Summary**

   - Purpose (one-line)
   - Type: ☐ New ☐ Change ☐ Delete
   - Core requirements (input/output/constraints/flow)

2. **Implementation Files** (New/Change/Reference table)

3. **Flow Diagram** (Mermaid)

4. **Test Plan**
   - TDD principles
   - Test cases table (TC ID, Layer, Scenario, Purpose, Input, Expected)

### Spec File Management

- **Location:** `backend/doc/specs/`
- **Naming:** `YYYYMMDD_feature_name.md`
- **Template:** `backend/doc/Backend_UnitSpec.md`

### Example

```
User: "Add PDF export feature"

Claude: "Creating Unit Spec first..."
→ Creates: backend/doc/specs/20251106_pdf_export.md
→ Shows: Summary of requirements, files, flow, tests
→ Asks: "Please review. Proceed?"

User: "Approved"

Claude: "Implementing..."
→ Code + Tests → Report results
```

### Benefits

- Clear requirements before coding
- Test-first development (TDD)
- Built-in documentation
- Early review point
- Consistent process

---

## 참고 문서

- `BACKEND_ONBOARDING.md` - 백엔드 온보딩 상세 가이드
- `backend/BACKEND_TEST.md` - 테스트 가이드
- `backend/CLAUDE.md` - 백엔드 개발 가이드라인 (DocString, 파일 관리)
- `backend/doc/Backend_UnitSpec.md` - **Unit Spec 템플릿**
- `backend/doc/07.PromptIntegrate.md` - 프롬프트 통합 가이드
- `backend/doc/04.messageChaining.md` - 메시지 체이닝 설계

---

**마지막 업데이트:** 2025-11-10
**버전:** 2.3
**Claude Code 최적화**

**최신 개선사항 (2025-11-10):**
- ✅ `/ask` 엔드포인트 아티팩트 마크다운 파싱 버그 수정
- ✅ 마크다운 파싱 검증 테스트 3개 추가 (TC-ASK-001, 003, 004)
- ✅ topics.py 커버리지 39% → 78% 향상
- ✅ 모든 28개 토픽 테스트 통과 (100%)
- ✅ Unit Spec 작성: `backend/doc/specs/20251110_fix_ask_artifact_markdown_parsing.md`
