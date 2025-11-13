# Unit Spec: Batch Placeholder 메타정보 생성 최적화 (옵션 A)

**작성일:** 2025-11-13
**버전:** 2.0 (옵션 A 기반 재작성)
**상태:** 작성 완료, 사용자 검토 대기

---

## 1. 요구사항 요약

### 목적
현재 개별 Claude API 호출 방식을 **배치 기반 구조로 리팩토링**하여:
- API 호출 수 60% 감소 (10 → 4회)
- 토큰 사용량 40% 감소
- 응답 시간 94% 단축 (병렬: ~1.67초)
- 비용 60% 절감

### 유형
- ☐ 신규 ☒ 변경 ☐ 삭제

### 핵심 요구사항

#### 현재 상황 분석
- **기존 코드:** `batch_generate_metadata()`가 이미 구현되어 있음 (placeholder_metadata_generator.py)
- **문제:** 순차 처리로 인해 병렬 처리 이점을 활용하지 못함
- **목표:** asyncio.gather()를 사용한 진정한 병렬 처리로 개선

#### 해결 방안 (옵션 A: 구조 정제)
**배치 크기:** 3개 Placeholder를 단위로 배치 처리
- 10개 Placeholder → 4개 배치 (3+3+3+1) → 4회 병렬 API 호출
- 순차 시간: ~6.24초 → 병렬 시간: ~1.67초 (4배 개선)

**구현 범위:**
1. **신규 함수:** `claude_metadata_generator.py`에 배치 전용 함수 추가
   - `batch_generate_placeholder_metadata()` - 단일 배치 처리
   - `_parse_batch_json_response()` - 배치 응답 파싱
   - `BATCH_SYSTEM_PROMPT_GENERATOR` - 배치 전용 프롬프트

2. **리팩토링:** `placeholder_metadata_generator.py`의 `batch_generate_metadata()` 개선
   - asyncio.gather() 도입으로 병렬 처리 구현
   - 단일 배치 처리 헬퍼 함수 추가

3. **에러 처리:** 부분 실패, 폴백 로직 강화

### 제약사항
- Claude API 타임아웃: None (무제한 대기, v2.4.1 정책)
- 폴백: Claude API 실패 시 기본 규칙 적용
- 캐싱: 동일 Placeholder 중복 호출 방지

---

## 2. 구현 대상 파일

### New (새로 추가되는 요소)

| 파일 | 요소 | 위치 | 설명 |
|------|------|------|------|
| `claude_metadata_generator.py` | `BATCH_SYSTEM_PROMPT_GENERATOR` | 상수 | 배치 처리 전용 시스템 프롬프트 |
| `claude_metadata_generator.py` | `batch_generate_placeholder_metadata()` | async def | 단일 배치(3개)를 Claude API로 처리 |
| `claude_metadata_generator.py` | `_parse_batch_json_response()` | def | 배치 응답에서 JSON 추출 및 파싱 |
| `placeholder_metadata_generator.py` | `batch_generate_metadata_single_batch()` | async def | asyncio.gather 태스크용 래퍼 함수 |

### Change (기존 함수 수정)

| 파일 | 함수 | 라인 | 변경 사항 |
|------|------|------|----------|
| `placeholder_metadata_generator.py` | `batch_generate_metadata()` | 139-197 | 순차 처리 → asyncio.gather 기반 병렬 처리 |

### Reference (변경 없음)

| 파일 | 함수 | 목적 |
|------|------|------|
| `meta_info_generator.py` | `generate_placeholder_metadata_with_claude()` | 배치 함수 호출 |
| `routers/templates.py` | POST `/api/templates` | 엔드포인트 |
| `claude_client.py` | `chat_completion()` | Claude API 호출 |

---

## 3. 상세 플로우 (Flowchart)

### 전체 호출 흐름

