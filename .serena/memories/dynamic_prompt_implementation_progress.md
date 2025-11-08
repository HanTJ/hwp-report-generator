# 동적 System Prompt 생성 기능 구현 진행상황

## 완료된 항목
✅ 1. `backend/app/utils/prompts.py`
   - `create_dynamic_system_prompt()` 함수 추가 완료
   - Placeholder 기반 동적 prompt 생성 로직 구현

✅ 2. `backend/app/models/topic.py`
   - `TopicMessageRequest` 클래스 추가 완료
   - template_id, selected_artifact_ids 필드 포함

✅ 3. `backend/app/utils/response_helper.py`
   - Template 에러 코드 이미 존재함
   - TEMPLATE_NOT_FOUND, TEMPLATE_UNAUTHORIZED 등

✅ 4. `backend/app/models/message.py`
   - `AskRequest` 클래스에 template_id 필드 추가 완료

## 진행 중인 항목
🔄 5. `backend/app/routers/topics.py` - ask() 함수 수정 필요

### topics.py 수정 필요 사항:

**5.1 필요한 임포트 추가 (라인 24 근처):**
```python
from app.utils.prompts import FINANCIAL_REPORT_SYSTEM_PROMPT, create_topic_context_message, create_dynamic_system_prompt
from app.database.template_db import TemplateDB, PlaceholderDB
```

**5.2 ask() 함수의 시스템 프롬프트 생성 로직 수정 (라인 710-716 근처):**

기존 로직:
```python
# 시스템 프롬프트 구성 (순수 지침만)
if body.system_prompt:
    system_prompt = body.system_prompt
    logger.info(f"[ASK] Using custom system prompt - length={len(system_prompt)}")
else:
    system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
    logger.info(f"[ASK] Using default system prompt")
```

새로운 로직:
```python
# === NEW: Template 기반 동적 system prompt 생성 ===
if body.template_id:
    logger.info(f"[ASK] Loading template - template_id={body.template_id}")
    template = TemplateDB.get_template_by_id(body.template_id)
    
    if not template or template.user_id != current_user.id:
        logger.warning(f"[ASK] Template not found or unauthorized - template_id={body.template_id}")
        return error_response(
            code=ErrorCode.TEMPLATE_NOT_FOUND,
            http_status=404,
            message="템플릿을 찾을 수 없습니다.",
            hint="템플릿 ID를 확인하거나 template_id 없이 요청해주세요."
        )
    
    # Placeholder 조회
    placeholders = PlaceholderDB.get_placeholders_by_template(template.id)
    logger.info(f"[ASK] Loaded placeholders - template_id={template.id}, count={len(placeholders)}")
    
    # 동적 prompt 생성
    if placeholders:
        system_prompt = create_dynamic_system_prompt(placeholders)
        logger.info(f"[ASK] Dynamic system prompt created - placeholder_count={len(placeholders)}")
    else:
        system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
        logger.info(f"[ASK] No placeholders found, using default system prompt")

# 사용자 정의 prompt (template_id 없는 경우)
elif body.system_prompt:
    system_prompt = body.system_prompt
    logger.info(f"[ASK] Using custom system prompt - length={len(system_prompt)}")
else:
    system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
    logger.info(f"[ASK] Using default system prompt")
```

## 아직 구현 필요한 항목
❌ 테스트 코드 (tests/ 디렉토리)
   - TC-UNIT-001부터 TC-INTG-010까지 10개 테스트
   - Unit, Integration, API 테스트

## 추가 고려사항
- TemplateDB와 PlaceholderDB의 실제 메서드 명확히 확인 필요
- user_id 필드 존재 여부 확인 필요 (Template 테이블)
- 권한 검증 로직 (다른 사용자의 template 접근 방지)
