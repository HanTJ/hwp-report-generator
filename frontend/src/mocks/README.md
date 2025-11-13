# MSW (Mock Service Worker) 사용 가이드

## 현재 Mock 처리되는 API

### 🔵 Mocked APIs (MSW Intercept)

| Method | Endpoint | 설명 | Handler 위치 |
|--------|----------|------|-------------|
| POST | `/api/outlines/ask` | 개요 생성 API | `handlers.ts:19` |

### ⚪ Passthrough APIs (실제 Backend 호출)

- `POST /api/topics/generate` - 보고서 생성
- `GET /api/topics` - 토픽 목록
- `POST /api/topics/{topic_id}/ask` - 메시지 전송
- 기타 모든 API

---

## 코드에서 확인하는 방법

### 1. handlers.ts 파일 직접 확인

```typescript
// frontend/src/mocks/handlers.ts
export const handlers = [
  http.post('/api/outlines/ask', ...),  // ← 이 API들이 mock됨
  // 더 추가하려면 여기에 작성
]
```

### 2. 헬퍼 함수 사용

```typescript
import { getMockedEndpoints, isMockedEndpoint } from './mocks/handlers'

// 모든 mock API 목록
const mockApis = getMockedEndpoints()
console.log(mockApis)
// ['POST /api/outlines/ask']

// 특정 API가 mock되는지 확인
const isMocked = isMockedEndpoint('POST', '/api/outlines/ask')
console.log(isMocked) // true
```

### 3. 브라우저 콘솔에서 확인

개발 서버 실행 후 브라우저 콘솔(F12)에서:

```javascript
// Mock API 목록 출력
window.listMockAPIs()

// MSW worker 제어
window.mswWorker.start()  // 시작
window.mswWorker.stop()   // 중지
```

### 4. Network 탭에서 확인

F12 → Network 탭

- **Mock API**: `(from service worker)` 표시
- **실제 API**: `localhost:8000` 표시

---

## 새로운 Mock API 추가 방법

### 예시: GET /api/users mock 추가

```typescript
// frontend/src/mocks/handlers.ts

export const handlers = [
  // 기존 handlers...
  
  /**
   * Mock: 사용자 목록 조회
   * GET /api/users
   */
  http.get('/api/users', async () => {
    await delay(300) // 300ms 지연
    
    return HttpResponse.json({
      success: true,
      data: [
        { id: 1, name: '홍길동' },
        { id: 2, name: '김철수' }
      ]
    })
  }),
  
  /**
   * Mock: 사용자 생성
   * POST /api/users
   */
  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    
    return HttpResponse.json({
      success: true,
      data: {
        id: 999,
        ...body
      }
    })
  })
]
```

### 동적 경로 파라미터

```typescript
// GET /api/users/:id
http.get('/api/users/:id', async ({ params }) => {
  const { id } = params
  
  return HttpResponse.json({
    success: true,
    data: {
      id: Number(id),
      name: `사용자${id}`
    }
  })
})
```

---

## Mock 비활성화 방법

### 1. 전체 MSW 비활성화

```typescript
// frontend/src/main.tsx

async function enableMocking() {
  // return  // ← 주석 해제하면 MSW 비활성화
  
  if (import.meta.env.MODE !== 'development') {
    return
  }
  // ...
}
```

### 2. 특정 API만 비활성화

```typescript
// frontend/src/mocks/handlers.ts

export const handlers = [
  // http.post('/api/outlines/ask', ...),  // ← 주석 처리
]
```

### 3. 런타임에서 비활성화

브라우저 콘솔:

```javascript
window.mswWorker.stop()
```

---

## 에러 응답 시뮬레이션

### 500 에러

```typescript
http.post('/api/outlines/ask', () => {
  return HttpResponse.json(
    { error: 'Internal Server Error' },
    { status: 500 }
  )
})
```

### 401 인증 에러

```typescript
http.get('/api/users', () => {
  return HttpResponse.json(
    { error: 'Unauthorized' },
    { status: 401 }
  )
})
```

### 조건부 에러

```typescript
http.post('/api/outlines/ask', async ({ request }) => {
  const body = await request.json()
  
  // 특정 조건에서만 에러
  if (!body.userMessage) {
    return HttpResponse.json(
      { error: 'userMessage is required' },
      { status: 400 }
    )
  }
  
  // 정상 응답
  return HttpResponse.json({ ... })
})
```

---

## 프로덕션 빌드

프로덕션 빌드 시 MSW는 자동으로 제외됩니다:

```typescript
// main.tsx
if (import.meta.env.MODE !== 'development') {
  return  // 프로덕션에서는 MSW 실행 안 함
}
```

**빌드 파일 확인:**
```bash
npm run build
# dist/ 폴더에 mockServiceWorker.js 포함되지 않음
```

---

## 디버깅 팁

### 1. MSW 로그 활성화

```typescript
// frontend/src/mocks/browser.ts

worker.start({
  onUnhandledRequest: 'warn',  // mock 안 된 요청 경고
  quiet: false  // 모든 요청 로그 출력
})
```

### 2. 요청/응답 로그

```typescript
http.post('/api/outlines/ask', async ({ request }) => {
  const body = await request.json()
  
  console.log('📥 Request:', body)
  
  const response = { /* ... */ }
  
  console.log('📤 Response:', response)
  
  return HttpResponse.json(response)
})
```

### 3. Network 탭 확인

F12 → Network 탭 → Type 필터: `fetch`

- MSW: `(from service worker)`
- 실제: `xhr` 또는 `fetch`

---

## 참고 자료

- [MSW 공식 문서](https://mswjs.io/docs/)
- [MSW GitHub](https://github.com/mswjs/msw)
- [프로젝트 SPEC](../doc/spec/MESSAGE_SPEC.md)
- [테스트 가이드](../doc/OUTLINE_FLOW_TEST_GUIDE.md)

---

**작성일:** 2025-11-12  
**버전:** 1.0