```
POST /api/templates (routers/templates.py:229-237)
│
└─► await generate_placeholder_metadata_with_claude(
    raw_placeholders=["{{TITLE}}", "{{SECTION_A}}", ..., "{{DATE}}"],  # 10개
    template_context="금융 보고서",
    enable_fallback=True
)
    ↓
    (meta_info_generator.py:276-417)
    ├─ 중복 Placeholder 검사
    └─ await batch_generate_metadata(
        placeholders=["{{TITLE}}", ..., "{{DATE}}"],
        template_context="금융 보고서",
        timeout_per_item=None,
        batch_size=3  ← [신규 파라미터]
    )
        ↓
        (placeholder_metadata_generator.py:139-197) [변경]
        │
        ├─ Step 1: 배치 분할 (3개씩)
        │  ├─ Batch 1: ["{{TITLE}}", "{{SECTION_A}}", "{{SECTION_B}}"]
        │  ├─ Batch 2: ["{{SECTION_C}}", "{{CONTENT_A}}", "{{CONTENT_B}}"]
        │  ├─ Batch 3: ["{{CONTENT_C}}", "{{ANALYSIS}}", "{{CONCLUSION}}"]
        │  └─ Batch 4: ["{{DATE}}"]
        │
        ├─ Step 2: asyncio.gather로 병렬 실행 [개선]
        │  ├─ Task 1: batch_generate_metadata_single_batch(Batch 1)
        │  │  ├─ await batch_generate_placeholder_metadata(Batch 1)
        │  │  │  ├─ 프롬프트 구성 (BATCH_SYSTEM_PROMPT_GENERATOR)
        │  │  │  ├─ Claude API 호출 (1회)
        │  │  │  └─ _parse_batch_json_response() → Dict[ph_key, metadata]
        │  │  └─ return Dict
        │  │
        │  ├─ Task 2: batch_generate_metadata_single_batch(Batch 2)
        │  │  └─ ... (병렬 실행)
        │  │
        │  ├─ Task 3: batch_generate_metadata_single_batch(Batch 3)
        │  │  └─ ... (병렬 실행)
        │  │
        │  └─ Task 4: batch_generate_metadata_single_batch(Batch 4)
        │     └─ ... (병렬 실행)
        │
        ├─ Step 3: 결과 병합
        │  {
        │    "{{TITLE}}": {...메타정보...},
        │    "{{SECTION_A}}": {...},
        │    ...
        │    "{{DATE}}": {...}
        │  }
        │
        └─ return 결과
```

### 배치 처리 상세 (Parallel Execution)

