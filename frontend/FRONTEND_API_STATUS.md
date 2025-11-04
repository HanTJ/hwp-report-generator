# Frontend API Implementation Status

> 프론트엔드/백엔드 API 엔드포인트 구현 현황 정리
>
> 작성일: 2025-10-30
> 최종 업데이트: 2025-10-30
> 기준: BACKEND_ONBOARDING.md v2.0

## 범례

### 프론트엔드 구현 상태

- ✅ **구현 완료**: 프론트엔드에 구현되어 사용 가능
- ❌ **미구현**: 백엔드 API는 존재하나 프론트엔드 미구현
- ⚠️ **부분 구현**: 일부 기능만 구현되었거나 개선 필요
- 🗑️ **Deprecated**: v1.0 호환성 유지, 향후 제거 예정

### 백엔드 구현 상태

- 🟢 **BE 구현**: 백엔드에서 실제 동작하는 로직 구현됨
- 🔴 **BE 미구현**: 백엔드 엔드포인트는 존재하나 실제 로직 미구현 (501 에러 등)

---

## 1. 인증 API (`/api/auth`)

**구현 파일**: `frontend/src/services/authApi.ts`

| Method | Endpoint                    | FE 상태 | BE 상태 | 비고                        |
| ------ | --------------------------- | ------- | ------- | --------------------------- |
| POST   | `/api/auth/register`        | ✅      | 🟢      | 회원가입                    |
| POST   | `/api/auth/login`           | ✅      | 🟢      | 로그인                      |
| POST   | `/api/auth/logout`          | ✅      | 🟢      | 로그아웃 ⭐                 |
| GET    | `/api/auth/me`              | ❌      | 🟢      | **FE 미구현** (BE는 구현됨) |
| POST   | `/api/auth/change-password` | ✅      | 🟢      | 비밀번호 변경               |

**구현률**:

- 프론트엔드: 80% (4/5)
- 백엔드: 100% (5/5) ✅

### 미구현 API 상세

#### `GET /api/auth/me`

현재 로그인한 사용자의 정보를 조회하는 엔드포인트입니다.

**필요성**:

- 페이지 새로고침 시 사용자 정보 복원
- 토큰 유효성 검증

**구현 예시**:

```typescript
getCurrentUser: async (): Promise<UserData> => {
    const response = await api.get<ApiResponse<UserData>>(API_ENDPOINTS.ME)

    if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error?.message || '사용자 정보 조회에 실패했습니다.')
    }

    return response.data.data
}
```

---

## 2. 토픽 API (`/api/topics`)

**구현 파일**: `frontend/src/services/topicApi.ts`

| Method | Endpoint                 | FE 상태 | BE 상태 | 비고                               |
| ------ | ------------------------ | ------- | ------- | ---------------------------------- |
| POST   | `/api/topics`            | ✅      | 🟢      | 토픽 생성 (AI 응답 없이)           |
| POST   | `/api/topics/generate`   | ✅      | 🟢      | 토픽 생성 + AI 보고서 자동 생성 ⭐ |
| GET    | `/api/topics`            | ✅      | 🟢      | 토픽 목록 조회                     |
| GET    | `/api/topics/{topic_id}` | ✅      | 🟢      | 특정 토픽 조회                     |
| PATCH  | `/api/topics/{topic_id}` | ✅      | 🟢      | 토픽 업데이트                      |
| DELETE | `/api/topics/{topic_id}` | ✅      | 🟢      | 토픽 삭제                          |

**구현률**:

- 프론트엔드: 100% (6/6) ✨
- 백엔드: 100% (6/6) ✨

**특이사항**:

- `POST /api/topics/generate`: v2.0의 핵심 API로, 토픽 생성 + Claude 보고서 자동 생성을 한 번에 처리
- 모든 CRUD 기능 완벽 구현

---

## 3. 메시지 API (`/api/topics/{topic_id}/messages`)

**구현 파일**: `frontend/src/services/messageApi.ts`

| Method | Endpoint                                       | FE 상태 | BE 상태 | 비고                                   |
| ------ | ---------------------------------------------- | ------- | ------- | -------------------------------------- |
| POST   | `/api/topics/{topic_id}/messages`              | ✅      | 🟢      | 메시지 생성 (user role → AI 자동 응답) |
| GET    | `/api/topics/{topic_id}/messages`              | ✅      | 🟢      | 메시지 목록 조회                       |
| GET    | `/api/topics/{topic_id}/messages/{message_id}` | ❌      | 🟢      | **FE 미구현** (BE는 구현됨)            |
| DELETE | `/api/topics/{topic_id}/messages/{message_id}` | ❌      | 🟢      | **FE 미구현** (BE는 구현됨)            |

