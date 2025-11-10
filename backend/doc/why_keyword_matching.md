# "왜 2번 키워드 매칭을 하는가?" - 상세 설명

## 질문
```
Placeholder가 "{{RISK}}" 같은 예측 불가능한 내용일 때,
왜 키워드 매칭을 시도하는가?
어차피 실패할 텐데 의미가 있는가?
```

---

## 답변: 🎯 **메타정보의 정확성과 유용성을 높이기 위함**

### 핵심 이유

```
목표: "모든 Placeholder를 최대한 정확하게 분류하고,
      적절한 메타정보를 제공하는 것"

이를 위해:
1️⃣ 먼저 정의된 키워드로 분류를 시도
   (정확성이 높은 경우 캐치)

2️⃣ 실패하면 기본값 사용
   (안전성 보장)
```

---

## 구체적인 예시로 이해하기

### 🔴 **시나리오: Template 업로드**

사용자가 다음과 같은 Placeholder를 가진 Template을 업로드했다고 가정:

```
{{TITLE}}
{{BACKGROUND_AND_CONTEXT}}
{{RISK_ASSESSMENT}}
{{DATE_CREATED}}
{{CUSTOM_FIELD}}
```

#### **만약 키워드 매칭을 "하지 않는다면"? ❌

```python
# 키워드 매칭 없이 모든 것을 기본값으로 처리
meta_info = [
  {
    "key": "{{TITLE}}",
    "type": "section_content",           # ❌ 기본값!
    "display_name": "TITLE 섹션",        # ❌ 부정확함
    "description": "TITLE에 해당하는 내용...",  # ❌ 이상함
  },
  {
    "key": "{{BACKGROUND_AND_CONTEXT}}",
    "type": "section_content",           # ❌ 기본값!
    "display_name": "BACKGROUND_AND_CONTEXT 섹션",  # ❌ 길고 부정확함
    "description": "BACKGROUND_AND_CONTEXT에 해당하는 내용...",
  },
  {
    "key": "{{RISK_ASSESSMENT}}",
    "type": "section_content",           # ❌ 기본값!
    "display_name": "RISK_ASSESSMENT 섹션",  # ❌ 부정확함
    "description": "RISK_ASSESSMENT에 해당하는 내용...",
  },
  {
    "key": "{{DATE_CREATED}}",
    "type": "section_content",           # ❌ 기본값! (메타데이터여야 함)
    "display_name": "DATE_CREATED 섹션",  # ❌ 틀림
    "description": "DATE_CREATED에 해당하는 내용...",  # ❌ 틀림
  },
  {
    "key": "{{CUSTOM_FIELD}}",
    "type": "section_content",
    "display_name": "CUSTOM_FIELD 섹션",
    "description": "CUSTOM_FIELD에 해당하는 내용...",
  }
]

# 문제점:
# 1. {{TITLE}}를 "TITLE 섹션"으로 표시 (보고서 제목이 아님)
# 2. {{BACKGROUND_AND_CONTEXT}}를 일반 섹션으로 표시 (배경인데!)
# 3. {{DATE_CREATED}}를 section_content로 표시 (메타데이터인데!)
# 4. 사용자는 메타정보를 보고 혼란스러움
# 5. Frontend에서 제대로 된 UI를 렌더링할 수 없음
```

---

#### **만약 키워드 매칭을 "한다면"? ✅

