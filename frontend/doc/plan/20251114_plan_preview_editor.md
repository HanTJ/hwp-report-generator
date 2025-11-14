# Plan Preview Editor 구현 계획

**작성일:** 2025-11-14
**목적:** 보고서 계획(Plan) 수정 기능 추가
**현재 구조:** OutlineActionButtons의 "수정" 버튼 클릭 시 계획 편집 가능한 사이드바 추가

---

## 1. 요구사항 분석

### 1.1 현재 동작
- `OutlineActionButtons`에서 "수정" 버튼 클릭 시 `onContinue` 호출
- `onContinue`는 버튼만 숨기고 ChatInput에 포커스

### 1.2 변경할 동작
1. **"수정" 버튼 클릭 시**:
   - PlanPreview 토글 (열기/닫기)
   - `OutlineActionButtons`는 **유지** (사라지지 않음)
2. **우측에서 PlanPreview 사이드바 슬라이드 인** (ReportPreview와 유사한 UI)
3. PlanPreview 내용은 **편집 가능** (Markdown 텍스트 에디터)
4. 우측 상단 액션:
   - **"보고서 생성" 버튼**: 현재 편집된 내용으로 보고서 생성
   - **"닫기" 버튼**: PlanPreview만 닫기 (OutlineActionButtons는 유지)
5. **OutlineActionButtons "생성" 버튼 클릭 시**:
   - 원본 plan으로 보고서 생성
   - OutlineActionButtons 사라짐
   - PlanPreview가 열려있다면 닫기
6. **PlanPreview "보고서 생성" 버튼 클릭 시**:
   - 편집된 plan으로 보고서 생성
   - OutlineActionButtons 사라짐
   - PlanPreview 자동 닫기

---

## 2. 구현 대상 파일

### 2.1 신규 파일

| 파일 경로 | 역할 |
|---------|------|
| `frontend/src/components/plan/PlanPreview.tsx` | 계획 편집 사이드바 컴포넌트 |
| `frontend/src/components/plan/PlanPreview.module.css` | PlanPreview 스타일 (ReportPreview.module.css 기반) |

### 2.2 수정할 파일

| 파일 경로 | 수정 내용 |
|---------|----------|
| `frontend/src/pages/MainPage.tsx` | - PlanPreview 상태 관리 추가<br>- handleContinueOutline 수정 (PlanPreview 토글, OutlineActionButtons 유지)<br>- handleGenerateFromOutline 수정 (PlanPreview 닫기)<br>- handleGenerateFromEditedPlan 추가 (편집된 plan 사용) |
| `frontend/src/components/OutlineMessage.tsx` | - showButtons 상태 관리 변경 (생성 시에만 숨김) |
| `frontend/src/stores/useTopicStore.ts` | - updatePlan() 액션 추가 (plan 수정용) |

### 2.3 참조 파일 (변경 없음)

| 파일 경로 | 참조 목적 |
|---------|----------|
| `frontend/src/components/report/ReportPreview.tsx` | PlanPreview UI/UX 레퍼런스 |
| `frontend/src/components/report/ReportPreview.module.css` | 스타일 레퍼런스 |
| `frontend/src/components/chat/OutlineActionButtons.tsx` | 버튼 동작 이해 |

---

## 3. 상세 설계

### 3.1 PlanPreview 컴포넌트

#### Props
```typescript
interface PlanPreviewProps {
    plan: string              // 마크다운 형식 계획 내용
    onClose: () => void       // 닫기 핸들러
    onGenerate: (editedPlan: string) => void  // 보고서 생성 핸들러
}
```

#### UI 구조
```
┌─────────────────────────────┐
│ 계획 수정              [생성][X] │ ← Header
├─────────────────────────────┤
│                             │
│  [Textarea - Markdown]      │ ← Content (편집 가능)
│                             │
│                             │
│                             │
└─────────────────────────────┘
```

#### 주요 기능
- **Textarea**: 마크다운 직접 편집 가능
- **보고서 생성 버튼**:
  - 클릭 시 `onGenerate(editedPlan)` 호출
  - 버튼 스타일: primary (파란색)
- **닫기 버튼**:
  - 클릭 시 `onClose()` 호출
  - 아이콘: `CloseOutlined`

#### 스타일
- ReportPreview.module.css 기반으로 작성
- `.planPreviewSidebar`: width 28rem, 우측 슬라이드 인 애니메이션
- `.editableTextarea`:
  - 전체 높이 사용
  - 마크다운 스타일 적용 (선택사항: 미리보기 탭 추가 가능)
  - font-family: monospace (코드 에디터 느낌)
  - line-height: 1.8