**구현률**:

- 프론트엔드: 50% (2/4)
- 백엔드: 100% (4/4) ✅

### 미구현 API 상세

#### `GET /api/topics/{topic_id}/messages/{message_id}`

특정 메시지의 상세 정보를 조회합니다.

**필요성**:

- 특정 메시지만 다시 불러오기
- 메시지 수정 기능 구현 시 필요

**구현 예시**:

```typescript
getMessage: async (topicId: number, messageId: number): Promise<Message> => {
    const response = await api.get<ApiResponse<Message>>(API_ENDPOINTS.GET_MESSAGE(topicId, messageId))

    if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error?.message || '메시지 조회에 실패했습니다.')
    }

    return response.data.data
}
```

#### `DELETE /api/topics/{topic_id}/messages/{message_id}`

특정 메시지를 삭제합니다.

**필요성**:

- 잘못 전송된 메시지 삭제
- 대화 흐름 관리

**구현 예시**:

```typescript
deleteMessage: async (topicId: number, messageId: number): Promise<void> => {
    const response = await api.delete<ApiResponse<void>>(API_ENDPOINTS.DELETE_MESSAGE(topicId, messageId))

    if (!response.data.success) {
        throw new Error(response.data.error?.message || '메시지 삭제에 실패했습니다.')
    }
}
```

---

## 4. 아티팩트 API (`/api/artifacts`)

**구현 파일**: `frontend/src/services/artifactApi.ts`

| Method | Endpoint                                | FE 상태 | BE 상태 | 비고                            |
| ------ | --------------------------------------- | ------- | ------- | ------------------------------- |
| GET    | `/api/artifacts/{artifact_id}`          | ✅      | 🟢      | 아티팩트 메타데이터 조회        |
| GET    | `/api/artifacts/{artifact_id}/content`  | ✅      | 🟢      | MD 파일 내용 조회               |
| GET    | `/api/artifacts/{artifact_id}/download` | ✅      | 🟢      | 파일 다운로드 (브라우저 트리거) |
| GET    | `/api/artifacts/topics/{topic_id}`      | ✅      | 🟢      | 토픽의 아티팩트 목록 조회       |
| POST   | `/api/artifacts/{artifact_id}/convert`  | ✅      | 🔴      | **BE 미구현** (501 에러) ⚠️     |

**구현률**:

- 프론트엔드: 100% (5/5) ✅
- 백엔드: 80% (4/5) - **convert만 미구현** ⚠️

### ⚠️ 중요: Convert API 미구현 문제

**`POST /api/artifacts/{artifact_id}/convert`**

- **현재 상태**: 백엔드 엔드포인트는 존재하나 실제 변환 로직 미구현
- **에러 코드**: `SERVER.SERVICE_UNAVAILABLE` (501)
- **에러 메시지**: "변환 기능은 아직 구현되지 않았습니다."
- **파일 위치**: `backend/app/routers/artifacts.py:419-426`

```python
# TODO: Implement actual conversion logic in Phase 6
# This is a placeholder response
return error_response(
    code=ErrorCode.SERVER_SERVICE_UNAVAILABLE,
    http_status=501,
    message="변환 기능은 아직 구현되지 않았습니다.",
    hint="Phase 6에서 구현 예정입니다."
)
```

**영향**:

- 프론트엔드 다운로드 버튼 클릭 시 에러 발생
- MD → HWPX 변환 불가능
- 사용자는 MD 파일만 다운로드 가능

**해결 방안**:

1. **백엔드 convert API 구현** (권장)
    - `app/utils/hwp_handler.py`에 변환 로직 구현
    - MD 파일을 파싱하여 HWPX 생성

2. **임시 해결책** (프론트엔드)
    - convert API 호출 실패 시 MD 파일 그대로 다운로드
    - 사용자에게 "HWPX 변환 기능 준비 중" 안내

**특이사항**:

- `downloadArtifact`: `fallbackFilename` 파라미터 추가로 확장자 문제 해결
- 프론트엔드 다운로드 플로우는 완벽하게 구현됨 (백엔드만 완성 필요)

**최근 개선사항** (2025-10-30):

- 다운로드 버튼 클릭 시 MD → HWPX 변환 후 다운로드하도록 수정
    - `handleDownload()` → `convertToHwpx()` → `downloadArtifact()`
    - 변환 진행 중 로딩 메시지 표시
    - ⚠️ 단, 백엔드 convert 미구현으로 실제 동작 안 함

---

## 5. 관리자 API (`/api/admin`)

**구현 파일**: `frontend/src/services/adminApi.ts`

