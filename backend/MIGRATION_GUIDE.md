# Chat-Based Report System Migration Guide

이 가이드는 기존 단일 요청 보고서 시스템을 대화형 시스템으로 마이그레이션하는 방법을 안내합니다.

## 목차

1. [사전 준비](#사전-준비)
2. [마이그레이션 실행](#마이그레이션-실행)
3. [검증](#검증)
4. [새로운 API 사용법](#새로운-api-사용법)
5. [롤백 방법](#롤백-방법)

---

## 사전 준비

### 1. 데이터 백업

⚠️ **중요**: 마이그레이션은 기존 `reports`와 `token_usage` 테이블을 **삭제**합니다. 필요한 경우 백업하세요.

```bash
# 데이터베이스 백업
cd backend/data
copy hwp_reports.db hwp_reports_backup.db
```

### 2. 환경 변수 확인

`.env` 파일에 필요한 환경 변수가 설정되어 있는지 확인합니다:

```env
# 필수
CLAUDE_API_KEY=your_api_key_here
PATH_PROJECT_HOME=D:\WorkSpace\hwp-report\hwp-report-generator

# 선택적
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

---

## 마이그레이션 실행

### Step 1: 마이그레이션 스크립트 실행

```bash
cd backend
uv run python migrate_to_chat.py
```

스크립트는 다음 작업을 수행합니다:
1. 새로운 테이블 생성 (`topics`, `messages`, `artifacts`, `ai_usage`, `transformations`)
2. 인덱스 생성 (성능 최적화)
3. 기존 테이블 삭제 (`reports`, `token_usage`)
4. 마이그레이션 검증

### Step 2: 확인 프롬프트

스크립트는 경고 메시지를 표시합니다:

```
⚠️  WARNING: This will DROP existing 'reports' and 'token_usage' tables.
All existing report data will be LOST.
Do you want to continue? (yes/no):
```

**`yes`를 입력하여 계속 진행합니다.**

### Step 3: 마이그레이션 완료 확인

성공 시 다음 메시지가 표시됩니다:

```
============================================================
✅ Migration completed successfully!
============================================================

Next steps:
1. Run backend server: uv run uvicorn app.main:app --reload
2. Check Swagger docs: http://localhost:8000/docs
3. Test new API endpoints: /api/topics, /api/messages, /api/artifacts
```

---

## 검증

### 1. 백엔드 서버 시작

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Swagger UI 확인

브라우저에서 http://localhost:8000/docs 접속

다음 엔드포인트가 표시되는지 확인:

**Topics:**
- `POST /api/topics` - Create a new topic
- `GET /api/topics` - Get user's topics
- `GET /api/topics/{topic_id}` - Get topic by ID
- `PATCH /api/topics/{topic_id}` - Update topic
- `DELETE /api/topics/{topic_id}` - Delete topic

**Messages:**
- `POST /api/topics/{topic_id}/messages` - Create a new message
- `GET /api/topics/{topic_id}/messages` - Get messages in a topic
- `GET /api/topics/{topic_id}/messages/{message_id}` - Get message by ID
- `DELETE /api/topics/{topic_id}/messages/{message_id}` - Delete message

**Artifacts:**
- `GET /api/artifacts/{artifact_id}` - Get artifact by ID
- `GET /api/artifacts/{artifact_id}/content` - Get artifact content
- `GET /api/artifacts/{artifact_id}/download` - Download artifact file
- `GET /api/artifacts/topics/{topic_id}` - Get artifacts by topic
- `POST /api/artifacts/{artifact_id}/convert` - Convert MD artifact to HWPX

### 3. 간단한 API 테스트

**Step 1: 로그인**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123!@#"}'
```

응답에서 `access_token`을 복사합니다.

**Step 2: 주제 생성**
```bash
curl -X POST http://localhost:8000/api/topics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"input_prompt": "디지털뱅킹 트렌드 분석", "language": "ko"}'
```

응답:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "input_prompt": "디지털뱅킹 트렌드 분석",
    "generated_title": null,
    "language": "ko",
    "status": "active",
    "created_at": "2025-10-28T10:30:00",
    "updated_at": "2025-10-28T10:30:00"
  },
  "error": null,
  "meta": {"requestId": "req_abc123"},
  "feedback": []
}
```

**Step 3: 주제 목록 조회**
```bash
curl -X GET http://localhost:8000/api/topics \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 새로운 API 사용법

### 보고서 생성 플로우 (Chat-Based)

#### 1. 주제 생성
```http
POST /api/topics
Content-Type: application/json
Authorization: Bearer {token}

{
  "input_prompt": "2025년 디지털뱅킹 트렌드 분석",
  "language": "ko"
}
```

**응답:** `topic_id` 획득

#### 2. 사용자 메시지 추가 (보고서 요청)
```http
POST /api/topics/{topic_id}/messages
Content-Type: application/json
Authorization: Bearer {token}

{
  "role": "user",
  "content": "위 주제로 보고서를 작성해주세요."
}
```

**Note:** 현재는 메시지만 저장됩니다. AI 응답 생성은 Phase 6의 통합 작업에서 완성될 예정입니다.

#### 3. MD 파일 조회 (추후 구현)
```http
GET /api/artifacts/{artifact_id}/content
Authorization: Bearer {token}
```

**응답:** Markdown 형식의 보고서 내용

#### 4. HWPX 변환 (추후 구현)
```http
POST /api/artifacts/{artifact_id}/convert
Authorization: Bearer {token}
```

**응답:** 변환된 HWPX artifact_id

#### 5. HWPX 다운로드
```http
GET /api/artifacts/{hwpx_artifact_id}/download
Authorization: Bearer {token}
```

**응답:** HWPX 파일 다운로드

---

## 롤백 방법

마이그레이션 후 문제가 발생하면 백업으로 롤백할 수 있습니다:

### 1. 서버 중지

현재 실행 중인 백엔드 서버를 중지합니다.

### 2. 데이터베이스 복원

```bash
cd backend/data
del hwp_reports.db
copy hwp_reports_backup.db hwp_reports.db
```

### 3. 코드 롤백

Git을 사용하는 경우:

```bash
git checkout main  # 또는 이전 안정 버전
```

### 4. 서버 재시작

```bash
cd backend
uv run uvicorn app.main:app --reload
```

---

## 주요 변경사항 요약

### 데이터베이스

**삭제된 테이블:**
- `reports` - 단일 보고서 저장
- `token_usage` - 보고서별 토큰 추적

**새로 추가된 테이블:**
- `topics` - 대화 주제/스레드
- `messages` - 대화 메시지 (user/assistant)
- `artifacts` - 생성된 파일 (MD, HWPX)
- `ai_usage` - 메시지별 AI 사용량
- `transformations` - 파일 변환 이력

### API 엔드포인트

**Deprecated (기존):**
- `POST /api/reports/generate` → **사용 중단 예정**
- `GET /api/reports/my-reports` → **사용 중단 예정**
- `GET /api/reports/download/{id}` → **사용 중단 예정**

**New (신규):**
- `POST /api/topics` - 주제 생성
- `POST /api/topics/{id}/messages` - 메시지 추가
- `GET /api/artifacts/{id}/content` - MD 내용 조회
- `POST /api/artifacts/{id}/convert` - MD → HWPX 변환
- `GET /api/artifacts/{id}/download` - 파일 다운로드

### 파일 구조

**Deprecated:**
- `backend/output/` - 기존 보고서 저장 (사용 중단)

**New:**
- `backend/artifacts/topics/topic_{id}/messages/` - 새로운 파일 구조

---

## 문제 해결

### 문제 1: 마이그레이션 스크립트가 실행되지 않음

**해결:**
```bash
# PATH_PROJECT_HOME 환경 변수 확인
echo $env:PATH_PROJECT_HOME  # Windows PowerShell
echo $PATH_PROJECT_HOME  # Linux/Mac

# .env 파일에 PATH_PROJECT_HOME 추가
PATH_PROJECT_HOME=D:\WorkSpace\hwp-report\hwp-report-generator
```

### 문제 2: 새로운 API 엔드포인트가 Swagger에 표시되지 않음

**해결:**
```bash
# 서버 재시작
# Ctrl+C로 중지 후 다시 시작
uv run uvicorn app.main:app --reload
```

### 문제 3: Import 오류 (shared 모듈)

**해결:**
```bash
# sys.path에 프로젝트 루트가 추가되어 있는지 확인
# main.py에서 자동으로 처리되므로, uvicorn으로 실행 필요
uv run uvicorn app.main:app --reload
```

---

## 지원 및 문의

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **BACKEND_TEST.md**: 테스트 가이드
- **CLAUDE.md**: 개발 가이드라인

---

**Last Updated:** 2025-10-28
**Version:** 2.0.0 (Chat-Based Architecture)
