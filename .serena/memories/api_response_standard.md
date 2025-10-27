# API 공통 규격 양식

HWP Report Generator 프로젝트의 모든 Backend-Frontend 간 API 응답은 아래 표준 형식을 따릅니다.

## 성공 응답 (SUCCESS)

```json
{
  "success": true,
  "data": { /* 리소스 또는 결과 데이터 */ },
  "error": null,
  "meta": {
    "requestId": "1c0c...f"
  },
  "feedback": [
    {
      "code": "PROFILE_INCOMPLETE",
      "level": "info",            // info | warning | error
      "feedbackCd": "프로필 사진을 등록하면 더 좋아요."
    }
  ]
}
```

### 필드 설명 (성공)
- `success`: `true` - 요청 성공 여부
- `data`: 실제 응답 데이터 (리소스, 결과 등)
- `error`: `null` - 에러가 없으므로 null
- `meta`: 메타데이터 객체
  - `requestId`: 요청 추적용 고유 ID
- `feedback`: 선택적 피드백 배열 (사용자에게 유용한 힌트/경고)
  - `code`: 피드백 코드
  - `level`: 피드백 레벨 (`info` | `warning` | `error`)
  - `feedbackCd`: 피드백 메시지

## 실패 응답 (FAILED)

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_TOKEN",   // 고유 에러 코드(도메인.세부)
    "httpStatus": 401,
    "message": "유효하지 않은 토큰입니다.",
    "details": { "reason": "expired" },
    "traceId": "1c0c...f",
    "hint": "다시 로그인해 주세요."
  },
  "meta": { "requestId": "1c0c...f" },
  "feedback": []
}
```

### 필드 설명 (실패)
- `success`: `false` - 요청 실패
- `data`: `null` - 실패 시 데이터 없음
- `error`: 에러 상세 정보 객체
  - `code`: 고유 에러 코드 (형식: `도메인.세부`, 예: `AUTH.INVALID_TOKEN`)
  - `httpStatus`: HTTP 상태 코드 (예: 401, 404, 500)
  - `message`: 사용자 친화적 에러 메시지
  - `details`: 에러 상세 정보 (선택)
  - `traceId`: 에러 추적용 고유 ID
  - `hint`: 사용자에게 제공할 해결 방법 힌트 (선택)
- `meta`: 메타데이터 객체
  - `requestId`: 요청 추적용 고유 ID
- `feedback`: 빈 배열 (실패 시에는 보통 비어있음)

## 구현 지침

### Backend (FastAPI)
모든 API 엔드포인트는 이 표준 형식을 따라야 합니다:

```python
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from enum import Enum

class FeedbackLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class Feedback(BaseModel):
    code: str
    level: FeedbackLevel
    feedbackCd: str

class ErrorResponse(BaseModel):
    code: str
    httpStatus: int
    message: str
    details: Optional[Dict[str, Any]] = None
    traceId: str
    hint: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorResponse] = None
    meta: Dict[str, str]
    feedback: List[Feedback] = []
```

### Frontend (React/TypeScript)
타입 정의:

```typescript
type FeedbackLevel = 'info' | 'warning' | 'error';

interface Feedback {
  code: string;
  level: FeedbackLevel;
  feedbackCd: string;
}

interface ErrorResponse {
  code: string;
  httpStatus: number;
  message: string;
  details?: Record<string, any>;
  traceId: string;
  hint?: string;
}

interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ErrorResponse | null;
  meta: {
    requestId: string;
  };
  feedback: Feedback[];
}
```

## 에러 코드 컨벤션

에러 코드는 `도메인.세부` 형식을 따릅니다:

- `AUTH.INVALID_TOKEN` - 인증 관련, 유효하지 않은 토큰
- `AUTH.TOKEN_EXPIRED` - 인증 관련, 토큰 만료
- `AUTH.UNAUTHORIZED` - 인증 관련, 권한 없음
- `REPORT.GENERATION_FAILED` - 보고서 관련, 생성 실패
- `REPORT.NOT_FOUND` - 보고서 관련, 찾을 수 없음
- `TEMPLATE.INVALID_FORMAT` - 템플릿 관련, 잘못된 형식
- `TEMPLATE.UPLOAD_FAILED` - 템플릿 관련, 업로드 실패
- `VALIDATION.REQUIRED_FIELD` - 유효성 검증, 필수 필드 누락
- `VALIDATION.INVALID_FORMAT` - 유효성 검증, 잘못된 형식
- `SERVER.INTERNAL_ERROR` - 서버 관련, 내부 오류
- `SERVER.SERVICE_UNAVAILABLE` - 서버 관련, 서비스 이용 불가

## 적용 범위

이 API 응답 표준은 다음 모든 엔드포인트에 적용됩니다:

1. **인증 API** (`/api/auth/*`)
   - 로그인, 회원가입, 로그아웃, 토큰 갱신 등

2. **보고서 API** (`/api/reports/*`)
   - 보고서 생성, 조회, 다운로드, 삭제 등

3. **템플릿 API** (`/api/templates/*`)
   - 템플릿 CRUD, 플레이스홀더 관리 등

4. **프롬프트 API** (`/api/prompts/*`)
   - 프롬프트 프리셋 CRUD 등

5. **관리자 API** (`/api/admin/*`)
   - 사용자 관리, 시스템 설정 등

## 예시

### 보고서 생성 성공
```json
{
  "success": true,
  "data": {
    "reportId": 123,
    "filename": "2025년_디지털뱅킹_트렌드.hwpx",
    "filePath": "/output/report_123.hwpx",
    "createdAt": "2025-10-27T10:30:00Z"
  },
  "error": null,
  "meta": {
    "requestId": "req_abc123"
  },
  "feedback": []
}
```

### 로그인 실패
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_CREDENTIALS",
    "httpStatus": 401,
    "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
    "details": { "field": "password" },
    "traceId": "trace_xyz789",
    "hint": "비밀번호를 잊으셨다면 '비밀번호 찾기'를 이용해주세요."
  },
  "meta": {
    "requestId": "req_def456"
  },
  "feedback": []
}
```
