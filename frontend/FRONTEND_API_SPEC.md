# Frontend API 통신 명세서

프론트엔드에서 백엔드와 통신할 때 사용하는 모든 API 엔드포인트와 데이터 형식을 정리한 문서입니다.

## 📋 목차

- [공통 응답 형식](#공통-응답-형식)
- [1. Topic API](#1-topic-api)
- [2. Message API](#2-message-api)
- [3. Artifact API](#3-artifact-api)
- [4. Report API (Legacy)](#4-report-api-legacy)

---

## 공통 응답 형식

모든 API는 표준화된 응답 형식을 사용합니다.

### 성공 응답

```typescript
{
  success: true,
  data: T,  // 실제 데이터
  error: null,
  meta: {
    requestId: string  // 요청 추적용 ID
  },
  feedback: []  // 사용자 피드백 (선택)
}
```

### 실패 응답

```typescript
{
  success: false,
  data: null,
  error: {
    code: string,           // 에러 코드 (예: "AUTH.INVALID_TOKEN")
    httpStatus: number,     // HTTP 상태 코드
    message: string,        // 사용자용 에러 메시지
    details?: object,       // 추가 에러 정보 (선택)
    traceId: string,        // 에러 추적용 ID
    hint?: string          // 해결 방법 힌트 (선택)
  },
  meta: {
    requestId: string
  },
  feedback: []
}
```

---

## 1. Topic API

토픽(대화 스레드) 관련 API

### 1.1 토픽 생성 + AI 보고서 자동 생성

**첫 번째 메시지에서 사용**: 토픽 생성과 동시에 AI가 보고서를 자동 생성합니다.

```
POST /api/topics/generate
```

**Request Body:**

```typescript
{
  input_prompt: string,   // 사용자 입력 (보고서 주제)
  language?: string       // 언어 (기본값: "ko")
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    topic_id: number,     // 생성된 토픽 ID
    md_path: string       // 생성된 MD 파일 경로
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

**사용 예시:**

```typescript
const response = await topicApi.generateTopic({
    input_prompt: '2024년 디지털 뱅킹 트렌드 분석',
    language: 'ko'
})
// response.topic_id로 토픽 ID 획득
```

---

### 1.2 토픽 생성 (AI 응답 없이)

```
POST /api/topics
```

**Request Body:**

```typescript
{
  input_prompt: string,
  language?: string
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    id: number,
    input_prompt: string,
    generated_title: string | null,
    language: string,
    status: "active" | "archived" | "deleted",
    created_at: string,    // ISO 8601 형식
    updated_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 1.3 토픽 목록 조회

```
GET /api/topics?status=active&page=1&page_size=20
```

**Query Parameters:**

- `status` (optional): "active" | "archived" | "deleted"
- `page` (optional): 페이지 번호 (기본값: 1)
- `page_size` (optional): 페이지 크기 (기본값: 20)

**Response (200):**

```typescript
{
  success: true,
  data: {
    topics: [
      {
        id: number,
        input_prompt: string,
        generated_title: string | null,
        language: string,
        status: "active" | "archived" | "deleted",
        created_at: string,
        updated_at: string
      }
    ],
    total: number,        // 전체 토픽 개수
    page: number,         // 현재 페이지
    page_size: number     // 페이지 크기
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 1.4 특정 토픽 조회

```
GET /api/topics/{topicId}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    id: number,
    input_prompt: string,
    generated_title: string | null,
    language: string,
    status: "active" | "archived" | "deleted",
    created_at: string,
    updated_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 1.5 토픽 업데이트

```
PATCH /api/topics/{topicId}
```

**Request Body:**

```typescript
{
  generated_title?: string,
  status?: "active" | "archived" | "deleted"
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    id: number,
    input_prompt: string,
    generated_title: string | null,
    language: string,
    status: "active" | "archived" | "deleted",
    created_at: string,
    updated_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 1.6 토픽 삭제

```
DELETE /api/topics/{topicId}
```

**Response (200):**

```typescript
{
  success: true,
  data: null,
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 1.7 메시지 체이닝 (대화 이어가기)

**두 번째 메시지부터 사용**: 기존 토픽에 새 메시지를 추가하고 AI 응답을 받습니다.

```
POST /api/topics/{topicId}/ask
```

**Request Body:**

```typescript
{
  content: string,                    // 사용자 메시지 (필수)
  artifact_id?: number | null,        // 참조할 아티팩트 ID (선택)
  include_artifact_content?: boolean, // 아티팩트 내용 포함 여부 (선택)
  max_messages?: number | null,       // 컨텍스트 메시지 최대 개수 (선택)
  system_prompt?: string | null       // 커스텀 시스템 프롬프트 (선택)
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    topic_id: number,
    user_message: {
      id: number,
      topic_id: number,
      role: "user",
      content: string,
      seq_no: number,
      created_at: string
    },
    assistant_message: {
      id: number,
      topic_id: number,
      role: "assistant",
      content: string,
      seq_no: number,
      created_at: string
    },
    artifact: {
      id: number,
      kind: "md" | "hwpx" | "pdf",
      filename: string,
      file_path: string,
      file_size: number,
      version: number,
      created_at: string
    },
    usage: {
      model: string,
      input_tokens: number,
      output_tokens: number,
      latency_ms: number
    }
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

**사용 예시:**

```typescript
// 2번째 메시지부터
const response = await topicApi.askTopic(topicId, {
    content: '좀 더 자세히 설명해줘'
})
```

---

## 2. Message API

메시지 관련 API

### 2.1 토픽의 메시지 목록 조회

```
GET /api/topics/{topicId}/messages?limit=50&offset=0
```

**Query Parameters:**

- `limit` (optional): 최대 메시지 수
- `offset` (optional): 건너뛸 메시지 수 (기본값: 0)

**Response (200):**

```typescript
{
  success: true,
  data: {
    messages: [
      {
        id: number,
        topic_id: number,
        user_id: number | null,
        role: "user" | "assistant" | "system",
        content: string,
        seq_no: number,         // 메시지 순서 번호
        created_at: string
      }
    ],
    total: number,              // 전체 메시지 개수
    topic_id: number
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

**사용 예시:**

```typescript
const response = await messageApi.listMessages(topicId)
// response.messages 배열 사용
```

---

### 2.2 새 메시지 생성 (Legacy)

**주의**: 이 API는 Legacy입니다. 대신 `/api/topics/{topicId}/ask`를 사용하세요.

```
POST /api/topics/{topicId}/messages
```

**Request Body:**

```typescript
{
  role: "user" | "assistant" | "system",
  content: string
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    id: number,
    topic_id: number,
    user_id: number | null,
    role: "user" | "assistant" | "system",
    content: string,
    seq_no: number,
    created_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

## 3. Artifact API

아티팩트(산출물: MD, HWPX 파일) 관련 API

### 3.1 아티팩트 메타데이터 조회

```
GET /api/artifacts/{artifactId}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    id: number,
    topic_id: number,
    message_id: number | null,
    kind: "md" | "hwpx" | "pdf",
    locale: string | null,
    version: number,
    filename: string,
    file_path: string,
    file_size: number,
    sha256: string | null,
    created_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 3.2 아티팩트 내용 조회 (MD 파일만)

```
GET /api/artifacts/{artifactId}/content
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    artifact_id: number,
    content: string,          // MD 파일 텍스트 내용
    filename: string,
    kind: "md"
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

**사용 예시:**

```typescript
// 보고서 미리보기용 MD 내용 가져오기
const response = await artifactApi.getArtifactContent(artifactId)
// response.content를 화면에 표시
```

---

### 3.3 아티팩트 파일 다운로드

```
GET /api/artifacts/{artifactId}/download
```

**Response (200):**

- Content-Type: `text/markdown`, `application/x-hwpx`, 또는 `application/pdf`
- Content-Disposition: `attachment; filename="..."`
- 파일 바이너리 데이터

**사용 예시:**

```typescript
// 브라우저에서 파일 다운로드
await artifactApi.downloadArtifact(artifactId, filename)
```

---

### 3.4 메시지 기반 HWPX 다운로드 (자동 생성) ⭐

**권장**: 이 API를 사용하여 HWPX 파일을 다운로드하세요.

```
GET /api/artifacts/messages/{messageId}/hwpx/download?locale=ko
```

**Query Parameters:**

- `locale` (optional): 언어 (기본값: "ko")

**Response (200):**

- Content-Type: `application/x-hwpx`
- Content-Disposition: `attachment; filename="..."`
- HWPX 파일 바이너리 데이터

**동작 방식:**

1. 백엔드에서 해당 메시지의 HWPX 아티팩트가 있는지 확인
2. 있으면 캐시된 파일 반환
3. 없으면 MD 아티팩트를 HWPX로 자동 변환 후 반환

**사용 예시:**

```typescript
// 다운로드 버튼 클릭 시
await artifactApi.downloadMessageHwpx(messageId, 'report.hwpx', 'ko')
```

---

### 3.5 토픽의 아티팩트 목록 조회

```
GET /api/artifacts/topics/{topicId}?kind=md&locale=ko&page=1&page_size=50
```

**Query Parameters:**

- `kind` (optional): "md" | "hwpx" | "pdf"
- `locale` (optional): "ko" | "en"
- `page` (optional): 페이지 번호 (기본값: 1)
- `page_size` (optional): 페이지 크기 (기본값: 50)

**Response (200):**

```typescript
{
  success: true,
  data: {
    artifacts: [
      {
        id: number,
        topic_id: number,
        message_id: number | null,
        kind: "md" | "hwpx" | "pdf",
        locale: string | null,
        version: number,
        filename: string,
        file_path: string,
        file_size: number,
        sha256: string | null,
        created_at: string
      }
    ],
    total: number,
    topic_id: number
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

**사용 예시:**

```typescript
// 토픽의 모든 아티팩트 가져오기
const response = await artifactApi.listArtifactsByTopic(topicId)
// response.artifacts 배열 사용
```

---

### 3.6 MD 아티팩트를 HWPX로 변환 (수동)

**주의**: 일반적으로는 3.4의 메시지 기반 다운로드를 사용하세요.

```
POST /api/artifacts/{artifactId}/convert
```

**Request Body:** 없음

**Response (200):**

```typescript
{
  success: true,
  data: {
    artifact_id: number,      // 새로 생성된 HWPX 아티팩트 ID
    kind: "hwpx",
    filename: string,
    file_path: string,
    file_size: number,
    created_at: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

## 4. Report API (Legacy)

**주의**: 이 API들은 Legacy입니다. 새로운 Topic/Artifact API를 사용하세요.

### 4.1 보고서 생성

```
POST /api/generate
```

**Request Body:**

```typescript
{
    topic: string
}
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    success: boolean,
    message: string,
    file_path?: string,
    filename?: string
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 4.2 보고서 목록 조회

```
GET /api/reports
```

**Response (200):**

```typescript
{
  success: true,
  data: {
    reports: [
      {
        filename: string,
        size: number,
        created: number
      }
    ]
  },
  error: null,
  meta: { requestId: string },
  feedback: []
}
```

---

### 4.3 보고서 다운로드

```
GET /api/download/{filename}
```

**Response (200):**

- 파일 바이너리 데이터

---

## 🔄 일반적인 사용 흐름

### 첫 번째 메시지 (토픽 생성)

```typescript
// 1. 토픽 생성 + AI 보고서 자동 생성
const generateResponse = await topicApi.generateTopic({
    input_prompt: '디지털 뱅킹 트렌드',
    language: 'ko'
})
const topicId = generateResponse.topic_id

// 2. 메시지 목록 조회 (AI 응답 포함)
const messagesResponse = await messageApi.listMessages(topicId)

// 3. 아티팩트 목록 조회 (보고서 파일)
const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)

// 4. MD 파일 내용 가져오기 (미리보기용)
const contentResponse = await artifactApi.getArtifactContent(artifactsResponse.artifacts[0].id)
```

### 두 번째 메시지부터 (메시지 체이닝)

```typescript
// 1. 메시지 체이닝 (대화 이어가기)
const askResponse = await topicApi.askTopic(topicId, {
    content: '좀 더 자세히 설명해줘'
})

// 2. 메시지 목록 재조회 (업데이트된 대화 내용)
const messagesResponse = await messageApi.listMessages(topicId)

// 3. 아티팩트 목록 재조회
const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)
```

### HWPX 다운로드

```typescript
// 메시지 ID로 HWPX 다운로드 (자동 생성)
await artifactApi.downloadMessageHwpx(messageId, 'report.hwpx', 'ko')
```

---

## 📝 에러 코드

자주 발생하는 에러 코드:

| 코드                         | HTTP Status | 의미                      |
| ---------------------------- | ----------- | ------------------------- |
| `AUTH.INVALID_TOKEN`         | 401         | 인증 토큰이 유효하지 않음 |
| `AUTH.TOKEN_EXPIRED`         | 401         | 토큰이 만료됨             |
| `AUTH.UNAUTHORIZED`          | 403         | 권한 없음                 |
| `TOPIC.NOT_FOUND`            | 404         | 토픽을 찾을 수 없음       |
| `TOPIC.UNAUTHORIZED`         | 403         | 토픽 접근 권한 없음       |
| `MESSAGE.NOT_FOUND`          | 404         | 메시지를 찾을 수 없음     |
| `ARTIFACT.NOT_FOUND`         | 404         | 아티팩트를 찾을 수 없음   |
| `ARTIFACT.INVALID_KIND`      | 400         | 잘못된 아티팩트 타입      |
| `ARTIFACT.DOWNLOAD_FAILED`   | 500         | 파일 다운로드 실패        |
| `ARTIFACT.CONVERSION_FAILED` | 500         | HWPX 변환 실패            |
| `VALIDATION.INVALID_FORMAT`  | 400         | 유효하지 않은 데이터 형식 |
| `SERVER.DATABASE_ERROR`      | 500         | 데이터베이스 오류         |
| `SERVER.INTERNAL_ERROR`      | 500         | 서버 내부 오류            |

---

## 🔐 인증

모든 API 호출에는 JWT 토큰이 필요합니다 (로그인/회원가입 제외).

**헤더:**

```
Authorization: Bearer {access_token}
```

**토큰 저장:**

```typescript
localStorage.getItem('access_token')
```

---

## 📌 타입 정의 위치

- **공통 타입**: `frontend/src/types/api.ts`
- **Topic 타입**: `frontend/src/types/topic.ts`
- **Message 타입**: `frontend/src/types/message.ts`
- **Artifact 타입**: `frontend/src/types/artifact.ts`
- **Report 타입**: `frontend/src/types/report.ts`

---

## 🛠️ API 클라이언트

- **Base Client**: `frontend/src/services/api.ts` (Axios 인스턴스)
- **Topic API**: `frontend/src/services/topicApi.ts`
- **Message API**: `frontend/src/services/messageApi.ts`
- **Artifact API**: `frontend/src/services/artifactApi.ts`
- **Report API**: `frontend/src/services/reportApi.ts` (Legacy)

---

**문서 생성일**: 2025-01-30
**버전**: 1.0.0
