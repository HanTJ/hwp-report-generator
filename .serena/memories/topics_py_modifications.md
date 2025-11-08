# topics.py /ask 함수 수정 계획

## 수정 위치
라인 712-718의 시스템 프롬프트 로직

## 기존 코드
```python
    # 시스템 프롬프트 구성 (순수 지침만)
    if body.system_prompt:
        system_prompt = body.system_prompt
        logger.info(f"[ASK] Using custom system prompt - length={len(system_prompt)}")
    else:
        system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
        logger.info(f"[ASK] Using default system prompt")
```

## 신규 코드
```python
    # 시스템 프롬프트 구성 (순서: custom > template_id > default)
    if body.system_prompt:
        system_prompt = body.system_prompt
        logger.info(f"[ASK] Using custom system prompt - length={len(system_prompt)}")
    elif body.template_id:
        # === Template 기반 동적 prompt 생성 ===
        logger.info(f"[ASK] Loading template for dynamic prompt - template_id={body.template_id}")
        
        template = TemplateDB.get_template_by_id(body.template_id, current_user.id)
        if not template:
            logger.warning(f"[ASK] Template not found - template_id={body.template_id}, user_id={current_user.id}")
            return error_response(
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                http_status=404,
                message="템플릿을 찾을 수 없습니다.",
                hint="템플릿 ID를 확인하거나 template_id 없이 요청해주세요."
            )
        
        logger.info(f"[ASK] Template found - template_id={template.id}, filename={template.filename}")
        
        # Placeholder 조회
        placeholders = PlaceholderDB.get_placeholders_by_template(template.id)
        logger.info(f"[ASK] Placeholders retrieved - count={len(placeholders) if placeholders else 0}")
        
        # 동적 prompt 생성
        if placeholders:
            system_prompt = create_dynamic_system_prompt(placeholders)
            logger.info(f"[ASK] Dynamic prompt created from template - template_id={template.id}, placeholders={len(placeholders)}, prompt_length={len(system_prompt)}")
        else:
            system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
            logger.info(f"[ASK] Using default prompt (template has no placeholders) - template_id={template.id}")
    else:
        system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT
        logger.info(f"[ASK] Using default system prompt")
```

## 필요한 import (이미 추가됨)
- TemplateDB, PlaceholderDB
- create_dynamic_system_prompt

## 필요한 에러 코드 (아직 추가 필요)
- ErrorCode.TEMPLATE_NOT_FOUND
