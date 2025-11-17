# Template Prompt 관리 기능 구현 계획

**작성일:** 2025-11-17  
**목적:** TemplateDetailModal에서 User Prompt와 System Prompt 입력 및 수정 기능 추가  
**현재 구조:** TemplateDetailModal은 템플릿 상세 정보만 표시 (읽기 전용)

---

## 1. 요구사항 분석

### 1.1 현재 동작
- `TemplateDetailModal`은 템플릿 상세 정보를 표시 (제목, 파일명, 파일 크기, 플레이스홀더 목록, 생성일)
- '닫기' 버튼만 존재
- 읽기 전용 모달

### 1.2 변경할 동작
1. **플레이스홀더 섹션 아래에 프롬프트 입력 섹션 추가**:
   - User Prompt 입력 필드 (Textarea)
   - System Prompt 입력 필드 (Textarea)
   - 기존 값이 있으면 표시

2. **Footer에 '저장' 버튼 추가**:
   - '닫기' 버튼 우측에 '저장' 버튼 추가
   - '저장' 버튼 클릭 시:
     - User Prompt가 변경되었으면 `PUT /api/templates/{id}/prompt-user` 호출
     - System Prompt가 변경되었으면:
       - **빈 값인 경우**: `POST /api/templates/{id}/regenerate-prompt-system` 호출
       - **빈 값이 아닌 경우**: `PUT /api/templates/{id}/prompt-system` 호출
     - 변경 사항이 없으면 아무 요청도 보내지 않음

3. **저장 로직**:
   - 변경 감지: 초기값과 현재값 비교
   - 변경된 항목만 API 요청
   - 여러 프롬프트가 변경된 경우 순차 처리
   - 성공 시 메시지 표시 및 모달 닫기

---

## 2. 구현 대상 파일

### 2.1 수정할 파일

| 파일 경로 | 수정 내용 |
|---------|----------|
| `frontend/src/components/template/TemplateDetailModal.tsx` | - User Prompt, System Prompt input 추가<br>- '저장' 버튼 추가<br>- 변경 감지 로직 구현<br>- API 호출 로직 구현 |
| `frontend/src/components/template/TemplateDetailModal.module.css` | - 프롬프트 입력 섹션 스타일 추가 |
| `frontend/src/services/templateApi.ts` | - `updatePromptUser()` 함수 추가<br>- `updatePromptSystem()` 함수 추가<br>- `regeneratePromptSystem()` 함수 추가 |
| `frontend/src/types/template.ts` | - 프롬프트 수정 요청/응답 타입 추가 |
| `frontend/src/constants/index.ts` | - 프롬프트 관련 API 엔드포인트 추가 |

### 2.2 참조 파일 (변경 없음)

| 파일 경로 | 참조 목적 |
|---------|----------|
| `backend/app/routers/templates.py` | API 엔드포인트 스펙 확인 |
| `backend/app/models/template.py` | 요청/응답 모델 확인 |

---

## 3. 전제 조건

**백엔드 API 가정**:
- `GET /api/templates/{id}` 응답에 `prompt_user`, `prompt_system` 필드가 **이미 포함되어 있다고 가정**
- `PUT /api/templates/{id}/prompt-user` 엔드포인트 사용 가능
- `PUT /api/templates/{id}/prompt-system` 엔드포인트 사용 가능
- `POST /api/templates/{id}/regenerate-prompt-system` 엔드포인트 사용 가능

---

## 4. 상세 설계

### 4.1 TemplateDetailModal 수정

#### State 추가
```typescript
const [promptUser, setPromptUser] = useState<string>('')
const [promptSystem, setPromptSystem] = useState<string>('')
const [initialPromptUser, setInitialPromptUser] = useState<string>('')
const [initialPromptSystem, setInitialPromptSystem] = useState<string>('')
const [isSaving, setIsSaving] = useState(false)
```

#### 초기값 로드 (useEffect)
```typescript
useEffect(() => {
    if (template) {
        const userPrompt = template.prompt_user || ''
        const systemPrompt = template.prompt_system || ''
        
        setPromptUser(userPrompt)
        setPromptSystem(systemPrompt)
        setInitialPromptUser(userPrompt)
        setInitialPromptSystem(systemPrompt)
    }
}, [template])
```

#### 변경 감지 함수
```typescript
const hasUserPromptChanged = (): boolean => {
    return promptUser !== initialPromptUser
}

const hasSystemPromptChanged = (): boolean => {
    return promptSystem !== initialPromptSystem
}

const hasAnyChanges = (): boolean => {
    return hasUserPromptChanged() || hasSystemPromptChanged()
}
```