```python
# 키워드 매칭으로 정확한 분류
meta_info = [
  {
    "key": "{{TITLE}}",
    "type": "section_title",             # ✅ "TITLE" 포함 → section_title!
    "display_name": "보고서 제목",        # ✅ 정확함
    "description": "보고서의 명확하고 간결한 제목을...",  # ✅ 적절함
  },
  {
    "key": "{{BACKGROUND_AND_CONTEXT}}",
    "type": "section_content",           # ✅ "BACKGROUND" 포함 → 배경!
    "display_name": "배경",               # ✅ 정확함
    "description": "보고서를 작성하게 된 배경, 현황...",  # ✅ 적절함
  },
  {
    "key": "{{RISK_ASSESSMENT}}",
    "type": "section_content",           # ✅ "RISK"는 없으므로 기본값 (이 경우 맞음)
    "display_name": "RISK_ASSESSMENT 섹션",
    "description": "RISK_ASSESSMENT에 해당하는 내용...",
  },
  {
    "key": "{{DATE_CREATED}}",
    "type": "metadata",                  # ✅ "DATE" 포함 → metadata!
    "display_name": "작성 날짜",          # ✅ 정확함
    "description": "보고서 작성 날짜를 입력하세요...",  # ✅ 적절함
    "required": false,                   # ✅ 메타데이터는 선택
  },
  {
    "key": "{{CUSTOM_FIELD}}",
    "type": "section_content",           # ✅ 일치하는 키워드 없으므로 기본값
    "display_name": "CUSTOM_FIELD 섹션",
    "description": "CUSTOM_FIELD에 해당하는 내용... (모호함)",
  }
]

# 개선점:
# 1. {{TITLE}} → 정확히 "보고서 제목" (제목으로 인식)
# 2. {{BACKGROUND_AND_CONTEXT}} → 정확히 "배경" (배경 정보로 인식)
# 3. {{DATE_CREATED}} → 정확히 "작성 날짜" (메타데이터로 인식)
# 4. 사용자는 명확한 메타정보를 받음
# 5. Frontend는 정확한 UI를 렌더링 가능
```

---

## 핵심 차이점 비교

### 메타정보의 품질 향상

| 항목 | 키워드 매칭 없음 ❌ | 키워드 매칭 있음 ✅ |
|------|---|---|
| `{{TITLE}}` 분류 | section_content | section_title |
| `{{TITLE}}` display_name | "TITLE 섹션" | "보고서 제목" |
| `{{BACKGROUND_AND_CONTEXT}}` 분류 | section_content | section_content (배경) |
| `{{BACKGROUND_AND_CONTEXT}}` display_name | "BACKGROUND_AND_CONTEXT 섹션" | "배경" |
| `{{DATE_CREATED}}` 분류 | section_content | metadata |
| `{{DATE_CREATED}}` display_name | "DATE_CREATED 섹션" | "작성 날짜" |
| `{{DATE_CREATED}}` required | true | **false** |
| 사용자 경험 | 혼란스러움 ❌ | 명확함 ✅ |

---

## 왜 "정확한 분류"가 중요한가?

### 1️⃣ **Frontend UI 렌더링**

```javascript
// Frontend에서 메타정보를 받아서 UI를 구성

// 만약 {{TITLE}}이 "section_content"라면:
{
  type: "section_content",
  display_name: "TITLE 섹션"
}
// → 일반 섹션으로 렌더링 (제목처럼 보이지 않음)

// 만약 {{TITLE}}이 "section_title"이라면:
{
  type: "section_title",
  display_name: "보고서 제목"
}
// → 제목으로 렌더링 (UI에서 강조 표시, 다른 스타일 등)
```

### 2️⃣ **Claude AI의 프롬프트 지시사항**

```python
# create_dynamic_system_prompt()에서 사용

# 정확한 분류 예:
# System Prompt:
# "## 보고서 제목
#  [제목을 입력하세요]
#
#  ## 배경
#  [배경을 작성하세요]
#
#  ## 작성 날짜 (메타데이터)
#  [날짜를 입력하세요]"

# 부정확한 분류 예:
# System Prompt:
# "## TITLE 섹션
#  [TITLE 섹션 내용을 작성하세요]
#
#  ## BACKGROUND_AND_CONTEXT 섹션
#  [BACKGROUND_AND_CONTEXT 섹션 내용을 작성하세요]
#
#  ## DATE_CREATED 섹션
#  [DATE_CREATED 섹션 내용을 작성하세요]"
# → Claude는 "DATE를 섹션처럼" 생각할 수 있음
```

### 3️⃣ **사용자가 보는 가이드**

```
정확한 분류 경우:
┌─────────────────────────────┐
│ 보고서 메타정보 가이드       │
├─────────────────────────────┤
│ [필수] 보고서 제목          │
│  → 명확하고 간결한 제목     │
│  예: 2025 디지털뱅킹 분석   │
│                             │
│ [필수] 배경                 │
│  → 보고서의 배경 설명       │
│  예: 최근 디지털...         │
│                             │
│ [선택] 작성 날짜            │
│  → 보고서 작성 날짜         │
│  예: 2025-11-08            │
└─────────────────────────────┘

부정확한 분류 경우:
┌─────────────────────────────┐
│ 보고서 메타정보 가이드       │
├─────────────────────────────┤
│ [필수] TITLE 섹션           │
│  → TITLE 섹션 내용...       │
│  예: TITLE에 해당...        │ ❌ 이게 뭐지?
│                             │
│ [필수] BACKGROUND_AND_...   │
│  → BACKGROUND_AND_...에...  │
│  예: BACKGROUND_AND_...     │ ❌ 이것도 뭐지?
│                             │
│ [필수] DATE_CREATED 섹션    │
│  → DATE_CREATED 섹션...     │
│  예: DATE_CREATED...        │ ❌ 이것도 뭐지?
└─────────────────────────────┘
```