### 3.2 MainPage 수정

#### State 추가
```typescript
const [planPreviewOpen, setPlanPreviewOpen] = useState(false)
const [editablePlan, setEditablePlan] = useState<string>('')
```

#### handleContinueOutline 수정
```typescript
const handleContinueOutline = () => {
    // PlanPreview 토글 (열기/닫기)
    // OutlineActionButtons는 유지됨

    if (planPreviewOpen) {
        // 이미 열려있으면 아무 동작 안 함
        return
    }

    const currentPlan = useTopicStore.getState().plan?.plan || ''
    if (!currentPlan) {
        antdMessage.error('계획 정보가 없습니다.')
        return
    }

    setEditablePlan(currentPlan)
    setPlanPreviewOpen(true)
}
```

#### handleGenerateFromOutline 수정
```typescript
const handleGenerateFromOutline = async () => {
    // OutlineActionButtons "생성" 버튼 클릭 시
    // 1. PlanPreview가 열려있다면 닫기
    if (planPreviewOpen) {
        setPlanPreviewOpen(false)
    }

    // 2. 원본 plan으로 보고서 생성
    await generateReportFromPlan(setIsLoadingMessages)
    // generateReportFromPlan 내부에서 OutlineActionButtons가 사라짐
}
```

#### handleGenerateFromEditedPlan (신규)
```typescript
const handleGenerateFromEditedPlan = async (editedPlan: string) => {
    // PlanPreview "보고서 생성" 버튼 클릭 시
    // 1. plan 상태 업데이트
    const {updatePlan} = useTopicStore.getState()
    updatePlan(editedPlan)

    // 2. PlanPreview 닫기
    setPlanPreviewOpen(false)

    // 3. 편집된 plan으로 보고서 생성
    await generateReportFromPlan(setIsLoadingMessages)
    // generateReportFromPlan 내부에서 OutlineActionButtons가 사라짐
}
```

#### JSX 추가
```tsx
{planPreviewOpen && (
    <PlanPreview
        plan={editablePlan}
        onClose={() => setPlanPreviewOpen(false)}
        onGenerate={handleGenerateFromEditedPlan}
    />
)}
```

### 3.3 useTopicStore 수정

#### updatePlan 액션 추가
```typescript
interface TopicStore {
    // ...
    updatePlan: (newPlan: string) => void
}

// Implementation
updatePlan: (newPlan) => {
    set((state) => {
        if (!state.plan) return state

        return {
            plan: {
                ...state.plan,
                plan: newPlan  // plan.plan 필드 업데이트
            }
        }
    })
}
```

---

## 4. 사이드 이펙트 분석

### 4.1 긍정적 효과
1. **UX 개선**: 계획 수정 시 시각적 피드백
2. **일관성**: ReportPreview와 유사한 UI/UX 패턴
3. **명확성**: 편집 상태와 일반 대화 상태 분리

### 4.2 잠재적 문제 및 해결

#### 문제 1: ReportPreview와 PlanPreview 동시 열림
- **상황**: 사용자가 보고서 미리보기 중에 계획 수정 시도
- **해결**:
  - PlanPreview 열 때 ReportPreview 자동 닫기
  - 또는 둘 중 하나만 열리도록 상호 배타적 관리

```typescript
const handleContinueOutline = () => {
    // ReportPreview가 열려있으면 닫기
    if (selectedReport) {
        setSelectedReport(null)
    }

    const currentPlan = useTopicStore.getState().plan?.plan || ''
    setEditablePlan(currentPlan)
    setPlanPreviewOpen(true)
}
```

#### 문제 2: 편집 중 사용자가 새 메시지 전송
- **상황**: PlanPreview 열린 상태에서 ChatInput 사용 가능
- **해결**:
  - Option A: ChatInput 비활성화 (`disabled={planPreviewOpen}`)
  - Option B: 허용하되 PlanPreview 자동 닫기 (경고 메시지)

**권장**: Option A (혼란 방지)

```tsx
<ChatInput
    ref={chatInputRef}
    onSend={handleSendMessage}
    disabled={isGeneratingMessage || isLoadingMessages || planPreviewOpen}
    // ...
/>
```

#### 문제 3: 브라우저 뒤로가기 시 PlanPreview 상태 유지
- **상황**: PlanPreview 열린 상태에서 브라우저 뒤로가기
- **해결**:
  - useEffect cleanup에서 PlanPreview 닫기
  - 이미 MainPage.tsx:60-81에 cleanup 로직 존재