#### 저장 핸들러
```typescript
const handleSave = async () => {
    if (!templateId) return
    
    // 변경사항 없으면 그냥 닫기
    if (!hasAnyChanges()) {
        antdMessage.info('변경된 내용이 없습니다.')
        return
    }
    
    setIsSaving(true)
    
    try {
        // User Prompt 업데이트
        if (hasUserPromptChanged()) {
            await templateApi.updatePromptUser(templateId, promptUser)
        }
        
        // System Prompt 업데이트
        if (hasSystemPromptChanged()) {
            const trimmedSystemPrompt = promptSystem.trim()
            
            if (trimmedSystemPrompt === '') {
                // 빈 값 -> 재생성
                await templateApi.regeneratePromptSystem(templateId)
            } else {
                // 값 있음 -> 업데이트
                await templateApi.updatePromptSystem(templateId, promptSystem)
            }
        }
        
        antdMessage.success('프롬프트가 저장되었습니다.')
        onClose()
    } catch (error: any) {
        console.error('TemplateDetailModal > handleSave', error)
        antdMessage.error('프롬프트 저장에 실패했습니다.')
    } finally {
        setIsSaving(false)
    }
}
```

#### UI 구조 (JSX 추가)
```tsx
{/* 기존 플레이스홀더 섹션 */}
<div className={styles.section}>
    <h3 className={styles.sectionTitle}>
        <TagsOutlined className={styles.sectionIcon} />
        플레이스홀더
    </h3>
    {/* ... 기존 코드 ... */}
</div>

{/* 신규: User Prompt 섹션 */}
<div className={styles.section}>
    <h3 className={styles.sectionTitle}>User Prompt</h3>
    <textarea
        className={styles.promptTextarea}
        value={promptUser}
        onChange={(e) => setPromptUser(e.target.value)}
        placeholder="사용자 프롬프트를 입력하세요 (선택사항)"
        rows={6}
    />
    <p className={styles.promptHint}>
        보고서 생성 시 사용자가 추가로 정의하는 프롬프트입니다.
    </p>
</div>

{/* 신규: System Prompt 섹션 */}
<div className={styles.section}>
    <h3 className={styles.sectionTitle}>System Prompt</h3>
    <textarea
        className={styles.promptTextarea}
        value={promptSystem}
        onChange={(e) => setPromptSystem(e.target.value)}
        placeholder="시스템 프롬프트를 입력하세요"
        rows={10}
    />
    <p className={styles.promptHint}>
        빈 값으로 저장 시 자동으로 재생성됩니다.
    </p>
</div>
```

#### Footer 수정
```tsx
footer={[
    <Button key="close" onClick={onClose}>
        닫기
    </Button>,
    <Button
        key="save"
        type="primary"
        loading={isSaving}
        disabled={!hasAnyChanges()}
        onClick={handleSave}
    >
        저장
    </Button>
]}
```

### 4.2 CSS 스타일 추가

```css
/* TemplateDetailModal.module.css */

.promptTextarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    line-height: 1.6;
    resize: vertical;
    transition: border-color 0.3s;
}

.promptTextarea:focus {
    outline: none;
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.promptHint {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #8c8c8c;
    font-style: italic;
}
```

### 4.3 templateApi.ts 함수 추가

```typescript
/**
 * User Prompt 업데이트
 */
updatePromptUser: async (templateId: number, promptUser: string): Promise<void> => {
    const response = await api.put<ApiResponse<any>>(
        API_ENDPOINTS.UPDATE_PROMPT_USER(templateId),
        { prompt_user: promptUser }
    )
    
    if (!response.data.success) {
        throw new Error(response.data.error?.message || 'User Prompt 업데이트에 실패했습니다.')
    }
}

/**
 * System Prompt 업데이트
 */
updatePromptSystem: async (templateId: number, promptSystem: string): Promise<void> => {
    const response = await api.put<ApiResponse<any>>(
        API_ENDPOINTS.UPDATE_PROMPT_SYSTEM(templateId),
        { prompt_system: promptSystem }
    )
    
    if (!response.data.success) {
        throw new Error(response.data.error?.message || 'System Prompt 업데이트에 실패했습니다.')
    }
}

/**
 * System Prompt 재생성
 */
regeneratePromptSystem: async (templateId: number): Promise<void> => {
    const response = await api.post<ApiResponse<any>>(
        API_ENDPOINTS.REGENERATE_PROMPT_SYSTEM(templateId)
    )
    
    if (!response.data.success) {
        throw new Error(response.data.error?.message || 'System Prompt 재생성에 실패했습니다.')
    }
}
```

### 4.4 constants/index.ts 엔드포인트 추가

```typescript
export const API_ENDPOINTS = {
    // ... 기존 엔드포인트 ...
    
    // Template Prompts
    UPDATE_PROMPT_USER: (templateId: number) => `/api/templates/${templateId}/prompt-user`,
    UPDATE_PROMPT_SYSTEM: (templateId: number) => `/api/templates/${templateId}/prompt-system`,
    REGENERATE_PROMPT_SYSTEM: (templateId: number) => `/api/templates/${templateId}/regenerate-prompt-system`,
}
```

### 4.5 types/template.ts 타입 추가