---

## 실제 결과의 차이

### 🔴 **키워드 매칭 없는 경우**

**User가 보는 Template 정보:**
```
템플릿: "재무보고서"
Placeholder:
- TITLE 섹션 (필수)
- BACKGROUND_AND_CONTEXT 섹션 (필수)
- RISK_ASSESSMENT 섹션 (필수)
- DATE_CREATED 섹션 (필수)
- CUSTOM_FIELD 섹션 (필수)

→ 사용자: "뭐가 필수고, 뭐가 선택인지 알 수 없음"
```

### 🟢 **키워드 매칭 있는 경우**

**User가 보는 Template 정보:**
```
템플릿: "재무보고서"
필수 정보:
- 보고서 제목 (제목/헤더)
- 배경 (배경/문제인식)
- RISK_ASSESSMENT 섹션 (내용)
- CUSTOM_FIELD 섹션 (내용)

선택 정보:
- 작성 날짜 (메타데이터)

→ 사용자: "아, 제목과 배경, 내용이 필수이고, 날짜는 선택이구나!"
```

---

## 결론

### ❌ **키워드 매칭을 "하지 않으면"**
- 모든 Placeholder가 동일하게 "섹션"으로 처리됨
- 메타정보의 의미가 명확하지 않음
- Frontend/사용자가 혼란스러워함
- Claude AI도 지시사항을 제대로 해석하기 어려움

### ✅ **키워드 매칭을 "하면"**
- 정의된 Placeholder는 정확하게 분류됨
- 메타정보의 의미가 명확함
- Frontend는 적절한 UI를 렌더링할 수 있음
- 사용자는 명확한 가이드를 받음
- Claude AI도 지시사항을 정확하게 해석함
- 예측 불가능한 Placeholder도 "기본값"으로 안전하게 처리됨

---

## 요약

```
질문: "왜 키워드 매칭을 하는가?"
답: "최대한 정확한 메타정보를 제공하기 위해"

상세:
1. 정의된 키워드는 정확하게 분류
   (TITLE → section_title, DATE → metadata 등)

2. 정의되지 않은 키워드는 기본값으로 안전하게 처리
   (RISK_ASSESSMENT, CUSTOM_FIELD → section_content)

3. 결과: 모든 경우에 유용한 메타정보 제공 ✅
```

---

## 추가 예시

### 예시 1: 일반적인 경우

```python
placeholders = [
    "{{TITLE}}",           # 정의됨
    "{{SUMMARY}}",         # 정의됨
    "{{BACKGROUND}}",      # 정의됨
    "{{CONCLUSION}}",      # 정의됨
    "{{DATE}}",            # 정의됨
]

# 결과: 5개 모두 정확하게 분류 ✅
```

### 예시 2: 혼합된 경우

```python
placeholders = [
    "{{TITLE}}",                    # 정의됨 → section_title
    "{{RISK_ANALYSIS}}",            # 미정의 → section_content (기본값)
    "{{PUBLISH_DATE}}",             # "DATE" 포함 → metadata
    "{{EXECUTIVE_SUMMARY}}",        # "SUMMARY" 포함 → section_content (요약)
]

# 결과:
# - 4개 중 3개는 정확하게 분류
# - 1개는 기본값으로 안전하게 처리
# → 최상의 결과! ✅
```

### 예시 3: 모두 예측 불가능한 경우

```python
placeholders = [
    "{{MARKET_SIZE}}",
    "{{COMPETITOR_INFO}}",
    "{{REGULATORY_STATUS}}",
]

# 결과:
# - 3개 모두 기본값으로 처리
# - 하지만 안전하고, display_name 자동 생성됨
# → "기본값이지만 사용 가능한" 메타정보 제공 ✅
```