```typescript
useEffect(() => {
    return () => {
        // 기존 cleanup + PlanPreview 닫기
        setPlanPreviewOpen(false)
        setEditablePlan('')
    }
}, [])
```

#### 문제 4: 편집 내용 손실
- **상황**: 사용자가 편집 중 실수로 닫기 클릭
- **해결**:
  - 닫기 전 확인 다이얼로그 (변경사항 있을 때만)
  - 또는 임시 저장 (로컬 스토리지)

**권장**: 간단하게 구현 - 확인 다이얼로그 없이 즉시 닫기 (v1)
- 추후 필요 시 `antd Modal.confirm()` 추가

#### 문제 5: Markdown 편집 UX
- **상황**: 일반 Textarea는 마크다운 편집에 불편
- **해결 (선택사항)**:
  - v1: 단순 Textarea (빠른 구현)
  - v2: react-markdown-editor-lite 같은 라이브러리 (추후)

**권장**: v1으로 시작 (의존성 추가 최소화)

#### 문제 6: 계획 생성 후 서버 동기화
- **상황**: `updatePlan()`으로 로컬 상태만 변경, 서버에 반영 안 됨
- **해결**:
  - 서버는 plan 자체를 저장하지 않음 (topic_id만 반환)
  - `generateReportFromPlan()`에서 plan 내용을 파라미터로 전달
  - 따라서 **문제 없음** (로컬 상태만 사용)

---

## 5. 구현 순서

### Step 1: PlanPreview 컴포넌트 생성
- [ ] `PlanPreview.tsx` 생성
- [ ] `PlanPreview.module.css` 생성 (ReportPreview 기반)
- [ ] Props 정의 및 기본 UI 구현
- [ ] Textarea 편집 기능 구현
- [ ] 버튼 동작 연결 (onClose, onGenerate)

### Step 2: useTopicStore 수정
- [ ] `updatePlan` 액션 추가
- [ ] 타입 정의 업데이트

### Step 3: MainPage 수정
- [ ] State 추가 (`planPreviewOpen`, `editablePlan`)
- [ ] `handleContinueOutline` 수정
- [ ] `handleGenerateFromEditedPlan` 추가
- [ ] JSX에 PlanPreview 추가
- [ ] ChatInput disabled 조건 추가

### Step 4: 사이드 이펙트 처리
- [ ] ReportPreview와 상호 배타적 처리
- [ ] cleanup 로직 추가 (useEffect)
- [ ] 테스트: 편집 → 생성 플로우
- [ ] 테스트: 닫기 → 다시 열기

### Step 5: 스타일링 및 UX 개선
- [ ] 슬라이드 애니메이션 확인
- [ ] 반응형 디자인 (모바일)
- [ ] 접근성 (aria-label, keyboard navigation)

---

## 6. 테스트 시나리오

### 6.1 정상 플로우
1. 새 토픽 시작 → 메시지 입력 → 계획 생성
2. "수정" 버튼 클릭 → PlanPreview 열림
3. 계획 내용 수정 (예: 섹션 추가/삭제)
4. "보고서 생성" 클릭 → 편집된 계획으로 보고서 생성
5. PlanPreview 자동 닫기 → 보고서 결과 확인

### 6.2 예외 플로우
1. PlanPreview 열린 상태에서 "닫기" 클릭 → 정상 닫힘
2. PlanPreview 열린 상태에서 ReportPreview 열기 → PlanPreview 자동 닫힘
3. PlanPreview 열린 상태에서 ChatInput 비활성화 확인
4. 브라우저 뒤로가기 → PlanPreview 정리 확인

### 6.3 에러 플로우
1. plan 데이터 없을 때 "수정" 클릭 → 에러 메시지 표시
2. 빈 plan으로 "보고서 생성" 클릭 → 검증 후 에러 메시지

---

## 7. UI/UX 상세 스펙

### 7.1 색상 및 타이포그래피
- 헤더 배경: `#ffffff`
- 제목: `font-weight: 600`, `font-size: 1rem`, `color: #1a1a1a`
- 생성 버튼: `#1976d2` (primary blue)
- 닫기 버튼: `#666666` (gray)

### 7.2 레이아웃
- Width: `28rem` (ReportPreview와 동일)
- Height: `100vh`
- Position: `fixed`, `right: 0`
- Z-index: `100`
- Shadow: `-2px 0 8px rgba(0, 0, 0, 0.1)`

### 7.3 애니메이션
- 슬라이드 인: `transform: translateX(100%) → translateX(0)`
- Duration: `0.3s`
- Easing: `ease-out`