```typescript
/**
 * User Prompt 업데이트 요청
 */
export interface UpdatePromptUserRequest {
    prompt_user: string
}

/**
 * System Prompt 업데이트 요청
 */
export interface UpdatePromptSystemRequest {
    prompt_system: string
}

/**
 * 프롬프트 업데이트 응답
 */
export interface UpdatePromptResponse {
    id: number
    title: string
    prompt_system: string | null
    prompt_user: string | null
    updated_at: string
}

/**
 * System Prompt 재생성 응답
 */
export interface RegeneratePromptResponse {
    id: number
    prompt_system: string | null
    regenerated_at: string
}

/**
 * 템플릿 상세 정보 (프롬프트 포함)
 */
export interface TemplateDetail {
    id: number
    title: string
    filename: string
    file_size: number
    placeholders: Array<{key: string}>
    prompt_user?: string | null      // 신규
    prompt_system?: string | null     // 신규
    created_at: string
}
```

---

## 5. 사이드 이펙트 분석

### 4.1 긍정적 효과
1. **UX 개선**: 템플릿 프롬프트를 모달에서 직접 편집 가능
2. **효율성**: 변경된 내용만 API 요청 (네트워크 최적화)
3. **사용자 피드백**: 버튼 disabled 상태로 변경 여부 시각적 표시

### 4.2 잠재적 문제 및 해결

#### 문제 1: 프롬프트가 매우 긴 경우 UI 깨짐
- **상황**: System Prompt가 수천 글자일 경우 모달 높이 초과
- **해결**:
  - Textarea에 `resize: vertical` 적용 (사용자가 크기 조정 가능)
  - 모달에 `overflow-y: auto` 적용
  - 최대 높이 제한: `max-height: 80vh`

```css
.content {
    max-height: 70vh;
    overflow-y: auto;
}
```

#### 문제 2: 저장 중 사용자가 모달 닫기
- **상황**: API 요청 중 사용자가 '닫기' 또는 ESC 키 입력
- **해결**:
  - 저장 중일 때 모달 닫기 비활성화
  - `Modal` props에 `closable={!isSaving}`, `maskClosable={!isSaving}` 추가

```tsx
<Modal
    closable={!isSaving}
    maskClosable={!isSaving}
    keyboard={!isSaving}
    // ...
/>
```

#### 문제 3: 재생성 시 기존 System Prompt 손실
- **상황**: 사용자가 System Prompt를 비우고 저장 시 재생성됨
- **해결**:
  - 재생성 전 확인 다이얼로그 표시
  - 사용자에게 재생성될 것임을 명확히 안내

```typescript
if (hasSystemPromptChanged() && promptSystem.trim() === '') {
    const confirmed = await new Promise((resolve) => {
        Modal.confirm({
            title: 'System Prompt 재생성',
            content: '빈 값으로 저장하면 System Prompt가 자동으로 재생성됩니다. 계속하시겠습니까?',
            onOk: () => resolve(true),
            onCancel: () => resolve(false)
        })
    })
    
    if (!confirmed) return
}
```

#### 문제 4: 여러 API 요청 중 일부 실패
- **상황**: User Prompt 업데이트는 성공했지만 System Prompt 업데이트 실패
- **해결**:
  - 부분 성공 시에도 사용자에게 알림
  - 실패한 항목만 재시도 가능하도록 안내

```typescript
const results = {
    userPromptSuccess: false,
    systemPromptSuccess: false
}

try {
    if (hasUserPromptChanged()) {
        await templateApi.updatePromptUser(templateId, promptUser)
        results.userPromptSuccess = true
    }
    
    if (hasSystemPromptChanged()) {
        // ...
        results.systemPromptSuccess = true
    }
    
    // 모두 성공
    antdMessage.success('프롬프트가 저장되었습니다.')
} catch (error) {
    // 부분 성공 처리
    if (results.userPromptSuccess || results.systemPromptSuccess) {
        antdMessage.warning('일부 프롬프트만 저장되었습니다. 다시 시도해주세요.')
    } else {
        antdMessage.error('프롬프트 저장에 실패했습니다.')
    }
}
```

#### 문제 5: 템플릿 상세 API에서 프롬프트 필드 누락
- **상황**: 기존 `GET /api/templates/{id}` 응답에 `prompt_user`, `prompt_system` 없음
- **해결**:
  - 백엔드 `TemplateDetailResponse` 모델 확인 필요
  - **현재 백엔드 모델에는 `prompt_system`만 있고 `prompt_user`는 없음**
  - 백엔드 수정 필요: `TemplateDetailResponse`에 `prompt_user` 필드 추가

**백엔드 수정 필요 (중요)**:
```python
# backend/app/models/template.py
class TemplateDetailResponse(BaseModel):
    id: int = Field(..., description="템플릿 ID")
    title: str = Field(..., description="템플릿 제목")
    filename: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    placeholders: List[PlaceholderResponse] = Field(..., description="플레이스홀더 목록")
    prompt_system: Optional[str] = Field(None, description="동적 생성된 System Prompt")
    prompt_user: Optional[str] = Field(None, description="사용자 프롬프트")  # 신규 추가
    created_at: datetime = Field(..., description="생성 일시")
```

```python
# backend/app/routers/templates.py - get_template 수정
response_data = TemplateDetailResponse(
    id=template.id,
    title=template.title,
    filename=template.filename,
    file_size=template.file_size,
    placeholders=placeholder_responses,
    prompt_system=template.prompt_system,  # 기존
    prompt_user=template.prompt_user,      # 신규 추가
    created_at=template.created_at
)
```

