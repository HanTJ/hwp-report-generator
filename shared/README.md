# API 공통 상수 (Shared Constants)

Frontend (React)와 Backend (FastAPI) 간 공유하는 API 상수 정의

## 파일 구조

```
shared/
├── constants.properties   # 원본 상수 정의 (Properties 형식)
├── constants.py          # Python 상수 (Backend용)
├── constants.ts          # TypeScript 상수 (Frontend용)
└── README.md            # 사용 가이드 (이 파일)
```

---

## 1. Python (Backend) 사용 예시

### 기본 사용법

```python
from shared.constants import (
    ErrorCode,
    Message,
    HttpStatus,
    FeedbackCode,
    FeedbackLevel,
    ValidationConstraint,
    get_error_message,
    get_error_hint
)

# 에러 응답 생성
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.post("/api/report/generate")
async def generate_report(topic: str):
    # 검증
    if len(topic) < ValidationConstraint.REPORT_TOPIC.MIN_LENGTH:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.REPORT.TOPIC_TOO_SHORT,
                    "httpStatus": HttpStatus.BAD_REQUEST,
                    "message": get_error_message(ErrorCode.REPORT.TOPIC_TOO_SHORT),
                    "hint": get_error_hint(ErrorCode.REPORT.TOPIC_TOO_SHORT),
                    "details": {
                        "minLength": ValidationConstraint.REPORT_TOPIC.MIN_LENGTH,
                        "currentLength": len(topic)
                    }
                },
                "meta": {"requestId": str(uuid.uuid4())},
                "timestamp": datetime.now().isoformat(),
                "feedback": []
            }
        )

    # 성공 응답 (피드백 포함)
    return {
        "success": True,
        "data": {"reportId": "123", "filename": "report.hwpx"},
        "error": None,
        "meta": {"requestId": str(uuid.uuid4())},
        "timestamp": datetime.now().isoformat(),
        "feedback": [
            {
                "code": FeedbackCode.REPORT.GENERATION_SUCCESS,
                "level": FeedbackLevel.INFO,
                "message": "보고서 생성이 완료되었습니다."
            }
        ]
    }
```

### Claude API 에러 처리

```python
from shared.constants import ErrorCode, Message, HttpStatus
import anthropic

try:
    # Claude API 호출
    response = claude_client.generate(prompt)
except anthropic.RateLimitError:
    return JSONResponse(
        status_code=HttpStatus.TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.CLAUDE.RATE_LIMIT,
                "httpStatus": HttpStatus.TOO_MANY_REQUESTS,
                "message": Message.ERROR.CLAUDE_RATE_LIMIT,
                "hint": Message.HINT.REDUCE_REQUEST_RATE
            }
        }
    )
```

### 설정값 사용

```python
from shared.constants import TokenConfig, BusinessRule, ClaudeConfig

# JWT 토큰 생성
from datetime import datetime, timedelta

access_token_expire = datetime.utcnow() + timedelta(
    minutes=TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES
)

# 파일 경로
template_path = BusinessRule.REPORT.TEMPLATE_PATH  # "templates/report_template.hwpx"
output_dir = BusinessRule.REPORT.OUTPUT_DIRECTORY  # "output"

# Claude API 설정
claude_model = ClaudeConfig.MODEL
max_tokens = ClaudeConfig.MAX_TOKENS
```

---

## 2. TypeScript (Frontend) 사용 예시

### 기본 사용법

```typescript
import {
  ErrorCode,
  Message,
  HttpStatus,
  FeedbackLevel,
  ValidationConstraint,
  getErrorMessage,
  getErrorHint,
  ApiResponse,
  isApiError,
  isApiSuccess
} from '@/shared/constants';

// API 호출 예시
const generateReport = async (topic: string) => {
  // 클라이언트 검증
  if (topic.length < ValidationConstraint.REPORT_TOPIC.MIN_LENGTH) {
    showError(Message.ERROR.TOPIC_TOO_SHORT);
    return;
  }

  try {
    const response = await apiClient.post<ApiResponse>('/api/report/generate', {
      topic
    });

    // 성공 응답 처리
    if (isApiSuccess(response.data)) {
      console.log('Report ID:', response.data.data.reportId);

      // 피드백 처리
      response.data.feedback.forEach(fb => {
        if (fb.level === FeedbackLevel.INFO) {
          showInfoToast(fb.message);
        } else if (fb.level === FeedbackLevel.WARNING) {
          showWarningToast(fb.message);
        }
      });
    }
  } catch (error: any) {
    const apiError = error.response?.data;

    if (isApiError(apiError)) {
      // 에러 코드별 처리
      switch (apiError.error.code) {
        case ErrorCode.AUTH.INVALID_TOKEN:
        case ErrorCode.AUTH.TOKEN_EXPIRED:
          // 로그인 페이지로 리다이렉트
          redirectToLogin();
          break;

        case ErrorCode.REPORT.TOPIC_TOO_SHORT:
          // 필드 에러 표시
          setFieldError('topic', apiError.error.message);
          if (apiError.error.hint) {
            showHint(apiError.error.hint);
          }
          break;

        case ErrorCode.CLAUDE.RATE_LIMIT:
          // Rate Limit 에러
          showErrorNotification(
            apiError.error.message,
            apiError.error.hint
          );
          break;

        default:
          // 기본 에러 처리
          showErrorNotification(
            getErrorMessage(apiError.error.code),
            getErrorHint(apiError.error.code)
          );
      }
    }
  }
};
```

### Axios Interceptor에서 사용

