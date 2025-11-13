# Message Architecture Specification

## 개요

메시지 시스템을 3계층 아키텍처로 재구성하여 관심사 분리 및 타입 안정성을 확보합니다.

## 아키텍처

### 3-Layer Architecture

```
┌─────────────────┐
│ MessageResponse │  ← API Layer (Backend 응답)
└────────┬────────┘
         │ mapMessageResponseToModel()
         ↓
┌─────────────────┐
│  MessageModel   │  ← Domain Layer (비즈니스 로직)
└────────┬────────┘
         │ mapMessageModelToUI()
         ↓
┌─────────────────┐
│   MessageUI     │  ← UI Layer (화면 표시)
└─────────────────┘
```

### 계층별 역할

#### 1. MessageResponse (API Layer)

**위치:** `frontend/src/services/messageApi.ts`

**역할:**
- Backend API 응답 타입 정의
- snake_case 필드명 (Backend 형식)

**타입:**
```typescript
export interface MessageResponse {
    id: number
    topic_id: number
    role: MessageRole
    content: string
    seq_no: number
    created_at: string
    updated_at: string
    report_data?: {
        report_id: number
        filename: string
        content: string
    }
}
```

#### 2. MessageModel (Domain Layer)

**위치:** `frontend/src/models/MessageModel.ts`

**역할:**
- 도메인 모델 (비즈니스 로직용)
- camelCase 필드명 (Frontend 형식)
- Zustand store에 저장되는 형식

**타입:**
```typescript
export interface MessageModel {
    id?: number // Optional: Outline 모드에서는 아직 Backend ID가 없음
    topicId: number
    role: MessageRole
    content: string
    seqNo: number
    createdAt: string
    reportData?: {
        reportId: number
        filename: string
        content: string
    }
}
```

**특징:**
- `id` optional: Outline 메시지는 DB에 저장 전이므로 id 없음
- 모든 비즈니스 로직은 이 타입 기준으로 작성

#### 3. MessageUI (UI Layer)

**위치:** `frontend/src/models/ui/MessageUI.ts`

**역할:**
- UI 표시용 타입
- MessageModel + UI 전용 필드

**타입:**
```typescript
export interface MessageUI extends MessageModel {
    timestamp: Date // UI 표시용 Date 객체
    isOutline?: boolean // Outline 모드 여부
}
```

**특징:**
- `timestamp`: string → Date 변환 (표시용)
- `isOutline`: Outline 모드 플래그 (UI 분기용)

## 변환 (Mapper)

### Mapper 패턴

**위치:** `frontend/src/mapper/messageMapper.ts`

```typescript
// API → Domain
export const mapMessageResponseToModel = (response: MessageResponse): MessageModel => {
    return {
        id: response.id,
        topicId: response.topic_id,
        role: response.role,
        content: response.content,
        seqNo: response.seq_no,
        createdAt: response.created_at,
        reportData: response.report_data ? {
            reportId: response.report_data.report_id,
            filename: response.report_data.filename,
            content: response.report_data.content
        } : undefined
    }
}

// Domain → UI
export const mapMessageModelToUI = (model: MessageModel): MessageUI => {
    return {
        ...model,
        timestamp: new Date(model.createdAt),
        isOutline: false // 기본값
    }
}

// Batch 변환
export const mapMessageResponsesToModels = (responses: MessageResponse[]): MessageModel[] => {
    return responses.map(mapMessageResponseToModel)
}
```

### 변환 시점

1. **API → Model:** API 호출 직후 (useMessages, messageApi)
2. **Model → UI:** 렌더링 직전 (컴포넌트 내부)

## 상태 관리 (Zustand)

### Store 구조

```typescript
// frontend/src/stores/useMessageStore.ts (예정)
interface MessageStore {
    // State
    messagesByTopic: Map<number, MessageModel[]>
    
    // Actions
    setMessages: (topicId: number, messages: MessageModel[]) => void
    addMessages: (topicId: number, messages: MessageModel[]) => void
    clearMessages: (topicId: number) => void
}
```

### 사용 전략

| 시나리오 | 액션 | fetchMessages 호출 |
|---------|------|-------------------|
| 첫 대화 시작 | generateTopic → setMessages | ✅ (한 번만) |
| 추가 메시지 | /ask → addMessages | ❌ (누적) |
| 토픽 전환 | setMessages | ✅ (전체 로드) |
| Outline 모드 | 로컬 생성 → addMessages | ❌ (DB 전 단계) |

## Data Flow

### 일반 메시지 플로우