---

## 6. 구현 순서

### Step 1: Mock API 테스트 작성
- [ ] `frontend/src/services/__tests__/templateApi.test.ts` 생성
- [ ] 테스트 케이스 7개 작성
  - getTemplate (prompt 필드 포함)
  - updatePromptUser (성공/실패)
  - updatePromptSystem
  - regeneratePromptSystem
  - listTemplates
  - uploadTemplate
  - deleteTemplate
- [ ] 테스트 실행 및 통과 확인

### Step 2: 프론트엔드 타입 정의
- [ ] `types/template.ts`에 프롬프트 관련 타입 추가
- [ ] `TemplateDetail` 인터페이스에 `prompt_user`, `prompt_system` 추가

### Step 3: API 서비스 함수 추가
- [ ] `constants/index.ts`에 엔드포인트 추가
- [ ] `services/templateApi.ts`에 3개 함수 추가
  - `updatePromptUser()`
  - `updatePromptSystem()`
  - `regeneratePromptSystem()`

### Step 4: TemplateDetailModal UI 수정
- [ ] State 추가 (prompt, initial, isSaving)
- [ ] useEffect로 초기값 로드
- [ ] User Prompt 섹션 추가 (Textarea)
- [ ] System Prompt 섹션 추가 (Textarea)
- [ ] Footer에 '저장' 버튼 추가

### Step 5: 저장 로직 구현
- [ ] 변경 감지 함수 구현
- [ ] handleSave 함수 구현
- [ ] 재생성 확인 다이얼로그 추가
- [ ] 에러 핸들링 (부분 성공 처리)

### Step 6: 스타일링
- [ ] CSS 추가 (promptTextarea, promptHint)
- [ ] 모달 최대 높이 제한 (overflow 처리)
- [ ] 반응형 디자인 확인

### Step 7: 테스트
- [ ] 정상 플로우 테스트
- [ ] 예외 플로우 테스트
- [ ] 에러 플로우 테스트

---

## 7. 테스트 시나리오

### 7.1 정상 플로우

**시나리오 1: User Prompt만 수정**
1. 템플릿 목록에서 템플릿 클릭 → 상세 모달 열림
2. User Prompt 텍스트에어리어에 "간결하게 작성하세요" 입력
3. '저장' 버튼 활성화 확인
4. '저장' 버튼 클릭
5. 성공 메시지 표시 → 모달 닫힘

**시나리오 2: System Prompt만 수정**
1. 템플릿 상세 모달 열기
2. System Prompt 수정 (예: "당신은 전문 보고서 작성 AI입니다" 추가)
3. '저장' 버튼 클릭
4. PUT /api/templates/{id}/prompt-system 호출 확인
5. 성공 메시지 표시

**시나리오 3: 둘 다 수정**
1. User Prompt + System Prompt 모두 수정
2. '저장' 버튼 클릭
3. 두 API 순차 호출 확인
4. 성공 메시지 표시

**시나리오 4: System Prompt 비우기 (재생성)**
1. System Prompt 텍스트 전체 삭제
2. '저장' 버튼 클릭
3. 확인 다이얼로그 표시: "재생성됩니다. 계속?"
4. '확인' 클릭
5. POST /api/templates/{id}/regenerate-prompt-system 호출 확인
6. 성공 메시지 표시

### 7.2 예외 플로우

**시나리오 5: 변경 없이 저장**
1. 템플릿 상세 모달 열기
2. 아무것도 수정하지 않음
3. '저장' 버튼 비활성화 확인
4. (또는) 클릭 시 "변경된 내용이 없습니다" 메시지

**시나리오 6: 저장 중 모달 닫기 시도**
1. 프롬프트 수정 후 '저장' 클릭
2. 로딩 중 ESC 키 입력 또는 X 버튼 클릭
3. 모달 닫히지 않음 확인
4. 저장 완료 후 모달 자동 닫힘

**시나리오 7: 재생성 확인 다이얼로그 취소**
1. System Prompt 비우기
2. '저장' 클릭 → 확인 다이얼로그
3. '취소' 클릭
4. 모달 열린 상태 유지 (저장 안 됨)

### 7.3 에러 플로우

**시나리오 8: API 호출 실패 (네트워크 에러)**
1. 프롬프트 수정 후 '저장' 클릭
2. 네트워크 차단 (개발자 도구로 시뮬레이션)
3. 에러 메시지 표시: "프롬프트 저장에 실패했습니다"
4. 모달 열린 상태 유지 (재시도 가능)

**시나리오 9: 부분 성공 (User 성공, System 실패)**
1. User + System 프롬프트 수정
2. User Prompt 업데이트 성공
3. System Prompt 업데이트 실패 (서버 오류)
4. 경고 메시지: "일부 프롬프트만 저장되었습니다"

**시나리오 10: 권한 없음 (403)**
1. 다른 사용자의 템플릿 접근 (비정상적 상황)
2. '저장' 클릭
3. 403 Forbidden 응답
4. 에러 메시지: "권한이 없습니다" (백엔드 에러 메시지 표시)

---

## 8. UI/UX 상세 스펙