```typescript
import axios from 'axios';
import { ErrorCode, Endpoint } from '@/shared/constants';

const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

// Response 인터셉터: 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const errorCode = error.response?.data?.error?.code;

    // 토큰 만료 시 자동 갱신
    if (errorCode === ErrorCode.AUTH.TOKEN_EXPIRED) {
      try {
        const refreshResponse = await axios.post(Endpoint.AUTH.REFRESH, {}, {
          withCredentials: true
        });

        if (refreshResponse.data.success) {
          // 원래 요청 재시도
          return apiClient(error.config);
        }
      } catch (refreshError) {
        // Refresh 실패 시 로그인 페이지로
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
```

### React Component에서 사용

```typescript
import React, { useState } from 'react';
import { ValidationConstraint, Message } from '@/shared/constants';

const ReportForm: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // 클라이언트 검증
    if (topic.length < ValidationConstraint.REPORT_TOPIC.MIN_LENGTH) {
      setError(Message.ERROR.TOPIC_TOO_SHORT);
      return;
    }

    if (topic.length > ValidationConstraint.REPORT_TOPIC.MAX_LENGTH) {
      setError(Message.ERROR.TOPIC_TOO_LONG);
      return;
    }

    // API 호출
    generateReport(topic);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        minLength={ValidationConstraint.REPORT_TOPIC.MIN_LENGTH}
        maxLength={ValidationConstraint.REPORT_TOPIC.MAX_LENGTH}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">보고서 생성</button>
    </form>
  );
};
```

---

## 3. 상수 추가 방법

### 1) constants.properties에 추가

```properties
# 새로운 에러 코드 추가
ERROR.USER.DUPLICATE_EMAIL=USER.DUPLICATE_EMAIL

# 새로운 메시지 추가
MESSAGE.ERROR.DUPLICATE_EMAIL=이미 사용 중인 이메일입니다.
```

### 2) constants.py에 추가

```python
class ErrorCode:
    class USER:
        DUPLICATE_EMAIL = _props.get("ERROR.USER.DUPLICATE_EMAIL")

class Message:
    class ERROR:
        DUPLICATE_EMAIL = _props.get("MESSAGE.ERROR.DUPLICATE_EMAIL")
```

### 3) constants.ts에 추가

```typescript
export const ErrorCode = {
  USER: {
    DUPLICATE_EMAIL: 'USER.DUPLICATE_EMAIL',
  },
} as const;

export const Message = {
  ERROR: {
    DUPLICATE_EMAIL: '이미 사용 중인 이메일입니다.',
  },
} as const;
```

---

## 4. 네이밍 컨벤션

### 에러 코드
- 형식: `도메인.세부_에러`
- 예시: `AUTH.INVALID_TOKEN`, `REPORT.GENERATION_FAILED`

### 피드백 코드
- 형식: `도메인.액션_또는_상태`
- 예시: `PROFILE.INCOMPLETE`, `REPORT.GENERATION_SUCCESS`

### 메시지 키
- 형식: `MESSAGE.{타입}.{설명}`
- 예시: `MESSAGE.ERROR.INVALID_TOKEN`, `MESSAGE.SUCCESS.REPORT_GENERATED`

---

## 5. 사용 가능한 상수 목록

### ErrorCode
- `ErrorCode.AUTH.*` - 인증/인가 에러
- `ErrorCode.VALIDATION.*` - 검증 에러
- `ErrorCode.REPORT.*` - 보고서 생성 에러
- `ErrorCode.HWP.*` - HWP 파일 처리 에러
- `ErrorCode.CLAUDE.*` - Claude API 에러
- `ErrorCode.FILE.*` - 파일 처리 에러
- `ErrorCode.SYSTEM.*` - 시스템 에러

### FeedbackCode
- `FeedbackCode.PROFILE.*` - 프로필 관련 피드백
- `FeedbackCode.REPORT.*` - 보고서 관련 피드백
- `FeedbackCode.SYSTEM.*` - 시스템 알림
- `FeedbackCode.SECURITY.*` - 보안 알림

### 설정값
- `ValidationConstraint` - 검증 제약조건
- `TokenConfig` - JWT 토큰 설정
- `CookieConfig` - 쿠키 설정
- `BusinessRule` - 비즈니스 규칙
- `ClaudeConfig` - Claude API 설정
- `Endpoint` - API 엔드포인트

---

## 6. 베스트 프랙티스

### ✅ 권장사항
1. **항상 상수 사용**: 하드코딩된 문자열 대신 상수 사용
2. **타입 안정성**: TypeScript에서 타입 추론 활용
3. **일관성**: 프론트/백엔드 동일한 에러 코드 사용
4. **에러 힌트 제공**: 사용자에게 해결 방법 안내

### ❌ 피해야 할 사항
1. 하드코딩된 에러 메시지 사용
2. 에러 코드 중복 정의
3. 네이밍 컨벤션 무시
4. 상수 파일 직접 수정 (properties → py/ts 자동 동기화)

---

## 7. 트러블슈팅

### Python에서 상수가 None으로 나올 때
```python
# constants.properties 파일 경로 확인
import os
from pathlib import Path

current_dir = Path(__file__).parent
props_file = current_dir / "constants.properties"
print(f"Properties file exists: {os.path.exists(props_file)}")
```

### TypeScript에서 import 에러
```typescript
// tsconfig.json에 path alias 추가
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/shared/*": ["shared/*"]
    }
  }
}
```

---

## 8. 유지보수

### 상수 변경 시 체크리스트
- [ ] `constants.properties` 수정
- [ ] `constants.py` 동기화
- [ ] `constants.ts` 동기화
- [ ] 영향받는 코드 확인
- [ ] 테스트 코드 업데이트
- [ ] API 문서 업데이트

---

## 9. 참고 링크

- [API 공통 규격 양식](../API%20공통%20규격%20양식.txt)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Best Practices](https://react.dev/)