```
1. API Call
   ↓
2. MessageResponse[] 수신
   ↓
3. mapMessageResponsesToModels()
   ↓
4. MessageModel[] → Zustand Store
   ↓
5. 컴포넌트에서 MessageModel 가져오기
   ↓
6. mapMessageModelToUI() (렌더링 시)
   ↓
7. MessageUI → Component Props
```

### Outline 메시지 플로우

```
1. Outline API Call (/api/outlines/ask)
   ↓
2. OutlineResponse 수신
   ↓
3. 로컬 MessageModel 생성 (id 없음)
   {
     topicId: -1,  // 임시 ID
     role: 'assistant',
     content: outline,
     seqNo: 1,
     createdAt: new Date().toISOString()
   }
   ↓
4. Zustand addMessages (로컬 메시지)
   ↓
5. "예" 클릭 → generateTopic
   ↓
6. Real topicId 발급 → fetchMessages
   ↓
7. Backend 메시지 + 기존 로컬 메시지 병합
```

## 파일 구조

```
frontend/src/
├── models/
│   ├── MessageModel.ts          # Domain model
│   └── ui/
│       └── MessageUI.ts         # UI model
├── mapper/
│   └── messageMapper.ts         # Response ↔ Model ↔ UI 변환
├── services/
│   ├── messageApi.ts            # API + MessageResponse 정의
│   └── outlineApi.ts            # Outline API
├── stores/
│   └── useMessageStore.ts       # Zustand store (예정)
├── hooks/
│   └── useMessages.ts           # Data fetching hook
└── components/
    ├── chat/
    │   └── ChatMessage.tsx      # MessageUI 사용
    └── OutlineMessage.tsx       # MessageUI 사용
```

## 주요 변경 사항

### Before (Old)

```typescript
// messageHelpers.ts에서 변환
const toUIMessage = (msg: MessageResponse): Message => { ... }

// useMessages가 커스텀 Message 타입 반환
const { messages } = useMessages() // Message[]

// 컴포넌트가 Message 타입 사용
<ChatMessage message={msg} />
```

### After (New)

```typescript
// mapper로 명시적 변환
const model = mapMessageResponseToModel(response)
const ui = mapMessageModelToUI(model)

// useMessages가 MessageModel 반환
const { messages } = useMessages() // MessageModel[]

// 컴포넌트가 MessageUI 사용
const ui = mapMessageModelToUI(message)
<ChatMessage message={ui} />
```

## 테스트 시나리오

### 1. 일반 대화

```typescript
// 1. API 호출
const response = await messageApi.getMessages(topicId)

// 2. 변환
const models = mapMessageResponsesToModels(response.messages)

// 3. Store 저장
setMessages(topicId, models)

// 4. UI 렌더링
const uis = models.map(mapMessageModelToUI)
```

### 2. Outline 대화

```typescript
// 1. Outline API
const outline = await outlineApi.askOutline(request)

// 2. 로컬 메시지 생성
const localMessages: MessageModel[] = [
  { topicId: -1, role: 'user', content: request.message, seqNo: 0, ... },
  { topicId: -1, role: 'assistant', content: outline.outline, seqNo: 1, ... }
]

// 3. Store 추가 (id 없음)
addMessages(-1, localMessages)

// 4. "예" → Generate
const { topic_id } = await topicApi.generateTopic(...)

// 5. Fetch 전체 메시지
const { messages } = await messageApi.getMessages(topic_id)
setMessages(topic_id, mapMessageResponsesToModels(messages))
```

## Best Practices

### 1. 타입 안정성

- ✅ 모든 변환은 mapper 함수 사용
- ❌ 직접 타입 캐스팅 금지

### 2. 관심사 분리

- API 레이어: snake_case 유지
- Domain 레이어: camelCase 사용
- UI 레이어: 표시 전용 필드 추가

### 3. Zustand 사용

- ✅ MessageModel 형식으로 저장
- ✅ 컴포넌트에서 필요 시 MessageUI로 변환
- ❌ Store에 UI 타입 저장 금지

### 4. Optional ID 처리

```typescript
// ✅ Good: Optional chaining
message.id ? fetchArtifact(message.id) : null

// ❌ Bad: 직접 접근
fetchArtifact(message.id!) // 위험!
```

## 향후 개선사항

1. **Zustand Store 구현**
   - messagesByTopic: Map<number, MessageModel[]>
   - setMessages/addMessages 액션

2. **Optimistic Updates**
   - 메시지 전송 즉시 로컬 추가
   - API 성공 시 id 업데이트

3. **Message Pagination**
   - 긴 대화 시 페이징 필요
   - offset/limit 지원

4. **Error Handling**
   - API 실패 시 로컬 메시지 롤백
   - 재시도 로직

---

**버전:** 1.0
**마지막 업데이트:** 2025-11-12
**작성자:** Claude Code
