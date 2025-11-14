# Message Fetch 로직 리팩토링 계획

**작성일**: 2025-11-14
**목적**: `fetchMessages` 분기 처리 및 `generateReportFromPlan` 후 메시지 유지 문제 해결

---

## 1. 문제 정의

### 현재 상황
- `generateReportFromPlan`에서 계획 메시지 + 서버 메시지를 `setMessages`로 설정
- `selectedTopicId` 변경 시 MainPage의 `useEffect`가 트리거
- `messages.length === 0` 판단으로 `fetchMessages` 호출
- `fetchMessages`가 서버에서 조회하여 **계획 메시지를 덮어씀**

### 근본 원인
- `fetchMessages`가 항상 `setMessages`로 **전체 교체**
- React 렌더링 지연으로 `messages.length === 0`으로 잘못 판단
- 대화 진행 중 vs 토픽 전환 시 구분 없음

---

## 2. 함수별 역할 분석

### 2.1 현재 함수들

| 함수 | 호출 시점 | 동작 | 문제점 |
|------|----------|------|--------|
| `fetchMessages` | 토픽 전환 시 | 서버 조회 → `setMessages` (전체 교체) | 계획 메시지 덮어씀 |
| `refreshMessages` | AI 응답 후, 삭제 후 | 서버 조회 → `setMessages` (전체 교체) | `fetchMessages`와 중복 |
| `addMessages` | 사용자 메시지 추가 | 기존 + 새 메시지 → `setMessages` | **중복 허용** (ID 체크 없음) |

### 2.2 addMessages vs 필요한 mergeNewMessages 차이

#### `addMessages` (기존)
```typescript
addMessages: (topicId, newMessages) => {
    const existing = newMap.get(topicId) || []
    newMap.set(topicId, [...existing, ...newMessages])  // 단순 추가 (중복 허용)
}
```
- **특징**: 중복 체크 없음 (사용자가 입력한 메시지는 항상 새로운 것이므로)
- **용도**: 사용자 메시지, 임시 메시지 추가

#### `mergeNewMessages` (신규 필요)
```typescript
mergeNewMessages: async (topicId) => {
    const serverMessages = await fetchFromServer()  // 서버에서 조회
    const existing = get().getMessages(topicId)

    // 중복 제거 (ID 기준)
    const existingIds = new Set(existing.map(m => m.id))
    const uniqueNew = serverMessages.filter(m => !existingIds.has(m.id))

    get().setMessages(topicId, [...existing, ...uniqueNew])  // 병합
}
```
- **특징**: 중복 체크 (ID 기반), artifact 연결 포함
- **용도**: 서버에서 새 메시지 가져와서 기존 메시지와 병합

**핵심 차이점**:
1. **서버 조회 여부**: `addMessages`는 파라미터로 받음, `mergeNewMessages`는 직접 조회
2. **중복 처리**: `addMessages`는 중복 허용, `mergeNewMessages`는 중복 제거
3. **Artifact 연결**: `addMessages`는 없음, `mergeNewMessages`는 포함

---

## 3. 최종 설계: 역할 기반 3개 함수

### 3.1 함수 정의

#### A. `loadMessages` (신규)
- **호출 시점**: 토픽 전환 (사이드바, 토픽 리스트)
- **동작**: 서버 조회 → `setMessages` (전체 교체)
- **용도**: 기존 대화 진입 시 전체 로드

```typescript
loadMessages: async (topicId: number) => {
    set({isLoadingMessages: true})
    try {
        // 1. 서버에서 메시지 조회
        const messagesResponse = await messageApi.listMessages(topicId)
        const messageModels = mapMessageResponsesToModels(messagesResponse.messages)

        // 2. Artifact 연결
        const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)
        const messagesWithArtifacts = await enrichMessagesWithArtifacts(
            messageModels,
            artifactsResponse.artifacts
        )

        // 3. 전체 교체
        get().setMessages(topicId, messagesWithArtifacts)
    } catch (error) {
        console.error('Failed to load messages:', error)
        antdMessage.error('메시지를 불러오는데 실패했습니다.')
    } finally {
        set({isLoadingMessages: false})
    }
}
```

#### B. `refreshMessages` (유지)
- **호출 시점**: AI 응답 후, 메시지 삭제 후
- **동작**: 서버 조회 → `setMessages` (전체 교체)
- **용도**: 현재 대화 새로고침

```typescript
// 기존 코드 유지 (loadMessages와 동일하지만 의미적으로 구분)
refreshMessages: async (topicId: number) => {
    // ... 기존 로직 유지
}
```

#### C. `mergeNewMessages` (신규)
- **호출 시점**: `generateReportFromPlan` 완료 후
- **동작**: 서버 조회 → 중복 제거 후 병합
- **용도**: 계획 메시지 유지하면서 서버 메시지 추가

