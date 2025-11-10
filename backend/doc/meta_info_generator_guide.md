# meta_info_generator.py 상세 설명서

## 목차
1. [개요](#개요)
2. [동작 원리](#동작-원리)
3. [Placeholder 분류 규칙](#placeholder-분류-규칙)
4. [엣지 케이스 처리](#엣지-케이스-처리)
5. [실행 흐름 (Flow Chart)](#실행-흐름)
6. [코드 예시](#코드-예시)
7. [주요 메서드 설명](#주요-메서드-설명)

---

## 개요

### 목적
`meta_info_generator.py`는 Template 업로드 시 추출된 **Placeholder를 분석**하여 각 Placeholder에 맞는 **메타정보 JSON**을 자동 생성하는 유틸리티입니다.

### 입출력
```
입력: Placeholder 객체 리스트
  [
    Placeholder(placeholder_key="{{TITLE}}"),
    Placeholder(placeholder_key="{{SUMMARY}}"),
    Placeholder(placeholder_key="{{CUSTOM_FIELD}}")
  ]

출력: 메타정보 JSON 배열
  [
    {
      "key": "{{TITLE}}",
      "type": "section_title",
      "display_name": "보고서 제목",
      "description": "보고서의 명확한 제목을 작성하세요...",
      "examples": ["2025 디지털뱅킹 트렌드 분석"],
      "required": true,
      "order_hint": 1
    },
    ...
  ]
```

### 핵심 기능
```
✅ Placeholder 이름에서 자동 키워드 분류
✅ 예측 불가능한 Placeholder도 안전한 기본값 제공
✅ 한글 display_name 자동 생성
✅ 상세 설명 및 예시 자동 생성
✅ required 필드 자동 판단
✅ 추천 순서(order_hint) 자동 계산
```

---

## 동작 원리

### 핵심 알고리즘

```
FOR EACH placeholder IN placeholders:
  1. placeholder_key에서 {{ }} 제거
     "{{TITLE}}" → "TITLE"

  2. 키워드 매칭 수행 (우선순위 순)
     ┌─ "TITLE" 포함? → type="section_title"
     ├─ "SUMMARY" 포함? → type="section_content" (요약)
     ├─ "BACKGROUND" 포함? → type="section_content" (배경)
     ├─ "CONCLUSION" 포함? → type="section_content" (결론)
     ├─ "DATE" 포함? → type="metadata" (날짜)
     └─ 모두 해당 안 함? → type="section_content" (기본값)

  3. 매칭된 타입에 따라 메타정보 구성
     ├─ display_name: 사전에서 조회 (없으면 기본명 생성)
     ├─ description: 상세 설명 자동 생성
     ├─ examples: 예시 자동 생성
     ├─ required: 타입이 "metadata"가 아니면 true
     └─ order_hint: 타입별 기본 순서값
```

---

## Placeholder 분류 규칙

### 1️⃣ 정의된 키워드 (우선순위 순)

| 키워드 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| TITLE | `section_title` | 제목/헤더 관련 | `{{TITLE}}`, `{{REPORT_TITLE}}` |
| SUMMARY | `section_content` | 요약 섹션 | `{{SUMMARY}}`, `{{EXEC_SUMMARY}}` |
| BACKGROUND | `section_content` | 배경/문제인식 | `{{BACKGROUND}}`, `{{INTRO_BACKGROUND}}` |
| CONCLUSION | `section_content` | 결론/제언 | `{{CONCLUSION}}`, `{{FINAL_CONCLUSION}}` |
| DATE | `metadata` | 날짜/메타데이터 | `{{DATE}}`, `{{REPORT_DATE}}` |

### 2️⃣ 분류 매칭 방식

```python
# 키워드 "포함" 검사 (정확한 일치 아님!)
if "TITLE" in "REPORT_TITLE":      # ✅ True → section_title
if "TITLE" in "MONTHLY_REPORT":    # ❌ False → 기본값

if "SUMMARY" in "EXEC_SUMMARY":    # ✅ True → 요약
if "SUMMARY" in "SUMMARY_DATA":    # ✅ True → 요약

if "BACKGROUND" in "BACKGROUND":   # ✅ True → 배경
if "BACKGROUND" in "INTRO":        # ❌ False → 기본값

if "CONCLUSION" in "CONCLUSION":   # ✅ True → 결론
if "CONCLUSION" in "FINAL_WORDS":  # ❌ False → 기본값

if "DATE" in "DATE":               # ✅ True → 메타데이터
if "DATE" in "CREATED_DATE":       # ✅ True → 메타데이터
if "DATE" in "REPORT_DATE":        # ✅ True → 메타데이터
```

### 3️⃣ 우선순위

```
매칭 순서 (우선순위):
1. "TITLE" 검사
2. "SUMMARY" 검사
3. "BACKGROUND" 검사
4. "CONCLUSION" 검사
5. "DATE" 검사
6. 모두 실패 → 기본값 사용

주의: 첫 번째 매칭되는 키워드를 사용하고 나머지는 검사하지 않음!
```

---

## 엣지 케이스 처리

### 시나리오별 동작

#### 📌 **시나리오 1: 정의된 키워드 포함**

```python
# 입력
placeholders = [
    Placeholder(placeholder_key="{{REPORT_TITLE}}"),
    Placeholder(placeholder_key="{{EXEC_SUMMARY}}"),
]

# 동작
"TITLE" in "REPORT_TITLE"     # ✅ True → section_title
"SUMMARY" in "EXEC_SUMMARY"   # ✅ True → section_content (요약)

# 출력
[
  {
    "key": "{{REPORT_TITLE}}",
    "type": "section_title",
    "display_name": "보고서 제목",
    "description": "보고서의 명확하고 간결한 제목을 작성하세요...",
    "examples": ["2025 디지털뱅킹 트렌드 분석"],
    "required": true,
    "order_hint": 1
  },
  {
    "key": "{{EXEC_SUMMARY}}",
    "type": "section_content",
    "display_name": "요약",
    "description": "2-3문단으로 보고서의 핵심 내용을 요약합니다...",
    "examples": ["최근 디지털 채널 이용률이 75%를 초과..."],
    "required": true,
    "order_hint": 2
  }
]
```

---

#### 📌 **시나리오 2: 예측 불가능한 Placeholder (⭐ 핵심)**

```python
# 입력
placeholders = [
    Placeholder(placeholder_key="{{RISK}}"),
    Placeholder(placeholder_key="{{MARKET_ANALYSIS}}"),
    Placeholder(placeholder_key="{{CUSTOM_FIELD}}"),
]

# 동작 분석

# 1. "{{RISK}}"
key_name = "RISK"
"TITLE" in "RISK"       # ❌ False
"SUMMARY" in "RISK"     # ❌ False
"BACKGROUND" in "RISK"  # ❌ False
"CONCLUSION" in "RISK"  # ❌ False
"DATE" in "RISK"        # ❌ False
→ 모두 실패! 기본값 사용

# 2. "{{MARKET_ANALYSIS}}"
key_name = "MARKET_ANALYSIS"
"TITLE" in "MARKET_ANALYSIS"       # ❌ False
... (모두 False)
→ 기본값 사용

# 3. "{{CUSTOM_FIELD}}"
key_name = "CUSTOM_FIELD"
... (모두 False)
→ 기본값 사용

# 출력 (기본값)
[
  {
    "key": "{{RISK}}",
    "type": "section_content",          # ← 기본값
    "display_name": "RISK 섹션",        # ← 자동 생성
    "description": "RISK에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)",
    "examples": ["RISK에 해당하는 예시를 제공하세요."],
    "required": true,
    "order_hint": 2
  },
  {
    "key": "{{MARKET_ANALYSIS}}",
    "type": "section_content",
    "display_name": "MARKET_ANALYSIS 섹션",
    "description": "MARKET_ANALYSIS에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)",
    "examples": ["MARKET_ANALYSIS에 해당하는 예시를 제공하세요."],
    "required": true,
    "order_hint": 2
  },
  {
    "key": "{{CUSTOM_FIELD}}",
    "type": "section_content",
    "display_name": "CUSTOM_FIELD 섹션",
    "description": "CUSTOM_FIELD에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)",
    "examples": ["CUSTOM_FIELD에 해당하는 예시를 제공하세요."],
    "required": true,
    "order_hint": 2
  }
]
```

---

#### 📌 **시나리오 3: 혼합된 Placeholder**

```python
# 입력
placeholders = [
    Placeholder(placeholder_key="{{TITLE}}"),
    Placeholder(placeholder_key="{{RISK}}"),
    Placeholder(placeholder_key="{{DATE}}"),
    Placeholder(placeholder_key="{{EXEC_SUMMARY}}"),
]

# 동작
{{TITLE}}       → section_title (정의됨)
{{RISK}}        → section_content (기본값)
{{DATE}}        → metadata (정의됨)
{{EXEC_SUMMARY}}→ section_content (정의됨, 요약)

# 출력
[
  {
    "key": "{{TITLE}}",
    "type": "section_title",
    "display_name": "보고서 제목",
    "description": "보고서의 명확하고 간결한 제목을...",
    "examples": ["2025 디지털뱅킹 트렌드 분석"],
    "required": true,
    "order_hint": 1          # ← section_title
  },
  {
    "key": "{{RISK}}",
    "type": "section_content",
    "display_name": "RISK 섹션",
    "description": "RISK에 해당하는 내용을...",
    "examples": ["RISK에 해당하는 예시..."],
    "required": true,
    "order_hint": 2          # ← section_content (기본)
  },
  {
    "key": "{{DATE}}",
    "type": "metadata",
    "display_name": "작성 날짜",
    "description": "보고서 작성 날짜를 입력하세요...",
    "examples": ["2025-11-08"],
    "required": false,       # ← metadata는 required=false
    "order_hint": 0          # ← metadata는 우선순위 0
  },
  {
    "key": "{{EXEC_SUMMARY}}",
    "type": "section_content",
    "display_name": "요약",
    "description": "2-3문단으로 보고서의 핵심 내용을...",
    "examples": ["최근 디지털 채널 이용률이..."],
    "required": true,
    "order_hint": 2          # ← section_content (요약)
  }
]
```

---

#### 📌 **시나리오 4: 중복되고 예측 불가능한 Placeholder**

```python
# 입력
placeholders = [
    Placeholder(placeholder_key="{{TITLE}}"),
    Placeholder(placeholder_key="{{CUSTOM_TITLE}}"),
    Placeholder(placeholder_key="{{ANOTHER_CUSTOM}}"),
]

# 동작
{{TITLE}}           → "TITLE" in "TITLE" → ✅ section_title
{{CUSTOM_TITLE}}    → "TITLE" in "CUSTOM_TITLE" → ✅ section_title
{{ANOTHER_CUSTOM}}  → 모든 키워드 불일치 → ❌ 기본값 (section_content)

# 출력
[
  {
    "key": "{{TITLE}}",
    "type": "section_title",
    "display_name": "보고서 제목",
    ...
  },
  {
    "key": "{{CUSTOM_TITLE}}",
    "type": "section_title",
    "display_name": "보고서 제목",    # ← 같은 display_name!
    ...
  },
  {
    "key": "{{ANOTHER_CUSTOM}}",
    "type": "section_content",        # ← 기본값
    "display_name": "ANOTHER_CUSTOM 섹션",
    ...
  }
]
```

---

## 실행 흐름

### Flowchart

```
┌─────────────────────────────────────────────────────┐
│ create_meta_info_from_placeholders(placeholders)   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ meta_info = []       │
        │ order_hints = {...}  │
        └──────────────────────┘
                   │
                   ▼
        ╔════════════════════════════╗
        ║ FOR EACH placeholder      ║
        ╚════════════════════╤═══════╝
                             │
                   ┌─────────▼────────────┐
                   │ key_name 추출        │
                   │ "{{TITLE}}" → "TITLE"
                   └─────────┬────────────┘
                             │
                   ┌─────────▼────────────────────┐
                   │ 키워드 매칭 시작             │
                   └─────────┬────────────────────┘
                             │
                ┌────────────┼────────────┬────────────┬────────────┐
                │            │            │            │            │
          ▼─────▼──────┐  ▼──────────┐  ▼──────────┐  ▼──────────┐  ▼──────┐
    "TITLE"포함?      │"SUMMARY"포함? │"BACKGROUND"|"CONCLUSION"|"DATE"포함?
         │            │포함?          │포함?       │포함?       │
        ✅ Yes        │ ✅ Yes       │ ✅ Yes    │ ✅ Yes    │ ✅ Yes
         │            │              │           │           │
         ▼            ▼              ▼           ▼           ▼
    section_title  section_content section_content section_content metadata
         │            │ (요약)      │ (배경)     │ (결론)    │
         └────────────┴──────────────┴───────────┴───────────┘
                             │
                   ┌─────────▼──────────────────┐
                   │ 모두 No?                  │
                   │ → 기본값 사용              │
                   │   type = section_content  │
                   └─────────┬──────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ 메타정보 구성 시작             │
                   │ 1. key 지정                    │
                   │ 2. type 지정                   │
                   └─────────┬──────────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ _get_display_name() 호출       │
                   │ (사전 조회 또는 기본값 생성)   │
                   └─────────┬──────────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ _get_description() 호출        │
                   │ (상세 설명 자동 생성)          │
                   │ (애매하면 주석 추가)            │
                   └─────────┬──────────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ _get_examples() 호출           │
                   │ (예시 자동 생성)               │
                   └─────────┬──────────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ required 판단                  │
                   │ type == "metadata" → false    │
                   │ else → true                   │
                   └─────────┬───────���──────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ order_hint 지정                │
                   │ order_hints[type]를 조회      │
                   └─────────┬──────────────────────┘
                             │
                   ┌─────────▼──────────────────────┐
                   │ meta_item 완성                 │
                   │ meta_info.append()             │
                   └─────────┬──────────────────────┘
                             │
                    ┌────────┴──────────┐
                    │ 다음 placeholder? │
                    └────────┬──────────┘
                             │
                        ┌────▼────┐
                        │ 있음?   │
                        └┬─────┬──┘
                       Yes     No
                         │     │
                         ▼     ▼
                      반복   return meta_info
```

---

## 코드 예시

### 예시 1: 표준 Placeholder

```python
from app.utils.meta_info_generator import create_meta_info_from_placeholders

placeholders = [
    type('Placeholder', (), {'placeholder_key': '{{TITLE}}'})(),
    type('Placeholder', (), {'placeholder_key': '{{SUMMARY}}'})(),
    type('Placeholder', (), {'placeholder_key': '{{BACKGROUND}}'})(),
]

meta_info = create_meta_info_from_placeholders(placeholders)

# 결과
# [
#   {
#     "key": "{{TITLE}}",
#     "type": "section_title",
#     "display_name": "보고서 제목",
#     "description": "보고서의 명확하고 간결한 제목을 작성하세요. 주요 주제를 한 문장으로 표현해야 합니다.",
#     "examples": ["2025 디지털뱅킹 트렌드 분석", "모바일 뱅킹 고도화 방안"],
#     "required": true,
#     "order_hint": 1
#   },
#   {
#     "key": "{{SUMMARY}}",
#     "type": "section_content",
#     "display_name": "요약",
#     "description": "2-3문단으로 보고서의 핵심 내용을 요약합니다. 독자가 전체 내용을 빠르게 파악할 수 있도록 작성해주세요.",
#     "examples": ["최근 디지털 채널 이용률이 75%를 초과함에 따라 모바일 채널 고도화 필요성이 대두되었습니다."],
#     "required": true,
#     "order_hint": 2
#   },
#   {
#     "key": "{{BACKGROUND}}",
#     "type": "section_content",
#     "display_name": "배경",
#     "description": "보고서를 작성하게 된 배경, 현황, 문제의식을 설명합니다. 독자가 이후 내용을 이해하는 데 필요한 최소한의 맥락을 제공해주세요.",
#     "examples": ["당 행의 전자금융 이용자는 전년도 대비 45% 증가하였으며, 특히 20-40대 이용자가 전체의 68%를 차지하고 있습니다."],
#     "required": true,
#     "order_hint": 2
#   }
# ]
```

### 예시 2: 예측 불가능한 Placeholder

```python
placeholders = [
    type('Placeholder', (), {'placeholder_key': '{{MARKET_RISK}}'})(),
    type('Placeholder', (), {'placeholder_key': '{{COMPETITOR_ANALYSIS}}'})(),
]

meta_info = create_meta_info_from_placeholders(placeholders)

# 결과
# [
#   {
#     "key": "{{MARKET_RISK}}",
#     "type": "section_content",  # ← 기본값
#     "display_name": "MARKET_RISK 섹션",  # ← 자동 생성
#     "description": "MARKET_RISK에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)",
#     "examples": ["MARKET_RISK에 해당하는 예시를 제공하세요."],
#     "required": true,
#     "order_hint": 2
#   },
#   {
#     "key": "{{COMPETITOR_ANALYSIS}}",
#     "type": "section_content",  # ← 기본값
#     "display_name": "COMPETITOR_ANALYSIS 섹션",
#     "description": "COMPETITOR_ANALYSIS에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)",
#     "examples": ["COMPETITOR_ANALYSIS에 해당하는 예시를 제공하세요."],
#     "required": true,
#     "order_hint": 2
#   }
# ]
```

### 예시 3: 혼합

```python
placeholders = [
    type('Placeholder', (), {'placeholder_key': '{{TITLE}}'})(),
    type('Placeholder', (), {'placeholder_key': '{{RISK_ANALYSIS}}'})(),
    type('Placeholder', (), {'placeholder_key': '{{PUBLISH_DATE}}'})(),
]

meta_info = create_meta_info_from_placeholders(placeholders)

# 결과
# [
#   {
#     "key": "{{TITLE}}",
#     "type": "section_title",
#     "display_name": "보고서 제목",
#     ...
#     "required": true,
#     "order_hint": 1
#   },
#   {
#     "key": "{{RISK_ANALYSIS}}",
#     "type": "section_content",  # ← 기본값 ("RISK"는 키워드 아님)
#     "display_name": "RISK_ANALYSIS 섹션",
#     ...
#     "required": true,
#     "order_hint": 2
#   },
#   {
#     "key": "{{PUBLISH_DATE}}",
#     "type": "metadata",  # ← "DATE" 포함 → metadata
#     "display_name": "작성 날짜",
#     ...
#     "required": false,  # ← metadata는 required=false
#     "order_hint": 0
#   }
# ]
```

---

## 주요 메서드 설명

### 1️⃣ `create_meta_info_from_placeholders(placeholders)`

**목적:** 메인 함수. Placeholder 리스트를 메타정보 JSON으로 변환

**입력:**
```python
placeholders: List[Placeholder]
# 예:
# [
#   Placeholder(placeholder_key="{{TITLE}}"),
#   Placeholder(placeholder_key="{{CUSTOM}}")
# ]
```

**출력:**
```python
List[Dict[str, Any]]
# 예:
# [
#   {"key": "{{TITLE}}", "type": "section_title", ...},
#   {"key": "{{CUSTOM}}", "type": "section_content", ...}
# ]
```

**동작:**
```
1. 각 placeholder에서 key_name 추출
2. 키워드 분류 수행
3. 3개의 헬퍼 함수 호출:
   - _get_display_name()
   - _get_description()
   - _get_examples()
4. 메타정보 아이템 조합
5. 배열에 추가
6. 모든 placeholder 처리 후 반환
```

---

### 2️⃣ `_get_display_name(key_name, ph_type)`

**목적:** 한글 display_name 생성

**로직:**
```python
display_names = {
    "TITLE": "보고서 제목",
    "SUMMARY": "요약",
    "BACKGROUND": "배경",
    "CONCLUSION": "결론",
    "DATE": "작성 날짜",
    "MAIN_CONTENT": "주요 내용",
    "RISK": "위험 요소",
}

# 사전에 있으면 → 사전값 반환
# 사전에 없으면 → f"{key_name} 섹션" 생성
```

**예시:**
```python
_get_display_name("TITLE", "section_title")           # "보고서 제목"
_get_display_name("RISK_ANALYSIS", "section_content")  # "RISK_ANALYSIS 섹션"
_get_display_name("CUSTOM", "section_content")         # "CUSTOM 섹션"
```

---

### 3️⃣ `_get_description(key_name, classification)`

**목적:** 상세 설명 자동 생성

**로직:**
```python
descriptions = {
    "TITLE": "보고서의 명확하고 간결한 제목을 작성하세요...",
    "SUMMARY": "2-3문단으로 보고서의 핵심 내용을 요약합니다...",
    ...
}

# 사전에 있으면 → 사전값 반환
# 사전에 없으면 → 기본 설명 + "이 키의 이름이 모호하여..." 주석 추가
```

**예시:**
```python
_get_description("TITLE", {...})
# "보고서의 명확하고 간결한 제목을 작성하세요. 주요 주제를 한 문장으로 표현해야 합니다."

_get_description("RISK_ANALYSIS", {...})
# "RISK_ANALYSIS에 해당하는 내용을 작성해주세요. (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)"
```

---

### 4️⃣ `_get_examples(key_name, classification)`

**목적:** 예시 문장 자동 생성

**로직:**
```python
examples = {
    "TITLE": ["2025 디지털뱅킹 트렌드 분석", "모바일 뱅킹 고도화 방안"],
    "SUMMARY": ["최근 디지털 채널 이용률이 75%를 초과..."],
    ...
}

# 사전에 있으면 → 사전값 반환 (List[str])
# 사전에 없으면 → [f"{key_name}에 해당하는 예시를 제공하세요."]
```

**예시:**
```python
_get_examples("TITLE", {...})
# ["2025 디지털뱅킹 트렌드 분석", "모바일 뱅킹 고도화 방안"]

_get_examples("RISK_ANALYSIS", {...})
# ["RISK_ANALYSIS에 해당하는 예시를 제공하세요."]
```

---

## 핵심 안전 메커니즘

### ✅ 안전장치 1: 키워드 "포함" 검사 (부분 매칭)

```python
# ❌ 정확한 일치만 하면 불안전
if key_name == "SUMMARY":  # {{EXEC_SUMMARY}}를 놓칠 수 있음

# ✅ "포함"으로 검사하면 안전
if "SUMMARY" in key_name:  # {{EXEC_SUMMARY}} → 포함됨 ✅
```

### ✅ 안전장치 2: 기본값 제공

```python
# 모든 키워드가 일치하지 않으면
if not classification:
    classification = {"type": "section_content", "section": "내용"}
    # → 기본값으로 안전하게 처리
```

### ✅ 안전장치 3: Display Name 자동 생성

```python
# 사전에 없으면
return display_names.get(key_name, f"{key_name} 섹션")
#                      ↑ key_name이 없으면 ↑
#                      자동으로 "{key_name} 섹션" 생성
```

### ✅ 안전장치 4: 설명에 주석 추가

```python
# 애매한 경우 사용자에게 알림
if key_name not in descriptions:
    desc += " (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)"
    # → 사용자는 "아, 이건 자동 추론이구나" 알 수 있음
```

### ✅ 안전장치 5: Required 필드 자동 판단

```python
# metadata가 아니면 필수
"required": classification["type"] != "metadata"
# → 날짜/메타데이터는 선택, 나머지는 필수
```

---

## 요약

### 언제 기본값을 사용하는가?

```
✅ 기본값 사용 조건:
1. Placeholder에 TITLE, SUMMARY, BACKGROUND, CONCLUSION, DATE 중
   어느것도 포함되지 않을 때
2. 예: {{RISK}}, {{MARKET_ANALYSIS}}, {{ANYTHING}}

❌ 기본값을 사용하지 않는 경우:
1. 위의 키워드 중 하나라도 포함될 때
2. 예: {{RISK_BACKGROUND}} → "BACKGROUND" 포함 → 배경 섹션
```

### 안전성

```
✅ 예측 불가능한 Placeholder도 안전하게 처리
   → 기본값 제공
   → Display name 자동 생성
   → 설명에 주석 추가
   → required 필드 자동 판단

✅ 사용자는 항상 유효한 메타정보를 받음
   (완벽하지는 않을 수 있지만, 안전함)
```

---

## 추가 질문?

더 알고 싶은 부분이 있으면 언제든지 질문하세요!
- 특정 시나리오의 동작 방식
- 코드 구현 방식
- 예시 추가