| Method | Endpoint                                    | FE 상태 | BE 상태 | 비고                        |
| ------ | ------------------------------------------- | ------- | ------- | --------------------------- |
| GET    | `/api/admin/users`                          | ✅      | 🟢      | 전체 사용자 목록 조회       |
| PATCH  | `/api/admin/users/{user_id}/approve`        | ✅      | 🟢      | 사용자 승인                 |
| PATCH  | `/api/admin/users/{user_id}/reject`         | ✅      | 🟢      | 사용자 거부                 |
| POST   | `/api/admin/users/{user_id}/reset-password` | ✅      | 🟢      | 비밀번호 초기화             |
| GET    | `/api/admin/token-usage`                    | ❌      | 🟢      | **FE 미구현** (BE는 구현됨) |
| GET    | `/api/admin/token-usage/{user_id}`          | ❌      | 🟢      | **FE 미구현** (BE는 구현됨) |

**구현률**:

- 프론트엔드: 67% (4/6)
- 백엔드: 100% (6/6) ✅

### 미구현 API 상세

#### `GET /api/admin/token-usage`

전체 사용자의 AI 토큰 사용량을 조회합니다.

**필요성**:

- 비용 관리 및 모니터링
- 사용량 통계 대시보드

**구현 예시**:

```typescript
interface TokenUsageStats {
    total_input_tokens: number
    total_output_tokens: number
    total_cost: number
    users: Array<{
        user_id: number
        username: string
        input_tokens: number
        output_tokens: number
    }>
}

getTokenUsage: async (): Promise<TokenUsageStats> => {
    const response = await api.get<ApiResponse<TokenUsageStats>>(API_ENDPOINTS.TOKEN_USAGE)

    if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error?.message || '토큰 사용량 조회에 실패했습니다.')
    }

    return response.data.data
}
```

#### `GET /api/admin/token-usage/{user_id}`

특정 사용자의 AI 토큰 사용량을 조회합니다.

**구현 예시**:

```typescript
getUserTokenUsage: async (userId: number): Promise<TokenUsageStats> => {
    const response = await api.get<ApiResponse<TokenUsageStats>>(API_ENDPOINTS.USER_TOKEN_USAGE(userId))

    if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error?.message || '사용자 토큰 사용량 조회에 실패했습니다.')
    }

    return response.data.data
}
```

---

## 6. 보고서 API (`/api/reports`) 🗑️ Deprecated

**구현 파일**: `frontend/src/services/reportApi.ts`

| Method | Endpoint                            | FE 상태 | BE 상태 | 비고                                  |
| ------ | ----------------------------------- | ------- | ------- | ------------------------------------- |
| POST   | `/api/reports/generate`             | ✅      | 🟢      | v1.0 단일 보고서 생성 (Deprecated)    |
| GET    | `/api/reports/my-reports`           | ✅      | 🟢      | v1.0 보고서 목록 조회 (Deprecated)    |
| GET    | `/api/reports/download/{report_id}` | ⚠️      | 🟢      | 다운로드 URL만 반환 (실제 fetch 없음) |

**구현률**:

- 프론트엔드: 100% (3/3)
- 백엔드: 100% (3/3)

**⚠️ 중요**:

- v1.0 호환성 유지를 위해 구현되었으나, **v2.0에서는 사용하지 않습니다.**
- 새로운 코드에서는 **Topics/Messages/Artifacts API를 사용**해야 합니다.
- 향후 제거 예정

---

## 전체 요약

### 프론트엔드 구현률

| API 카테고리         | FE 구현률 | BE 구현률 | 구현/전체 | 상태                    |
| -------------------- | --------- | --------- | --------- | ----------------------- |
| 인증 (Auth)          | 80%       | 100%      | 4/5       | 🟡 FE 개선 필요         |
| 토픽 (Topics)        | 100%      | 100%      | 6/6       | 🟢 완벽                 |
| 메시지 (Messages)    | 50%       | 100%      | 2/4       | 🟡 FE 개선 필요         |
| 아티팩트 (Artifacts) | 100%      | 80%       | 5/5       | 🔴 BE convert 미구현 ⚠️ |
| 관리자 (Admin)       | 67%       | 100%      | 4/6       | 🟡 FE 개선 필요         |
| 보고서 (Reports)     | 100%      | 100%      | 3/3       | 🗑️ Deprecated           |

**전체 구현률**:

- 프론트엔드: 83% (24/29) ⬆️
- 백엔드: 97% (28/29) - **Artifacts convert만 미구현** ⚠️

---

## 우선순위별 구현 권장사항

### 🔴 Critical Priority (긴급 구현 필요)