### 7.1 레이아웃 구조
```
┌─────────────────────────────────────┐
│ 템플릿 상세                    [X]  │  ← 모달 헤더
├─────────────────────────────────────┤
│                                     │
│ [기본 정보 섹션]                     │
│ - 제목, 파일명, 파일 크기, 생성일    │
│                                     │
│ [플레이스홀더 섹션]                  │
│ - {{KEY}} 태그 목록                 │
│                                     │
│ [User Prompt 섹션]                  │  ← 신규
│ ┌─────────────────────────────────┐│
│ │ [Textarea - 6 rows]             ││
│ │                                 ││
│ └─────────────────────────────────┘│
│ "사용자 프롬프트를 입력하세요..."   │
│                                     │
│ [System Prompt 섹션]                │  ← 신규
│ ┌─────────────────────────────────┐│
│ │ [Textarea - 10 rows]            ││
│ │                                 ││
│ │                                 ││
│ └─────────────────────────────────┘│
│ "빈 값으로 저장 시 자동 재생성"     │
│                                     │
├─────────────────────────────────────┤
│               [닫기] [저장]          │  ← Footer (수정)
└─────────────────────────────────────┘
```

### 7.2 색상 및 타이포그래피
- **Textarea 테두리**: `#d9d9d9` (기본), `#1890ff` (포커스)
- **Hint 텍스트**: `#8c8c8c`, `font-size: 0.75rem`, `font-style: italic`
- **저장 버튼**: Ant Design `primary` (파란색)
- **저장 버튼 비활성화**: `opacity: 0.6`, `cursor: not-allowed`

### 7.3 Textarea 스펙
- **User Prompt**:
  - Rows: 6
  - Placeholder: "사용자 프롬프트를 입력하세요 (선택사항)"
  
- **System Prompt**:
  - Rows: 10
  - Placeholder: "시스템 프롬프트를 입력하세요"
  
- **공통 스타일**:
  - Font: `'Courier New', monospace`
  - Font size: `0.875rem`
  - Line height: `1.6`
  - Resize: `vertical` (사용자가 크기 조정 가능)

### 8.4 모달 스크롤 처리
```css
.content {
    max-height: 70vh;
    overflow-y: auto;
    padding: 1.5rem;
}
```

---

## 8. Mock API 테스트 추가

### 8.1 테스트 파일 생성
**파일**: `frontend/src/services/__tests__/templateApi.test.ts`

### 8.2 테스트 케이스

#### 테스트 1: getTemplate - prompt 필드 포함 확인
```typescript
describe('templateApi.getTemplate', () => {
    it('should return template detail with prompts', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                filename: 'template.hwpx',
                file_size: 45678,
                placeholders: [{key: '{{TITLE}}'}],
                prompt_user: '간결하게 작성하세요',
                prompt_system: '당신은 전문 보고서 작성 AI입니다',
                created_at: '2025-11-17T10:00:00'
            }
        }
        
        mockAxios.get.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.getTemplate(1)
        
        expect(result.prompt_user).toBe('간결하게 작성하세요')
        expect(result.prompt_system).toBe('당신은 전문 보고서 작성 AI입니다')
    })
})
```

#### 테스트 2: updatePromptUser
```typescript
describe('templateApi.updatePromptUser', () => {
    it('should update user prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                prompt_user: '새로운 사용자 프롬프트',
                prompt_system: '시스템 프롬프트',
                updated_at: '2025-11-17T10:05:00'
            }
        }
        
        mockAxios.put.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.updatePromptUser(1, '새로운 사용자 프롬프트')
        
        expect(mockAxios.put).toHaveBeenCalledWith(
            '/api/templates/1/prompt-user',
            {prompt_user: '새로운 사용자 프롬프트'}
        )
    })
    
    it('should throw error on failure', async () => {
        const mockResponse = {
            success: false,
            error: {message: 'Update failed'}
        }
        
        mockAxios.put.mockResolvedValueOnce({data: mockResponse})
        
        await expect(
            templateApi.updatePromptUser(1, 'test')
        ).rejects.toThrow('Update failed')
    })
})
```

#### 테스트 3: updatePromptSystem
```typescript
describe('templateApi.updatePromptSystem', () => {
    it('should update system prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                prompt_user: '사용자 프롬프트',
                prompt_system: '새로운 시스템 프롬프트',
                updated_at: '2025-11-17T10:06:00'
            }
        }
        
        mockAxios.put.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.updatePromptSystem(1, '새로운 시스템 프롬프트')
        
        expect(mockAxios.put).toHaveBeenCalledWith(
            '/api/templates/1/prompt-system',
            {prompt_system: '새로운 시스템 프롬프트'}
        )
    })
})
```

#### 테스트 4: regeneratePromptSystem
```typescript
describe('templateApi.regeneratePromptSystem', () => {
    it('should regenerate system prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                prompt_system: '재생성된 시스템 프롬프트',
                regenerated_at: '2025-11-17T10:07:00'
            }
        }
        
        mockAxios.post.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.regeneratePromptSystem(1)
        
        expect(mockAxios.post).toHaveBeenCalledWith(
            '/api/templates/1/regenerate-prompt-system'
        )
    })
})
```