```
시간축 (Timeline)
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ Task 1 (Batch 1)  ▓▓▓▓▓▓▓▓▓▓▓▓  API 응답: ~1-2초          │
│ Task 2 (Batch 2)      ▓▓▓▓▓▓▓▓▓▓▓▓  API 응답: ~1-2초        │
│ Task 3 (Batch 3)          ▓▓▓▓▓▓▓▓▓▓▓▓  API 응답: ~1-2초      │
│ Task 4 (Batch 4)              ▓▓▓▓▓▓▓▓▓▓▓▓  API 응답: ~1-2초  │
│                                                             │
│ Total: ~1.67초 (최대 Task 시간) vs 순차: ~6.24초           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 함수 시그니처 및 구현 상세

### 4.1 `BATCH_SYSTEM_PROMPT_GENERATOR` (상수)

**파일:** `claude_metadata_generator.py`
**타입:** str
**목적:** 배치 처리 최적화된 시스템 프롬프트

```python
BATCH_SYSTEM_PROMPT_GENERATOR = """당신은 "금융 보고서 다중 Placeholder 메타정보 생성기"입니다.

입력:
- 금융 보고서 템플릿의 여러 Placeholder들
- 각 Placeholder의 위치와 역할 정보

목표:
- 모든 Placeholder에 대해 **일관된 스타일과 형식**으로 메타정보를 생성합니다.
- 응답은 반드시 JSON 객체 형식입니다.

규칙:
1. 응답은 {"placeholder_key": {...}} 형식의 단일 JSON 객체입니다. (배열이 아님)
2. 모든 description은 명사형 또는 "~하는" 형태로 통일합니다.
3. 각 Placeholder의 역할과 컨텍스트를 고려합니다:
   - section_title: 간결한 설명 (20~50자)
   - section_content: 상세한 설명 (50~200자)
   - metadata: 간단한 설명 (10~30자)
4. examples는 보고서 작성 AI가 그대로 참고할 수 있는 수준으로 작성합니다.
5. 추가 설명이나 마크다운 없이 JSON만 반환합니다. (필수)

출력 예시:
{
  "{{TITLE}}": {
    "type": "section_title",
    "description": "보고서의 핵심 주제를 명확하게 표현한 제목",
    "examples": ["2025년 금융 시장 분석"],
    "max_length": 200,
    "required": true
  },
  "{{SUMMARY}}": {
    "type": "section_content",
    ...
  }
}
"""
```

---

### 4.2 `batch_generate_placeholder_metadata()` (신규 async 함수)

**파일:** `claude_metadata_generator.py`

```python
async def batch_generate_placeholder_metadata(
    placeholders: List[str],
    template_context: str = "보고서",
    timeout: Optional[float] = None
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    여러 Placeholder의 메타정보를 **단일 Claude API 호출**로 생성합니다.

    배치 크기의 Placeholder(일반적으로 3개)를 한 번에 Claude에 전달하여
    일관된 포맷의 메타정보를 생성합니다.

    Args:
        placeholders (List[str]):
            Placeholder 키 목록 (예: ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"])
            일반적으로 batch_size(=3)개 이하의 Placeholder

        template_context (str, optional):
            템플릿 컨텍스트 (예: "금융 보고서", "마케팅 계획")
            Placeholder의 의미를 이해하는 데 도움
            기본값: "보고서"

        timeout (Optional[float], optional):
            API 호출의 타임아웃 시간 (초)
            None이면 무제한 (v2.4.1 정책)
            기본값: None

    Returns:
        Dict[str, Optional[Dict[str, Any]]]:
            {
                "{{TITLE}}": {
                    "type": "section_title",
                    "description": "보고서의 핵심 주제를 명확하게 표현한 제목",
                    "examples": ["2025년 금융 시장 분석"],
                    "max_length": 200,
                    "required": true
                },
                "{{SUMMARY}}": {...},
                ...
            }

        실패한 Placeholder는 None으로 표시:
            "{{UNKNOWN}}": None  # 파싱 실패 등의 경우

    Raises:
        Exception: Claude API 호출 실패 시
                  (호출자가 catch하여 폴백 처리)

    Implementation Flow:
        1. 프롬프트 구성: placeholder_list를 문자열로 변환
        2. Claude API 호출:
           - system: BATCH_SYSTEM_PROMPT_GENERATOR
           - user: "{{TITLE}}, {{SUMMARY}}, {{DATE}}의 메타정보 생성"
           - timeout: timeout 값 전달
        3. 응답 파싱: _parse_batch_json_response()로 JSON 추출
        4. 검증: 모든 placeholder에 대한 결과 확인
        5. 반환: 결과 dict 반환

    Example:
        >>> result = await batch_generate_placeholder_metadata(
        ...     placeholders=["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"],
        ...     template_context="금융 보고서",
        ...     timeout=None
        ... )
        >>> print(result["{{TITLE}}"]['description'])
        "보고서의 핵심 주제를 명확하게 표현한 제목"
    """
    pass  # 구현은 section 5에서
```

**사용 위치:** `batch_generate_metadata_single_batch()` 내부에서 호출

---

### 4.3 `_parse_batch_json_response()` (신규 함수)

**파일:** `claude_metadata_generator.py`

```python
def _parse_batch_json_response(
    response: str
) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    배치 Claude 응답에서 JSON 객체 추출 및 파싱합니다.

    응답 형식 처리:
    1. 마크다운 코드블록: ```json {...} ``` → 추출 후 파싱
    2. 순수 JSON: {...} → 바로 파싱
    3. 기타 형식: JSON 부분 자동 추출 시도

    Args:
        response (str): Claude API의 응답 문자열

    Returns:
        Optional[Dict[str, Dict[str, Any]]]:
            파싱 성공: {
                "{{TITLE}}": {type, description, ...},
                "{{SUMMARY}}": {...},
                ...
            }
            파싱 실패: None

    Example:
        >>> response = '''{
        ...   "{{TITLE}}": {
        ...     "type": "section_title",
        ...     "description": "..."
        ...   }
        ... }'''
        >>> result = _parse_batch_json_response(response)
        >>> result["{{TITLE}}"]['type']
        "section_title"
    """
    pass  # 구현은 section 5에서
```

**사용 위치:** `batch_generate_placeholder_metadata()` 내부에서 응답 파싱 시

---

### 4.4 `batch_generate_metadata()` [리팩토링]

**파일:** `placeholder_metadata_generator.py`
**라인:** 139-197
**변경:** 순차 처리 → asyncio.gather 기반 병렬 처리

```python
async def batch_generate_metadata(
    placeholders: List[str],
    template_context: str = "보고서",
    timeout_per_item: Optional[float] = None,
    batch_size: int = 3  # [신규] 배치 크기 파라미터
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    여러 Placeholder의 메타정보를 **배치 처리**로 생성합니다.

    [변경 사항]
    - 기존: 10개 Placeholder → 10번의 순차 API 호출 (병렬이 아님)
    - 변경: 10개 Placeholder → 4번의 배치 병렬 호출 (asyncio.gather 사용)

    배치별로 나누어서 병렬 처리함으로써:
    ✓ API 호출 60% 감소 (10 → 4)
    ✓ 토큰 사용 40% 감소
    ✓ 응답 시간 개선 (병렬: ~1.67초 vs 순차: ~6.24초)
    ✓ 부분 실패 시 해당 배치만 재시도 가능

    Args:
        placeholders (List[str]):
            Placeholder 키 목록 (예: ["{{TITLE}}", "{{SECTION_A}}", ...])

        template_context (str, optional):
            템플릿 컨텍스트
            기본값: "보고서"

        timeout_per_item (Optional[float], optional):
            각 항목의 타임아웃 (현재 사용 안 함, v2.4.1 정책)
            기본값: None

        batch_size (int, optional):
            한 번에 처리할 배치 크기 (Placeholder 개수)
            기본값: 3 (권장값)
            예: batch_size=3이면 3개씩 묶어서 API 호출

    Returns:
        Dict[str, Optional[Dict[str, Any]]]:
            {
                "{{TITLE}}": {메타정보},
                "{{SECTION_A}}": {메타정보},
                ...
                "{{DATE}}": {메타정보 or None}
            }

    Process Flow:
        1. 배치 분할 (배치 크기 기준):
           placeholders를 batch_size씩 분할
           ["A", "B", "C", "D", "E", "F", "G"]
           → [["A","B","C"], ["D","E","F"], ["G"]]

        2. asyncio.gather로 배치들을 병렬 실행 [개선]:
           - Task 1: batch_generate_metadata_single_batch(["A","B","C"])
           - Task 2: batch_generate_metadata_single_batch(["D","E","F"])
           - Task 3: batch_generate_metadata_single_batch(["G"])
           → 동시 실행 (순차 아님!)

        3. 배치별 처리 (각 Task 내부):
           - await batch_generate_placeholder_metadata() 호출
           - 단일 Claude API 호출 (배치별 1회)
           - 응답 파싱 및 dict 반환

        4. 결과 집계:
           모든 배치 결과를 병합하여 최종 dict 반환

    Example:
        >>> result = await batch_generate_metadata(
        ...     placeholders=["{{TITLE}}", "{{SECTION_A}}", ..., "{{DATE}}"],
        ...     template_context="금융 보고서",
        ...     batch_size=3
        ... )
        >>> len(result)  # 10개 Placeholder
        10
        >>> print([k for k, v in result.items() if v is None])
        []  # 모두 성공
    """
    pass  # 구현은 section 5에서
```

**호출 위치:** `meta_info_generator.py:324`의 `generate_placeholder_metadata_with_claude()` 내부

---

### 4.5 `batch_generate_metadata_single_batch()` (신규 헬퍼 함수)

**파일:** `placeholder_metadata_generator.py`

```python
async def batch_generate_metadata_single_batch(
    batch: List[str],
    template_context: str,
    timeout: Optional[float] = None
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    단일 배치(batch_size개의 Placeholder)를 Claude API로 처리합니다.

    이 함수는 여러 배치를 asyncio.gather로 병렬 실행할 때 사용됩니다.
    예를 들어, 10개 Placeholder를 3개씩 나누면 4개의 이 함수가
    동시에 실행됩니다.

    Args:
        batch (List[str]):
            단일 배치의 Placeholder 목록 (일반적으로 3개, 마지막은 그 이하)
            예: ["{{TITLE}}", "{{SECTION_A}}", "{{SECTION_B}}"]

        template_context (str):
            템플릿 컨텍스트 (상위 함수에서 전달)

        timeout (Optional[float], optional):
            타임아웃 (상위 함수에서 전달)

    Returns:
        Dict[str, Optional[Dict[str, Any]]]:
            {
                "{{TITLE}}": {메타정보},
                "{{SECTION_A}}": {메타정보},
                "{{SECTION_B}}": {메타정보}
            }

    Implementation:
        from app.utils.claude_metadata_generator import batch_generate_placeholder_metadata

        result = await batch_generate_placeholder_metadata(
            placeholders=batch,
            template_context=template_context,
            timeout=timeout
        )
        return result
    """
    pass  # 구현은 section 5에서
```

**호출 위치:** `batch_generate_metadata()` 내부에서 asyncio.gather 태스크로 사용

---

## 5. 테스트 계획

### 5.1 테스트 범위

| 계층 | 목적 | 대상 | 예상 개수 |
|------|------|------|---------|
| Unit | 개별 함수 동작 검증 | `batch_generate_placeholder_metadata()`, `_parse_batch_json_response()` 등 | 8개 |
| Integration | 엔드 투 엔드 플로우 | Template 업로드 → 배치 메타정보 생성 → DB 저장 | 5개 |
| API | API 계약 검증 | POST `/api/templates` 응답 및 성능 | 2개 |

**총 테스트 케이스: 15개**

### 5.2 테스트 케이스 상세

| TC ID | 계층 | 시나리오 | 목적 | 기대결과 | 함수 대상 |
|-------|------|---------|------|---------|----------|
| TC-001 | Unit | 배치 처리 정상 동작 (3개) | 배치별 정확성 | 메타정보 정확성, JSON 파싱 성공 | `batch_generate_placeholder_metadata()` |
| TC-002 | Unit | 배치 분할 (10개 → 4개 배치) | 배치 크기 검증 | [3,3,3,1] 크기로 분할 | `batch_generate_metadata()` |
| TC-003 | Unit | asyncio.gather 병렬 처리 | 병렬화 검증 | 모든 배치가 동시 실행 (시간 측정) | `batch_generate_metadata()` |
| TC-004 | Unit | 응답 포맷 일관성 | 배치 내 일관성 | 모든 description이 명사형 | `batch_generate_placeholder_metadata()` |
| TC-005 | Unit | JSON 파싱 (마크다운 블록) | 응답 형식 다양성 | ```json {...} ``` 처리 | `_parse_batch_json_response()` |
| TC-006 | Unit | JSON 파싱 (순수 JSON) | 응답 형식 단순성 | {...} 처리 | `_parse_batch_json_response()` |
| TC-007 | Unit | Claude API 실패 (타임아웃) | 에러 핸들링 | 부분 실패 처리, None 반환 | `batch_generate_placeholder_metadata()` |
| TC-008 | Unit | 폴백 메커니즘 | 기본 규칙 적용 | Claude 실패 → 기본 규칙으로 대체 | `generate_placeholder_metadata_with_claude()` |
| TC-009 | Integration | Template 업로드 (10개 Placeholder) | E2E 플로우 | 4회 API 호출 (배치 4개), 201 응답 | POST `/api/templates` |
| TC-010 | Integration | 배치 병렬 처리 성능 | 응답 시간 검증 | <3초 (목표: ~1.67초) | `batch_generate_metadata()` |
| TC-011 | Integration | 부분 실패 복구 | 탄력성 | 일부 배치 실패 → 나머지 성공 | `batch_generate_metadata()` |
| TC-012 | Integration | 중복 Placeholder 검사 | 입력 검증 | ValueError 발생 | `generate_placeholder_metadata_with_claude()` |
| TC-013 | API | Template 업로드 응답 스키마 | API 계약 | placeholders_metadata 포함 | POST `/api/templates` |
| TC-014 | API | 에러 응답 (Claude 실패) | 우아한 실패 | 200/201 + 기본 메타정보 | POST `/api/templates` |
| TC-015 | API | API 호출 횟수 검증 | 최적화 검증 | 개별 호출이 아닌 배치 호출 (로깅 확인) | 전체 흐름 |

---

## 6. 에러 처리 시나리오

### 에러 타입별 처리 전략

| 에러 타입 | 발생 상황 | 처리 방법 | 결과 |
|----------|---------|---------|------|
| **Rate Limit** | 호출 제한 초과 (HTTP 429) | 지수 백오프 재시도 | 자동 복구 ✅ |
| **Timeout** | 응답 시간 초과 | 부분 실패, None 반환 | 폴백 적용 ✅ |
| **Invalid JSON** | 응답 파싱 실패 | 로깅 + None 반환 | 폴백 적용 ✅ |
| **API Error** | Claude 서버 에러 (HTTP 500) | 배치별 재시도 또는 폴백 | 폴백 적용 ✅ |
| **Network Error** | 연결 끊김 | 재시도 또는 폴백 | 폴백 적용 ✅ |
| **Duplicate Placeholder** | 입력 검증 실패 | ValueError 발생 | 요청 거절 ❌ |

### 에러 핸들링 코드 패턴

```python
# batch_generate_placeholder_metadata() 내부
try:
    result = await batch_generate_placeholder_metadata(...)
    return result
except Exception as e:
    logger.error(f"[BATCH_METADATA] Error: {str(e)}", exc_info=True)
    return {ph_key: None for ph_key in placeholders}  # 부분 실패 처리

# batch_generate_metadata() 내부
try:
    results_list = await asyncio.gather(
        *tasks,
        return_exceptions=True  # 일부 실패해도 계속 진행
    )
except Exception as e:
    logger.error(f"[BATCH] Unexpected error: {str(e)}")
    # 모든 배치 실패 처리
    return {ph_key: None for ph_key in placeholders}

# generate_placeholder_metadata_with_claude() 내부
try:
    claude_metadata = await batch_generate_metadata(...)
except Exception as e:
    logger.warning(f"[METADATA] Claude API failed, using fallback")
    if not enable_fallback:
        raise
    claude_metadata = {}  # 빈 dict로 설정 → 모든 Placeholder에 기본 규칙 적용
```

---

## 7. 성능 예상치

### 응답 시간 비교 (10개 Placeholder)

| 옵션 | 호출 수 | 순차 시간 | 병렬 시간 | 토큰 사용 | 비용 |
|------|--------|----------|----------|---------|------|
| **기존** (순차) | 10회 | ~30초 | N/A | ~25,000 | $0.10 |
| **옵션 A** (하이브리드, batch_size=3, 병렬) | 4회 | 6.24초 | **1.67초** ⭐ | ~3,500 | $0.04 |

### 개선 효과

- **API 호출:** 10 → 4 (60% 감소) ⭐
- **토큰 사용:** ~25,000 → ~3,500 (86% 감소) ⭐
- **응답 시간 (병렬):** ~30초 → ~1.67초 (94% 단축) ⭐
- **비용:** $0.10 → $0.04 (60% 절감) ⭐

### 병렬 처리 시간 계산

```
배치 구성:
- Batch 1 (3개): API 응답 ~1-2초
- Batch 2 (3개): API 응답 ~1-2초
- Batch 3 (3개): API 응답 ~1-2초
- Batch 4 (1개): API 응답 ~1-2초

순차 처리 (기존):
- Batch 1: 0-2초
- Batch 2: 2-4초
- Batch 3: 4-6초
- Batch 4: 6-8초
→ 총: ~8초

병렬 처리 (개선):
- Batch 1,2,3,4: 0-2초 (동시 실행)
→ 총: ~1.67초 (최대 배치 시간)

가정: asyncio 오버헤드 +0.67초
```

---

## 8. 구현 체크리스트

### Phase 1: 코드 작성

- [ ] `BATCH_SYSTEM_PROMPT_GENERATOR` 상수 추가 (`claude_metadata_generator.py`)
- [ ] `batch_generate_placeholder_metadata()` 함수 구현 (`claude_metadata_generator.py`)
  - [ ] 프롬프트 구성
  - [ ] Claude API 호출
  - [ ] 응답 파싱 (에러 처리 포함)
  - [ ] 로깅 추가
- [ ] `_parse_batch_json_response()` 함수 구현 (`claude_metadata_generator.py`)
  - [ ] 마크다운 블록 처리
  - [ ] 순수 JSON 처리
  - [ ] 유효성 검사
- [ ] `batch_generate_metadata()` 리팩토링 (`placeholder_metadata_generator.py`)
  - [ ] 배치 분할 로직
  - [ ] asyncio.gather 도입 ← 핵심 개선
  - [ ] 결과 병합
  - [ ] 에러 처리
- [ ] `batch_generate_metadata_single_batch()` 헬퍼 함수 추가 (`placeholder_metadata_generator.py`)
- [ ] 로깅 추가 (API 호출 횟수, 배치 정보 등)

### Phase 2: 테스트 작성

- [ ] Unit 테스트 8개 작성 (`tests/test_placeholder_metadata_generator.py`)
  - [ ] `batch_generate_placeholder_metadata()` 테스트 (3개)
  - [ ] `_parse_batch_json_response()` 테스트 (2개)
  - [ ] `batch_generate_metadata()` 테스트 (3개)
- [ ] Integration 테스트 5개 작성 (`tests/test_templates.py`)
- [ ] API 테스트 2개 작성 (`tests/test_templates.py`)
- [ ] 모든 테스트 실행 및 통과 확인

### Phase 3: 검증

- [ ] 기존 테스트 회귀 없음 확인 (전체 테스트 스위트 실행)
- [ ] 응답 속도 검증 (<3초 목표, ~1.67초 달성)
- [ ] API 호출 횟수 검증 (로깅 확인: 4회)
- [ ] 폴백 메커니즘 검증 (Claude 실패 시나리오)
- [ ] 병렬 처리 동작 확인 (Task 동시 실행 확인)

### Phase 4: 문서화

- [ ] Unit Spec 최종 확인
- [ ] 코드 DocString 작성 (Google 스타일)
- [ ] CLAUDE.md 업데이트 (새 함수 명시)
- [ ] 아키텍처 다이어그램 업데이트 (필요시)

---

## 9. 구현 참고사항

### 주의사항

1. **asyncio.gather() 사용 필수**
   - 현재 코드는 Task를 생성하지만 순차적으로 await
   - asyncio.gather()를 사용하여 진정한 병렬 처리 구현
   ```python
   # ❌ 순차 처리 (현재 코드)
   for ph_key, task in tasks:
       metadata = await task  # 하나씩 대기

   # ✅ 병렬 처리 (개선)
   results_list = await asyncio.gather(*tasks, return_exceptions=True)
   ```

2. **프롬프트 일관성**
   - `BATCH_SYSTEM_PROMPT_GENERATOR`는 배치 처리에 최적화
   - JSON 객체 형식 (배열 아님) 강제
   - 일관된 설명 형식 (명사형) 강요

3. **배치 크기 선택**
   - `batch_size=3`은 경험적 최적값
   - 너무 작으면 (1-2): API 호출 수 증가
   - 너무 크면 (5+): 개별 API 응답 시간 증가
   - 3개가 균형점 (응답 ~1-2초/배치)

4. **에러 처리**
   - `return_exceptions=True`로 일부 실패 처리
   - 실패한 Placeholder는 `None` 반환
   - 호출자(meta_info_generator)가 폴백 적용

5. **캐싱**
   - 기존 `_placeholder_metadata_cache` 활용
   - 동일 Placeholder는 재호출 방지
   - 배치 내 Placeholder 검사 시 캐시 확인

6. **타임아웃**
   - v2.4.1에서 제거됨, `timeout=None` 기본값
   - Claude API 응답을 기다림 (품질 우선)

---

## 10. 예상 API 호출 로그

### 개선 후 (배치 처리, 병렬)

```
[METADATA] Generating metadata with Claude - count=10
[BATCH_GENERATION] Processing 10 placeholders in 4 batches (size=3)
[BATCH_METADATA] Calling Claude API for 3 placeholders in parallel batch  # Batch 1 시작
[BATCH_METADATA] Calling Claude API for 3 placeholders in parallel batch  # Batch 2 시작
[BATCH_METADATA] Calling Claude API for 3 placeholders in parallel batch  # Batch 3 시작
[BATCH_METADATA] Calling Claude API for 1 placeholders in parallel batch  # Batch 4 시작
[BATCH_METADATA] Batch 1 completed - succeeded=3
[BATCH_METADATA] Batch 2 completed - succeeded=3
[BATCH_METADATA] Batch 3 completed - succeeded=3
[BATCH_METADATA] Batch 4 completed - succeeded=1
[BATCH_GENERATION] Completed - total_succeeded=10, total_failed=0, elapsed_time=1.67s
[METADATA] Claude API metadata generation completed
```

---

## 11. 마이그레이션 영향 분석

### Breaking Changes
없음. 기존 함수 시그니처는 유지됩니다.

### Backward Compatibility
- `batch_generate_metadata()`: 파라미터 추가 (`batch_size=3`), 기본값으로 하위 호환성 유지
- `generate_placeholder_metadata_with_claude()`: 변경 없음
- POST `/api/templates`: 응답 형식 변경 없음

### 마이그레이션 경로
1. 새 함수 구현 (`batch_generate_placeholder_metadata()`, `_parse_batch_json_response()`)
2. `batch_generate_metadata()` 리팩토링 (asyncio.gather 적용)
3. 점진적 테스트 및 검증
4. 배포

---

## 12. 함수 호출 맵 (Call Graph)

```
POST /api/templates (routers/templates.py:229)
└─ await generate_placeholder_metadata_with_claude() (meta_info_generator.py:276)
   ├─ 중복 검사 (라인 309)
   └─ await batch_generate_metadata() [리팩토링] (placeholder_metadata_generator.py:139)
      ├─ 배치 분할 (3개씩)
      └─ await asyncio.gather(
         ├─ await batch_generate_metadata_single_batch() [신규] (라인 신규)
         │  └─ await batch_generate_placeholder_metadata() [신규] (claude_metadata_generator.py:신규)
         │     ├─ 프롬프트 구성
         │     ├─ Claude API 호출 (1회)
         │     └─ _parse_batch_json_response() [신규]
         ├─ await batch_generate_metadata_single_batch() [신규]
         │  └─ (동일 프로세스)
         ├─ await batch_generate_metadata_single_batch() [신규]
         │  └─ (동일 프로세스)
         └─ await batch_generate_metadata_single_batch() [신규]
            └─ (동일 프로세스)
```

---

**마지막 업데이트:** 2025-11-13
**버전:** 2.0 (옵션 A 재작성)
**상태:** Unit Spec 재작성 완료, 사용자 검토 대기