```typescript
mergeNewMessages: async (topicId: number) => {
    try {
        // 1. 서버에서 메시지 + Artifact 조회
        const messagesResponse = await messageApi.listMessages(topicId)
        const messageModels = mapMessageResponsesToModels(messagesResponse.messages)

        const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId)
        const serverMessages = await enrichMessagesWithArtifacts(
            messageModels,
            artifactsResponse.artifacts
        )

        // 2. 기존 메시지 가져오기 (계획 메시지 포함)
        const existingMessages = get().getMessages(topicId)

        // 3. 중복 제거: ID가 없는 것만 추가
        const existingIds = new Set(
            existingMessages.filter(m => m.id).map(m => m.id)
        )
        const newMessages = serverMessages.filter(
            m => !m.id || !existingIds.has(m.id)
        )

        // 4. 병합 (기존 + 새 메시지)
        get().setMessages(topicId, [...existingMessages, ...newMessages])

        console.log('✅ mergeNewMessages 완료:', {
            existing: existingMessages.length,
            new: newMessages.length,
            total: existingMessages.length + newMessages.length
        })
    } catch (error) {
        console.error('Failed to merge messages:', error)
        // 에러 시에도 기존 메시지 유지
    }
}
```

### 3.2 함수 비교표

| 함수 | 서버 조회 | 동작 | 중복 처리 | Artifact | 용도 |
|------|----------|------|----------|----------|------|
| `loadMessages` | ✅ | 전체 교체 | N/A | ✅ | 토픽 전환 |
| `refreshMessages` | ✅ | 전체 교체 | N/A | ✅ | 새로고침 |
| `mergeNewMessages` | ✅ | 병합 | ID 기반 제거 | ✅ | 계획 후 병합 |
| `addMessages` | ❌ | 추가 | 중복 허용 | ❌ | 사용자 메시지 |

---

## 4. 구현 상세

### 4.1 useMessageStore.ts 수정

#### Interface 업데이트
```typescript
interface MessageStore {
    // ... 기존 필드

    // API Actions
    loadMessages: (topicId: number) => Promise<void>        // 신규
    refreshMessages: (topicId: number) => Promise<void>     // 유지
    mergeNewMessages: (topicId: number) => Promise<void>    // 신규
    fetchMessages: (topicId: number) => Promise<void>       // 삭제 예정 (deprecated)
}
```

#### 구현 순서
1. `loadMessages` 추가 (fetchMessages 복사 후 이름 변경)
2. `mergeNewMessages` 추가 (중복 제거 로직 포함)
3. `fetchMessages`를 `loadMessages`로 변경 (기존 호출 위치)
4. `fetchMessages` deprecated 처리 또는 삭제

### 4.2 MainPage.tsx 수정

#### Before
```typescript
useEffect(() => {
    if (selectedTopicId > 0 && messages.length === 0 && !skipFetchRef.current) {
        fetchMessages(selectedTopicId)  // 문제: 계획 메시지 덮어씀
    }

    if (skipFetchRef.current) {
        skipFetchRef.current = false
    }
}, [selectedTopicId])
```

#### After
```typescript
useEffect(() => {
    if (selectedTopicId !== null && selectedTopicId > 0) {
        // Zustand에서 직접 확인 (React 렌더링 지연 방지)
        const messageStore = useMessageStore.getState()
        const storedMessages = messageStore.getMessages(selectedTopicId)

        // Zustand에 메시지가 없을 때만 서버에서 로드
        if (storedMessages.length === 0) {
            loadMessages(selectedTopicId)  // 전체 로드
        }
    }
}, [selectedTopicId])
```

**변경 사항**:
- `messages.length` 대신 `storedMessages.length` 사용 (Zustand 직접 확인)
- `skipFetchRef` 제거 (불필요)
- `fetchMessages` → `loadMessages` 변경

### 4.3 useTopicStore.ts 수정 (generateReportFromPlan)

#### Before (라인 424-451)
```typescript
// 2. Backend에서 메시지 + Artifact 조회
const messagesResponse = await messageApi.listMessages(response.topic_id)
const artifactsResponse = await artifactApi.listArtifactsByTopic(response.topic_id)

const backendMessageModels = mapMessageResponsesToModels(messagesResponse.messages)
const newMessagesWithArtifacts = await enrichMessagesWithArtifacts(
    backendMessageModels,
    artifactsResponse.artifacts
)

// 4. 기존 계획 메시지의 topicId 업데이트
const updatedPlanMessages = planMessages.map((msg) => ({
    ...msg,
    topicId: response.topic_id
}))

// 5. 메시지 업데이트
messageStore.setMessages(response.topic_id, [
    ...updatedPlanMessages,
    ...newMessagesWithArtifacts
])

// 6. 계획 모드 메시지 정리
messageStore.clearMessages(0)

// 7. selectedTopicId 전환
set({selectedTopicId: response.topic_id})
```

#### After
```typescript
// 1. 계획 메시지 topicId 업데이트 (0 → realTopicId)
const updatedPlanMessages = planMessages.map((msg) => ({
    ...msg,
    topicId: response.topic_id
}))

// 2. 계획 메시지를 실제 topicId로 먼저 설정
messageStore.setMessages(response.topic_id, updatedPlanMessages)

// 3. 계획 모드 메시지 정리
messageStore.clearMessages(0)

// 4. selectedTopicId 전환 (깜박임 방지: 메시지 준비 후 전환)
set({selectedTopicId: response.topic_id})

// 5. 서버 메시지 병합 (중복 제거, artifact 연결)
await messageStore.mergeNewMessages(response.topic_id)
```