#### 테스트 5: listTemplates
```typescript
describe('templateApi.listTemplates', () => {
    it('should return template list', async () => {
        const mockResponse = {
            success: true,
            data: [
                {
                    id: 1,
                    title: '재무보고서 템플릿',
                    filename: 'template1.hwpx',
                    file_size: 45678,
                    created_at: '2025-11-17T10:00:00'
                },
                {
                    id: 2,
                    title: '영업보고서 템플릿',
                    filename: 'template2.hwpx',
                    file_size: 52341,
                    created_at: '2025-11-16T14:00:00'
                }
            ]
        }
        
        mockAxios.get.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.listTemplates()
        
        expect(result).toHaveLength(2)
        expect(result[0].title).toBe('재무보고서 템플릿')
    })
})
```

#### 테스트 6: uploadTemplate
```typescript
describe('templateApi.uploadTemplate', () => {
    it('should upload template successfully', async () => {
        const mockFile = new File(['content'], 'test.hwpx', {type: 'application/hwpx'})
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '새 템플릿',
                filename: 'test.hwpx',
                file_size: 1024,
                placeholders: [{key: '{{TITLE}}'}],
                prompt_user: null,
                prompt_system: '자동 생성된 시스템 프롬프트',
                created_at: '2025-11-17T10:00:00'
            }
        }
        
        mockAxios.post.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.uploadTemplate(mockFile, '새 템플릿')
        
        expect(result.id).toBe(1)
        expect(result.prompt_system).toBe('자동 생성된 시스템 프롬프트')
        
        // FormData 검증
        const formData = mockAxios.post.mock.calls[0][1]
        expect(formData).toBeInstanceOf(FormData)
    })
})
```

#### 테스트 7: deleteTemplate
```typescript
describe('templateApi.deleteTemplate', () => {
    it('should delete template successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                message: '템플릿이 삭제되었습니다.'
            }
        }
        
        mockAxios.delete.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.deleteTemplate(1)
        
        expect(result.id).toBe(1)
        expect(result.message).toBe('템플릿이 삭제되었습니다.')
    })
})
```

### 8.3 테스트 설정 파일

**파일**: `frontend/src/services/__tests__/setup.ts`
```typescript
import axios from 'axios'

jest.mock('axios')

export const mockAxios = axios as jest.Mocked<typeof axios>

beforeEach(() => {
    jest.clearAllMocks()
})
```

### 8.4 테스트 실행 명령
```bash
# 전체 테스트
npm test templateApi.test.ts

# 커버리지 포함
npm test -- --coverage templateApi.test.ts
```

---

## 9. Mock API 테스트

### 9.1 테스트 파일
**파일**: `frontend/src/services/__tests__/templateApi.test.ts`

### 9.2 테스트 케이스 목록

#### TC1: getTemplate - prompt 필드 포함 확인
```typescript
describe('templateApi.getTemplate', () => {
    it('should return template detail with prompts', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                filename: 'template.hwpx',
                file_size: 45678,
                placeholders: [{key: '{{TITLE}}'}],
                prompt_user: '간결하게 작성하세요',
                prompt_system: '당신은 전문 보고서 작성 AI입니다',
                created_at: '2025-11-17T10:00:00'
            }
        }
        
        mockAxios.get.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.getTemplate(1)
        
        expect(result.prompt_user).toBe('간결하게 작성하세요')
        expect(result.prompt_system).toBe('당신은 전문 보고서 작성 AI입니다')
    })
})
```

#### TC2: updatePromptUser - 성공
```typescript
describe('templateApi.updatePromptUser', () => {
    it('should update user prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                prompt_user: '새로운 사용자 프롬프트',
                prompt_system: '시스템 프롬프트',
                updated_at: '2025-11-17T10:05:00'
            }
        }
        
        mockAxios.put.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.updatePromptUser(1, '새로운 사용자 프롬프트')
        
        expect(mockAxios.put).toHaveBeenCalledWith(
            '/api/templates/1/prompt-user',
            {prompt_user: '새로운 사용자 프롬프트'}
        )
    })
})
```

#### TC3: updatePromptUser - 실패
```typescript
it('should throw error on failure', async () => {
    const mockResponse = {
        success: false,
        error: {message: 'Update failed'}
    }
    
    mockAxios.put.mockResolvedValueOnce({data: mockResponse})
    
    await expect(
        templateApi.updatePromptUser(1, 'test')
    ).rejects.toThrow('Update failed')
})
```

#### TC4: updatePromptSystem
```typescript
describe('templateApi.updatePromptSystem', () => {
    it('should update system prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '재무보고서 템플릿',
                prompt_user: '사용자 프롬프트',
                prompt_system: '새로운 시스템 프롬프트',
                updated_at: '2025-11-17T10:06:00'
            }
        }
        
        mockAxios.put.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.updatePromptSystem(1, '새로운 시스템 프롬프트')
        
        expect(mockAxios.put).toHaveBeenCalledWith(
            '/api/templates/1/prompt-system',
            {prompt_system: '새로운 시스템 프롬프트'}
        )
    })
})
```