1. **`POST /api/artifacts/{artifact_id}/convert` - 백엔드** (MD → HWPX 변환)
    - **현재 상태**: 501 에러 (미구현)
    - **영향**: 다운로드 기능 전체 차단
    - **위치**: `backend/app/routers/artifacts.py:419-426`
    - **필요 작업**: `app/utils/hwp_handler.py`에 변환 로직 구현
    - **영향도**: 🔴 매우 높음 (핵심 기능)

### 🔴 High Priority (즉시 구현 필요 - 프론트엔드)

2. **`GET /api/auth/me`** (현재 사용자 정보 조회)
    - 토큰 유효성 검증
    - 페이지 새로고침 시 로그인 상태 유지
    - 백엔드 구현 완료 ✅
    - **영향도**: 높음 (사용자 경험)

### 🟡 Medium Priority (기능 개선 시 구현)

3. **`DELETE /api/topics/{topic_id}/messages/{message_id}`** (메시지 삭제)
    - 대화 관리 기능
    - **영향도**: 중간 (사용성)

4. **`GET /api/admin/token-usage`** (토큰 사용량 조회)
    - 비용 모니터링
    - **영향도**: 중간 (관리)

### 🟢 Low Priority (선택적 구현)

5. **`GET /api/topics/{topic_id}/messages/{message_id}`** (특정 메시지 조회)
    - 현재는 목록 조회로 충분
    - **영향도**: 낮음

6. **`GET /api/admin/token-usage/{user_id}`** (사용자별 토큰 사용량)
    - 관리 기능 강화
    - **영향도**: 낮음

---

## API 엔드포인트 상수 관리

**파일**: `frontend/src/constants/index.ts`

프론트엔드의 모든 API 엔드포인트는 `constants/index.ts`에서 중앙 관리됩니다.

### 필요한 추가 상수

```typescript
// Auth
ME: '/api/auth/me',
LOGOUT: '/api/auth/logout',

// Messages
GET_MESSAGE: (topicId: number, messageId: number) =>
  `/api/topics/${topicId}/messages/${messageId}`,
DELETE_MESSAGE: (topicId: number, messageId: number) =>
  `/api/topics/${topicId}/messages/${messageId}`,

// Admin
TOKEN_USAGE: '/api/admin/token-usage',
USER_TOKEN_USAGE: (userId: number) => `/api/admin/token-usage/${userId}`,
```

---

## 변경 이력

### 2025-10-30 (v3)

- **로그아웃 API 구현 완료** ✨
    - `POST /api/auth/logout` 프론트엔드 구현
    - `authApi.logout()`: 백엔드 API 호출 + 로컬 토큰 삭제
    - `AuthContext.logout()`: async로 변경, API 호출 추가
    - `Sidebar.handleLogout()`: async/await 적용, 에러 처리
    - Auth API 구현률: 60% → 80% (4/5)
    - 전체 프론트엔드 구현률: 80% → 83% (24/29)

### 2025-10-30 (v2)

- **백엔드 API 구현 상태 추가**
    - 모든 API 테이블에 "BE 상태" 열 추가
    - 백엔드 구현률 분석 완료
    - **중요 발견**: `POST /api/artifacts/{artifact_id}/convert` 백엔드 미구현 (501 에러)
- **프론트엔드 구현 현황**
    - Auth API: 백엔드 100% 구현됨, 프론트 60% (GET /me, POST /logout 미구현)
    - Topics API: 양쪽 모두 100% 완벽 구현 ✨
    - Messages API: 백엔드 100% 구현됨, 프론트 50% (GET/DELETE message 미구현)
    - Artifacts API: 프론트 100%, **백엔드 80%** (convert만 미구현) ⚠️
    - Admin API: 백엔드 100% 구현됨, 프론트 67% (token-usage 미구현)
- **우선순위 재조정**
    - 🔴 Critical: convert API 백엔드 구현 (긴급)
    - 🔴 High: Auth API 프론트엔드 구현 (GET /me, POST /logout)

### 2025-10-30 (v1)

- 다운로드 버튼 동작 개선: MD → HWPX 변환 후 다운로드
- `artifactApi.downloadArtifact()`: `fallbackFilename` 파라미터 추가
- `MainChatPage.handleDownload()`: convert API 활용하도록 수정
- `ChatMessage.tsx`: reportData 있을 때 간결한 메시지 표시

### 2025-10-28

- 초기 API 구현 현황 정리 (프론트엔드만)
- v2.0 대화형 시스템 전환 완료
- Topics/Messages/Artifacts API 100% 구현 (프론트엔드)

---

## 참고 문서

- **백엔드 API 스펙**: `BACKEND_ONBOARDING.md`
- **프로젝트 가이드**: `CLAUDE.md`
- **프론트엔드 가이드**: `FRONTEND_ONBOARDING.md`