### 7.4 Textarea 스펙
- Font: `font-family: 'Courier New', monospace`
- Font size: `0.875rem`
- Line height: `1.8`
- Padding: `1.5rem`
- Border: `none`
- Background: `#fafafa` (연한 회색)
- Resize: `none` (고정)

---

## 8. 향후 개선 가능성

### v2 기능 (선택사항)
1. **Markdown 미리보기 탭**
   - 편집/미리보기 토글 버튼
   - react-markdown으로 렌더링

2. **실시간 자동 저장**
   - 로컬 스토리지에 임시 저장
   - 브라우저 새로고침 시 복구

3. **편집 이력 (Undo/Redo)**
   - Ctrl+Z / Ctrl+Shift+Z 지원
   - 간단한 스택 관리

4. **AI 제안 기능**
   - "계획 개선" 버튼
   - Claude API로 계획 보완 제안

5. **템플릿 기반 섹션 추가**
   - 드롭다운에서 섹션 선택 → 자동 삽입

---

## 9. 코드 예시

### PlanPreview.tsx (초안)
```typescript
import React, {useState} from 'react'
import {CloseOutlined, CheckOutlined} from '@ant-design/icons'
import styles from './PlanPreview.module.css'

interface PlanPreviewProps {
    plan: string
    onClose: () => void
    onGenerate: (editedPlan: string) => void
}

const PlanPreview: React.FC<PlanPreviewProps> = ({plan, onClose, onGenerate}) => {
    const [editedPlan, setEditedPlan] = useState(plan)

    const handleGenerate = () => {
        if (!editedPlan.trim()) {
            alert('계획 내용을 입력해주세요.')
            return
        }
        onGenerate(editedPlan)
    }

    return (
        <div className={styles.planPreviewSidebar}>
            <div className={styles.previewHeader}>
                <div className={styles.previewTitle}>
                    <span>계획 수정</span>
                </div>
                <div className={styles.previewActions}>
                    <button
                        className={`${styles.previewActionBtn} ${styles.generate}`}
                        onClick={handleGenerate}
                        title="보고서 생성"
                    >
                        <CheckOutlined />
                    </button>
                    <button
                        className={`${styles.previewActionBtn} ${styles.close}`}
                        onClick={onClose}
                        title="닫기"
                    >
                        <CloseOutlined />
                    </button>
                </div>
            </div>

            <div className={styles.previewContent}>
                <textarea
                    className={styles.editableTextarea}
                    value={editedPlan}
                    onChange={(e) => setEditedPlan(e.target.value)}
                    placeholder="보고서 계획을 입력하세요..."
                />
            </div>
        </div>
    )
}

export default PlanPreview
```

### MainPage 수정 (주요 부분)
```typescript
// State 추가
const [planPreviewOpen, setPlanPreviewOpen] = useState(false)
const [editablePlan, setEditablePlan] = useState<string>('')

// Handler 수정
const handleContinueOutline = () => {
    // ReportPreview 닫기
    if (selectedReport) {
        setSelectedReport(null)
    }

    const currentPlan = useTopicStore.getState().plan?.plan || ''
    if (!currentPlan) {
        antdMessage.error('계획 정보가 없습니다.')
        return
    }

    setEditablePlan(currentPlan)
    setPlanPreviewOpen(true)
}

const handleGenerateFromEditedPlan = async (editedPlan: string) => {
    const {updatePlan} = useTopicStore.getState()
    updatePlan(editedPlan)
    setPlanPreviewOpen(false)
    await generateReportFromPlan(setIsLoadingMessages)
}

// JSX 추가 (ReportPreview 옆)
{planPreviewOpen && (
    <PlanPreview
        plan={editablePlan}
        onClose={() => setPlanPreviewOpen(false)}
        onGenerate={handleGenerateFromEditedPlan}
    />
)}

// ChatInput disabled 조건
<ChatInput
    disabled={isGeneratingMessage || isLoadingMessages || planPreviewOpen}
    // ...
/>
```

---

## 10. 체크리스트

### 구현 전 확인
- [ ] 요구사항 명확화 완료
- [ ] 사이드 이펙트 분석 완료
- [ ] ReportPreview 코드 리뷰 완료

### 구현 중 확인
- [ ] TypeScript 타입 에러 없음
- [ ] Console 에러/경고 없음
- [ ] 기존 기능 정상 동작 (회귀 테스트)

### 구현 후 확인
- [ ] 모든 테스트 시나리오 통과
- [ ] 모바일 반응형 확인
- [ ] 접근성 검증 (키보드 네비게이션)
- [ ] 코드 리뷰 및 리팩토링

---

**최종 검토일:** 2025-11-14
**작성자:** Claude Code
**버전:** 1.0