**변경 사항**:
- Backend 조회 로직 제거 (`mergeNewMessages`에서 처리)
- 계획 메시지를 먼저 설정하여 깜박임 방지
- `mergeNewMessages` 호출로 서버 메시지 병합

### 4.4 useChatActions.ts 수정

#### Before
```typescript
// AI 응답 후
await refreshMessages(currentTopicId)

// 메시지 삭제 후
await refreshMessages(selectedTopicId)
```

#### After
```typescript
// 유지 (변경 없음)
await refreshMessages(currentTopicId)
await refreshMessages(selectedTopicId)
```

---

## 5. 에러 처리 및 엣지 케이스

### 5.1 mergeNewMessages 실패 시
- 기존 메시지 유지 (계획 메시지만 표시)
- 사용자에게 에러 알림 없음 (백그라운드 동작)
- 콘솔 에러 로그만 출력

### 5.2 중복 제거 로직
- **ID가 있는 메시지**: ID 기반 중복 체크
- **ID가 없는 메시지**: 임시 메시지 (계획 메시지), 항상 유지

```typescript
// 중복 제거 상세 로직
const existingIds = new Set(
    existingMessages
        .filter(m => m.id !== undefined && m.id !== null)  // ID 있는 것만
        .map(m => m.id)
)

const newMessages = serverMessages.filter(m => {
    // ID가 없으면 무조건 추가 (임시 메시지)
    if (!m.id) return true

    // ID가 있으면 중복 체크
    return !existingIds.has(m.id)
})
```

### 5.3 순서 보장
- 계획 메시지 (seq_no: 1, 2)
- 서버 메시지 (seq_no: 3+)
- seq_no 기반 정렬 보장 (서버에서 이미 정렬됨)

---

## 6. 테스트 시나리오

### 6.1 정상 플로우
1. ✅ 템플릿 선택 → 첫 메시지 입력 → 계획 생성
2. ✅ 계획 메시지 2개 표시 (사용자 + AI)
3. ✅ "예" 클릭 → 보고서 생성
4. ✅ 계획 메시지 + 보고서 메시지 모두 표시
5. ✅ 추가 메시지 전송 → 정상 동작

### 6.2 엣지 케이스
- ❌ 보고서 생성 중 사이드바에서 다른 토픽 클릭 → 정상 전환
- ❌ 보고서 생성 실패 → 계획 메시지만 표시
- ❌ 네트워크 오류 → 기존 메시지 유지

---

## 7. 마이그레이션 체크리스트

### 7.1 코드 수정
- [ ] `useMessageStore.ts`
  - [ ] `loadMessages` 추가
  - [ ] `mergeNewMessages` 추가
  - [ ] Interface 업데이트
  - [ ] `fetchMessages` deprecated 처리

- [ ] `MainPage.tsx`
  - [ ] `useEffect` 로직 수정 (Zustand 직접 확인)
  - [ ] `skipFetchRef` 제거
  - [ ] `loadMessages` import 및 사용

- [ ] `useTopicStore.ts`
  - [ ] `generateReportFromPlan` 리팩토링
  - [ ] Backend 조회 로직 제거
  - [ ] `mergeNewMessages` 호출 추가

### 7.2 테스트
- [ ] 보고서 생성 → 계획 메시지 유지 확인
- [ ] 사이드바 토픽 전환 → 전체 로드 확인
- [ ] AI 응답 후 → 새로고침 확인
- [ ] 메시지 삭제 후 → 새로고침 확인

### 7.3 문서화
- [ ] CHANGELOG 업데이트
- [ ] JSDoc 주석 추가
- [ ] 이 계획 문서 완료 체크

---

## 8. 예상 효과

### 8.1 문제 해결
- ✅ 계획 메시지 덮어쓰기 문제 해결
- ✅ React 렌더링 지연 문제 해결
- ✅ 함수 역할 명확화

### 8.2 코드 개선
- ✅ 단일 책임 원칙 준수
- ✅ 함수 이름으로 의도 명확화
- ✅ 유지보수성 향상

### 8.3 사용자 경험
- ✅ 보고서 생성 후에도 계획 메시지 보임
- ✅ 메시지 깜박임 제거
- ✅ 일관된 메시지 표시

---

## 9. 참고 사항

### 9.1 관련 파일
- `frontend/src/stores/useMessageStore.ts`
- `frontend/src/stores/useTopicStore.ts`
- `frontend/src/pages/MainPage.tsx`
- `frontend/src/hooks/useChatActions.ts`

### 9.2 관련 이슈
- GitHub Issue: [계획 메시지가 보고서 생성 후 사라지는 문제]

### 9.3 향후 개선 가능성
- SSE를 활용한 실시간 메시지 업데이트
- 메시지 캐싱 전략 개선
- Optimistic UI 적용

---

**작성자**: Claude Code
**검토자**: -
**승인자**: -
**상태**: 구현 대기
