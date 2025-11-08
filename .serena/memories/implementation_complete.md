# ✅ 동적 Prompt 생성 기능 - 전체 구현 완료

## 📋 구현 완료 목록

### ✅ 1단계: prompts.py - 동적 Prompt 함수
- **파일**: `backend/app/utils/prompts.py`
- **상태**: 이미 구현됨 ✅
- **함수**: `create_dynamic_system_prompt(placeholders: List[Placeholder]) -> str`
- **기능**: Placeholder 기반으로 동적 system prompt 생성

### ✅ 2단계: models/topic.py - TopicMessageRequest 모델
- **파일**: `backend/app/models/topic.py`
- **상태**: 이미 구현됨 ✅
- **필드**: `template_id: Optional[int]`

### ✅ 3단계: models/message.py - AskRequest 모델 수정
- **파일**: `backend/app/models/message.py`
- **상태**: ✅ 수정 완료
- **변경**: 구문 오류 수정, template_id 필드 정리

### ✅ 4단계: routers/topics.py - /ask 엔드포인트 수정
- **파일**: `backend/app/routers/topics.py`
- **상태**: ✅ 수정 완료
- **변경사항**:
  1. Import 추가:
     - `from app.database.template_db import TemplateDB, PlaceholderDB`
     - `from app.utils.prompts import create_dynamic_system_prompt`
  2. 시스템 프롬프트 로직 (라인 712-718):
     - 기존: custom prompt 또는 default만 지원
     - 신규: custom > template_id > default 우선순위
  3. Template 권한 검증 추가 (ErrorCode.TEMPLATE_NOT_FOUND)
  4. Placeholder 조회 및 동적 prompt 생성 로직 추가

### ✅ 5단계: response_helper.py - 에러 코드
- **파일**: `backend/app/utils/response_helper.py`
- **상태**: 이미 구현됨 ✅
- **에러 코드**: TEMPLATE_NOT_FOUND, TEMPLATE_INVALID_FORMAT, TEMPLATE_DUPLICATE_PLACEHOLDER, TEMPLATE_UNAUTHORIZED

### ✅ 6단계: 테스트 코드
- **파일**: `backend/tests/test_dynamic_prompts.py`
- **상태**: ✅ 작성 완료
- **테스트 케이스**:
  - Unit: TC-UNIT-001~004 (Prompt 생성 로직)
  - API: TC-API-005~008 (/ask 엔드포인트)
  - Integration: TC-INTG-009~010

## 🔧 주요 수정사항 요약

### 1. AskRequest 모델 (message.py)
```python
# ❌ 이전 (구문 오류)
system_prompt: Optional[str] = Field(
template_id: Optional[int] = Field(...)
    default=None, ...

# ✅ 현재 (수정됨)
system_prompt: Optional[str] = Field(default=None, ...)
template_id: Optional[int] = Field(default=None, ...)
```

### 2. /ask 엔드포인트 (topics.py)
```python
# ✅ Template 기반 동적 prompt 생성 로직 추가
if body.system_prompt:
    system_prompt = body.system_prompt
elif body.template_id:  # ← NEW
    template = TemplateDB.get_template_by_id(body.template_id, current_user.id)
    if not template:
        return error_response(code=ErrorCode.TEMPLATE_NOT_FOUND, ...)
    
    placeholders = PlaceholderDB.get_placeholders_by_template(template.id)
    if placeholders:
        system_prompt = create_dynamic_system_prompt(placeholders)
    else:
        system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
else:
    system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
```

## 🔒 보안 고려사항

1. **Template 권한 검증**: `TemplateDB.get_template_by_id(template_id, user_id)` 사용
   - 다른 사용자의 template 접근 차단 ✅
2. **SQL Injection 방지**: Parameterized query 사용 (이미 적용됨) ✅
3. **Placeholder Injection 방지**: Regex 패턴 `{{[A-Z_]+}}` 형식만 허용 ✅

## 📈 성능 고려사항

1. **DB 쿼리 최적화**: Template + Placeholder 조회 ✅
2. **Prompt 생성 오버헤드**: 최대 20-30개 placeholder 무시 가능 수준 ✅
3. **Claude API 타임아웃**: 기존 120초 유지 ✅

## ✨ 하위 호환성

- `template_id`는 Optional 파라미터 ✅
- 기존 요청 (template_id 없음)은 기본 prompt 사용 ✅
- 기존 API 응답 구조 유지 ✅

## 🚀 동작 플로우

```
POST /api/topics/{topic_id}/ask with template_id
  ↓
1. Topic 권한 검증
  ↓
2. [NEW] Template 기반 prompt 생성 (template_id 있을 경우)
  ├─ Template 조회 (권한 검증)
  ├─ Placeholder 조회
  ├─ 동적 prompt 생성
  └─ 에러: TEMPLATE_NOT_FOUND (권한 없음)
  ↓
3. Claude API 호출 (동적 or 기본 prompt)
  ↓
4. 응답 저장 (MD, Artifact, Usage)
  ↓
5. 성공 응답 반환
```

## 📝 사용 예시

```bash
# 기본 요청 (하위 호환성)
POST /api/topics/1/ask
{
  "content": "보고서 작성해주세요"
}
→ 기본 prompt 사용

# Template 기반 요청 (신규)
POST /api/topics/1/ask
{
  "content": "보고서 작성해주세요",
  "template_id": 5
}
→ Template #5의 placeholder 기반 동적 prompt 생성

# Custom prompt 요청 (우선순위 최고)
POST /api/topics/1/ask
{
  "content": "보고서 작성해주세요",
  "system_prompt": "커스텀 프롬프트..."
}
→ 커스텀 prompt 사용
```

## 🧪 테스트 실행

```bash
cd backend
pytest tests/test_dynamic_prompts.py -v

# Unit 테스트
pytest tests/test_dynamic_prompts.py::TestCreateDynamicSystemPrompt -v

# API 테스트  
pytest tests/test_dynamic_prompts.py::TestAskEndpointWithTemplate -v
```

---

**완료 날짜**: 2025-11-07
**버전**: 1.0
**상태**: ✅ 완료 및 테스트 가능