#### TC5: regeneratePromptSystem
```typescript
describe('templateApi.regeneratePromptSystem', () => {
    it('should regenerate system prompt successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                prompt_system: '재생성된 시스템 프롬프트',
                regenerated_at: '2025-11-17T10:07:00'
            }
        }
        
        mockAxios.post.mockResolvedValueOnce({data: mockResponse})
        
        await templateApi.regeneratePromptSystem(1)
        
        expect(mockAxios.post).toHaveBeenCalledWith(
            '/api/templates/1/regenerate-prompt-system'
        )
    })
})
```

#### TC6: listTemplates
```typescript
describe('templateApi.listTemplates', () => {
    it('should return template list', async () => {
        const mockResponse = {
            success: true,
            data: [
                {
                    id: 1,
                    title: '재무보고서 템플릿',
                    filename: 'template1.hwpx',
                    file_size: 45678,
                    created_at: '2025-11-17T10:00:00'
                },
                {
                    id: 2,
                    title: '영업보고서 템플릿',
                    filename: 'template2.hwpx',
                    file_size: 52341,
                    created_at: '2025-11-16T14:00:00'
                }
            ]
        }
        
        mockAxios.get.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.listTemplates()
        
        expect(result).toHaveLength(2)
        expect(result[0].title).toBe('재무보고서 템플릿')
    })
})
```

#### TC7: uploadTemplate
```typescript
describe('templateApi.uploadTemplate', () => {
    it('should upload template successfully', async () => {
        const mockFile = new File(['content'], 'test.hwpx', {type: 'application/hwpx'})
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                title: '새 템플릿',
                filename: 'test.hwpx',
                file_size: 1024,
                placeholders: [{key: '{{TITLE}}'}],
                prompt_user: null,
                prompt_system: '자동 생성된 시스템 프롬프트',
                created_at: '2025-11-17T10:00:00'
            }
        }
        
        mockAxios.post.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.uploadTemplate(mockFile, '새 템플릿')
        
        expect(result.id).toBe(1)
        expect(result.prompt_system).toBe('자동 생성된 시스템 프롬프트')
        
        // FormData 검증
        const formData = mockAxios.post.mock.calls[0][1]
        expect(formData).toBeInstanceOf(FormData)
    })
})
```

#### TC8: deleteTemplate
```typescript
describe('templateApi.deleteTemplate', () => {
    it('should delete template successfully', async () => {
        const mockResponse = {
            success: true,
            data: {
                id: 1,
                message: '템플릿이 삭제되었습니다.'
            }
        }
        
        mockAxios.delete.mockResolvedValueOnce({data: mockResponse})
        
        const result = await templateApi.deleteTemplate(1)
        
        expect(result.id).toBe(1)
        expect(result.message).toBe('템플릿이 삭제되었습니다.')
    })
})
```

### 9.3 테스트 설정

**파일**: `frontend/src/services/__tests__/setup.ts`
```typescript
import axios from 'axios'

jest.mock('axios')

export const mockAxios = axios as jest.Mocked<typeof axios>

beforeEach(() => {
    jest.clearAllMocks()
})
```

### 9.4 테스트 실행
```bash
# 전체 테스트
npm test templateApi.test.ts

# 커버리지 포함
npm test -- --coverage templateApi.test.ts
```

---

## 10. 향후 개선 가능성

### v2 기능 (선택사항)
1. **Markdown 미리보기**:
   - System Prompt를 마크다운으로 작성하는 경우 미리보기 탭 제공
   - react-markdown 사용

2. **프롬프트 템플릿**:
   - 자주 사용하는 프롬프트를 템플릿으로 저장
   - 드롭다운에서 선택하여 빠르게 적용

3. **변경 이력 (History)**:
   - 프롬프트 수정 이력을 DB에 저장
   - 이전 버전 복원 기능

4. **AI 제안**:
   - "프롬프트 개선" 버튼
   - Claude API로 더 나은 프롬프트 제안

5. **프롬프트 검증**:
   - 길이 제한 (예: 10,000자)
   - 금지 키워드 체크

---

## 11. 체크리스트

### Mock API 테스트
- [ ] 테스트 파일 생성 (`__tests__/templateApi.test.ts`)
- [ ] 7개 테스트 케이스 작성
- [ ] 모든 테스트 통과 확인

### 프론트엔드 구현
- [ ] 타입 정의 (`types/template.ts`)
- [ ] API 엔드포인트 추가 (`constants/index.ts`)
- [ ] API 서비스 함수 3개 추가 (`templateApi.ts`)
- [ ] TemplateDetailModal State 추가
- [ ] User Prompt 섹션 UI 추가
- [ ] System Prompt 섹션 UI 추가
- [ ] '저장' 버튼 추가
- [ ] 변경 감지 로직 구현
- [ ] handleSave 함수 구현
- [ ] 재생성 확인 다이얼로그 추가
- [ ] CSS 스타일링
- [ ] 모달 스크롤 처리

### 테스트
- [ ] 시나리오 1-4 (정상 플로우)
- [ ] 시나리오 5-7 (예외 플로우)
- [ ] 시나리오 8-10 (에러 플로우)
- [ ] 모바일 반응형 확인
- [ ] 접근성 (키보드 네비게이션, aria-label)

