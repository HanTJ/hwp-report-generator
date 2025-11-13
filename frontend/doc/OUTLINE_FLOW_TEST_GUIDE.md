# Outline Flow 테스트 가이드

## 개요

Outline 모드에서 "예" 클릭 전까지의 메시지는 Backend DB에 저장되지 않습니다.
이 문서는 Backend 구현 없이 Frontend에서 Outline 플로우를 테스트하는 방법을 설명합니다.

## 테스트 전략

### MSW (Mock Service Worker) 활용

MSW를 사용하여 Outline API와 Messages API를 mock 처리합니다.

**핵심 아이디어:**
1. Outline 대화 메시지를 `pendingMessagesByTopic` (메모리)에 임시 저장
2. 임시 topicId (음수)로 관리하여 여러 대화 동시 테스트 가능
3. "예" 클릭 → `generateTopic` (실제 API) → 실제 topicId 발급
4. `fetchMessages` 호출 시 pending 메시지를 실제 topicId 메시지와 합쳐서 반환

## 테스트 시나리오

### 1. 첫 Outline 대화 시작

**사용자 액션:**
```
1. 메인 페이지 접속
2. "보고서 개요부터 작성" 모드 선택
3. 메시지 입력: "디지털뱅킹 트렌드 보고서 작성해줘"
```

**MSW 동작:**
```typescript
POST /api/outlines/ask
→ tempTopicId: -1 생성
→ pendingMessagesByTopic에 저장:
  - User 메시지 (seqNo: 0)
  - Assistant 개요 (seqNo: 1)
→ 응답: { id: -1, outline: "..." }
```

**Frontend 동작:**
```typescript
// MainPage.tsx
const outlineMessages = [
  { role: 'user', content: '...', seqNo: 0, topicId: -1 },
  { role: 'assistant', content: '개요...', seqNo: 1, topicId: -1, isOutline: true }
]
// Zustand에 로컬 메시지로 저장 (fetchMessages X)
```

### 2. Outline 대화 계속

**사용자 액션:**
```
"아니오" 클릭 → 추가 요청 입력
```

**MSW 동작:**
```typescript
POST /api/outlines/ask (id: -1)
→ 기존 tempTopicId -1 사용
→ pendingMessagesByTopic[-1]에 추가:
  - User 메시지 (seqNo: 2)
  - Assistant 개요 (seqNo: 3)
```

**Frontend 동작:**
```typescript
// 로컬 메시지만 업데이트
outlineMessages.push(newUserMsg, newAssistantMsg)
```

### 3. 보고서 생성 ("예" 클릭)

**사용자 액션:**
```
"예" 클릭
```

**Backend API 동작:**
```typescript
POST /api/topics/generate (Real API)
→ Backend에서 실제 topicId 생성: 123
→ 보고서 생성 후 반환
```

**Frontend 동작:**
```typescript
// MainPage.tsx
1. generateTopic() 호출
2. response.topic_id = 123 받음
3. setSelectedTopicId(123)
4. useEffect → fetchMessages(123) 자동 호출
```

**MSW 동작:**
```typescript
GET /api/topics/123/messages (Mock)
→ pendingMessagesByTopic[-1] 가져오기
→ Backend 메시지 (보고서)와 합치기
→ 반환:
  [
    { id: 1, topic_id: 123, role: 'user', content: '...', seq_no: 0 },
    { id: 2, topic_id: 123, role: 'assistant', content: '개요...', seq_no: 1 },
    { id: 3, topic_id: 123, role: 'assistant', content: '보고서...', seq_no: 2, report_data: {...} }
  ]
→ pendingMessagesByTopic[-1] 삭제 (소비됨)
```

## 디버깅 도구

### 브라우저 콘솔

```javascript
// Mock API 목록 확인
window.listMockAPIs()
// 출력:
// 🔵 MSW Mock APIs
//   POST /api/outlines/ask
//   GET /api/topics/:topicId/messages

// Pending 메시지 확인
window.pendingMessagesByTopic
// Map { -1 => [...], -2 => [...] }

// Mock 메시지 확인
window.mockTopicMessages
// Map { 123 => [...] }

// Pending 메시지 초기화
window.clearPendingMessages()
```

### MSW 로그

```
[MSW] Outline request - tempTopicId: -1, messages count: 2
[MSW] Outline request - tempTopicId: -1, messages count: 4
[MSW] Messages fetched for topicId: 123, count: 3
```

## 현재 제약사항

### Backend 미구현 부분

1. **Outline 메시지 저장:**
   - Backend가 구현되면 `/api/outlines/ask`가 실제로 메시지를 저장해야 함
   - 현재는 MSW가 메모리에만 저장

2. **Topic-Pending 매핑:**
   - 현재는 "가장 최근 pending"을 사용
   - Backend 구현 시 tempTopicId와 realTopicId 매핑 필요

3. **Seq No 관리:**
   - Frontend에서 seqNo 계산 중
   - Backend 구현 시 서버에서 관리해야 함

## 테스트 체크리스트

- [ ] Outline 모드로 첫 대화 시작
- [ ] User/Assistant 메시지 정상 표시
- [ ] "아니오" 클릭 → 추가 대화 정상 동작
- [ ] 여러 번 대화 후에도 메시지 순서 유지
- [ ] "예" 클릭 → 보고서 생성
- [ ] 생성 후 fetchMessages로 전체 대화 표시
- [ ] Outline 메시지 + 보고서 메시지 모두 보임
- [ ] seqNo 순서대로 정렬되어 표시
- [ ] 사이드바에서 토픽 선택 시 정상 표시

## 다음 단계: Backend 구현

Backend 구현 시 필요한 API:

```python
# 1. Outline 메시지 저장 (DB)
POST /api/topics/{topic_id}/outline-messages
→ topic_id가 없으면 임시 저장
→ seqNo 자동 증가

# 2. Generate Topic 시 연결
POST /api/topics/generate
→ 임시 저장된 outline 메시지를 realTopicId와 연결
→ seqNo 유지

# 3. Messages 조회
GET /api/topics/{topic_id}/messages
→ Outline 메시지 + 일반 메시지 모두 반환
→ seqNo 순서로 정렬
```

## 참고 파일

- [frontend/src/mocks/handlers.ts](../src/mocks/handlers.ts) - MSW 핸들러
- [frontend/src/services/outlineApi.ts](../src/services/outlineApi.ts) - Outline API 서비스
- [frontend/src/pages/MainPage.tsx](../src/pages/MainPage.tsx) - Outline 플로우 구현
- [frontend/src/components/OutlineMessage.tsx](../src/components/OutlineMessage.tsx) - Outline 메시지 컴포넌트

---

**마지막 업데이트:** 2025-11-12
**작성자:** Claude Code