### 코드 리뷰
- [ ] TypeScript 타입 에러 없음
- [ ] Console 에러/경고 없음
- [ ] 코드 스타일 일관성
- [ ] 주석 및 DocString 추가

---

## 12. 코드 예시

### TemplateDetailModal.tsx (주요 부분)

```typescript
const TemplateDetailModal: React.FC<TemplateDetailModalProps> = ({
    open,
    templateId,
    onClose
}) => {
    const [template, setTemplate] = useState<TemplateDetail | null>(null)
    const [loading, setLoading] = useState(false)
    
    // 신규: 프롬프트 상태 관리
    const [promptUser, setPromptUser] = useState<string>('')
    const [promptSystem, setPromptSystem] = useState<string>('')
    const [initialPromptUser, setInitialPromptUser] = useState<string>('')
    const [initialPromptSystem, setInitialPromptSystem] = useState<string>('')
    const [isSaving, setIsSaving] = useState(false)
    
    // 템플릿 로드 시 초기값 설정
    useEffect(() => {
        if (template) {
            const userPrompt = template.prompt_user || ''
            const systemPrompt = template.prompt_system || ''
            
            setPromptUser(userPrompt)
            setPromptSystem(systemPrompt)
            setInitialPromptUser(userPrompt)
            setInitialPromptSystem(systemPrompt)
        }
    }, [template])
    
    // 변경 감지
    const hasUserPromptChanged = () => promptUser !== initialPromptUser
    const hasSystemPromptChanged = () => promptSystem !== initialPromptSystem
    const hasAnyChanges = () => hasUserPromptChanged() || hasSystemPromptChanged()
    
    // 저장 핸들러
    const handleSave = async () => {
        if (!templateId) return
        
        if (!hasAnyChanges()) {
            antdMessage.info('변경된 내용이 없습니다.')
            return
        }
        
        setIsSaving(true)
        
        try {
            // User Prompt 업데이트
            if (hasUserPromptChanged()) {
                await templateApi.updatePromptUser(templateId, promptUser)
            }
            
            // System Prompt 업데이트 또는 재생성
            if (hasSystemPromptChanged()) {
                const trimmedSystemPrompt = promptSystem.trim()
                
                if (trimmedSystemPrompt === '') {
                    // 재생성 확인
                    const confirmed = await new Promise<boolean>((resolve) => {
                        Modal.confirm({
                            title: 'System Prompt 재생성',
                            content: '빈 값으로 저장하면 System Prompt가 자동으로 재생성됩니다. 계속하시겠습니까?',
                            onOk: () => resolve(true),
                            onCancel: () => resolve(false)
                        })
                    })
                    
                    if (!confirmed) {
                        setIsSaving(false)
                        return
                    }
                    
                    await templateApi.regeneratePromptSystem(templateId)
                } else {
                    await templateApi.updatePromptSystem(templateId, promptSystem)
                }
            }
            
            antdMessage.success('프롬프트가 저장되었습니다.')
            onClose()
        } catch (error: any) {
            console.error('TemplateDetailModal > handleSave', error)
            antdMessage.error(error.message || '프롬프트 저장에 실패했습니다.')
        } finally {
            setIsSaving(false)
        }
    }
    
    return (
        <Modal
            title="템플릿 상세"
            open={open}
            onCancel={onClose}
            width={700}
            closable={!isSaving}
            maskClosable={!isSaving}
            keyboard={!isSaving}
            footer={[
                <Button key="close" onClick={onClose} disabled={isSaving}>
                    닫기
                </Button>,
                <Button
                    key="save"
                    type="primary"
                    loading={isSaving}
                    disabled={!hasAnyChanges()}
                    onClick={handleSave}
                >
                    저장
                </Button>
            ]}>
            {/* ... 기존 내용 ... */}
            
            {/* User Prompt 섹션 */}
            <div className={styles.section}>
                <h3 className={styles.sectionTitle}>User Prompt</h3>
                <textarea
                    className={styles.promptTextarea}
                    value={promptUser}
                    onChange={(e) => setPromptUser(e.target.value)}
                    placeholder="사용자 프롬프트를 입력하세요 (선택사항)"
                    rows={6}
                    disabled={isSaving}
                />
                <p className={styles.promptHint}>
                    보고서 생성 시 사용자가 추가로 정의하는 프롬프트입니다.
                </p>
            </div>
            
            {/* System Prompt 섹션 */}
            <div className={styles.section}>
                <h3 className={styles.sectionTitle}>System Prompt</h3>
                <textarea
                    className={styles.promptTextarea}
                    value={promptSystem}
                    onChange={(e) => setPromptSystem(e.target.value)}
                    placeholder="시스템 프롬프트를 입력하세요"
                    rows={10}
                    disabled={isSaving}
                />
                <p className={styles.promptHint}>
                    빈 값으로 저장 시 자동으로 재생성됩니다.
                </p>
            </div>
        </Modal>
    )
}
```

---

**최종 검토일:** 2025-11-17  
**작성자:** Claude Code  
**버전:** 1.0
