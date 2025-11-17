"""
Sequential Planning을 이용한 보고서 계획 생성 모듈

Template의 prompt_system을 활용하여 Claude Sequential Planning MCP를 사용하고
보고서의 구조화된 계획을 생성합니다.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any

import os
from shared.constants import ClaudeConfig
from app.database.template_db import TemplateDB
from app.utils.claude_client import ClaudeClient
from app.utils.prompt_filter import filter_guidance_prompt

logger = logging.getLogger(__name__)


class SequentialPlanningError(Exception):
    """Sequential Planning 실행 중 발생하는 예외"""
    pass


class TimeoutError(SequentialPlanningError):
    """Sequential Planning 응답시간 초과"""
    pass


async def sequential_planning(
    topic: str,
    template_id: Optional[int] = None,
    user_id: Optional[str] = None,
    is_web_search: bool = False
) -> Dict[str, Any]:
    """
    Sequential Planning을 이용한 보고서 계획 수립

    Template의 prompt_system을 가이드로 사용하여 보고서의 구조화된 계획을 생성합니다.

    Args:
        topic: 보고서 주제 (필수)
        template_id: 사용할 템플릿 ID (선택, None이면 default 사용)
        user_id: 사용자 ID (template_id 지정 시 권한 확인용)
        is_web_search: Claude 웹 검색 도구 활성화 여부

    Returns:
        {
            "plan": "# 보고서 계획\n## 개요\n...",
            "sections": [
                {
                    "title": "개요",
                    "description": "보고서의 전체 개요",
                    "order": 1
                },
                ...
            ]
        }

    Raises:
        SequentialPlanningError: 보고서 계획 생성 실패
        TimeoutError: 응답시간 초과 (> 2초)
        ValueError: 필수 파라미터 누락

    Constraints:
        - 응답시간: 반드시 2초 이내
    """
    start_time = time.time()

    # 1. 입력 검증
    if not topic or not isinstance(topic, str):
        raise ValueError("topic is required and must be a string")

    if len(topic) > 200:
        raise ValueError("topic must be less than 200 characters")

    logger.info(f"Sequential Planning started - topic={topic}, template_id={template_id}")

    try:
        # 2. Template의 prompt_system 로드
        guidance_prompt = await _get_guidance_prompt(template_id, user_id)

        # 3. Input prompt 구성
        input_prompt = _create_planning_prompt(topic, guidance_prompt)

        # 4. Claude API 호출 (Sequential Planning)
        plan_response = await _call_sequential_planning(
            input_prompt,
            is_web_search=is_web_search
        )

        # 5. 응답 파싱: plan 텍스트 + sections 배열 추출
        plan_dict = _parse_plan_response(plan_response)

        elapsed = time.time() - start_time
        logger.info(f"Sequential Planning completed - elapsed={elapsed:.2f}s, sections={len(plan_dict['sections'])}")

        # 6. 응답시간 검증 (< 2초)
        if elapsed > 20.0:
            logger.warning(f"Sequential Planning exceeded 5s constraint - elapsed={elapsed:.2f}s")
            raise TimeoutError(
                f"Sequential Planning took {elapsed:.2f}s, exceeding 5s constraint"
            )

        return plan_dict

    except TimeoutError:
        raise
    except Exception as e:
        logger.error(f"Sequential Planning failed - error={str(e)}", exc_info=True)
        raise SequentialPlanningError(f"Failed to generate plan: {str(e)}")


async def _get_guidance_prompt(
    template_id: Optional[int],
    user_id: Optional[str]
) -> str:
    """
    Template의 prompt_system을 가이드로 가져오기

    Args:
        template_id: 템플릿 ID (None이면 default)
        user_id: 사용자 ID (권한 확인용)

    Returns:
        가이드 프롬프트 문자열
    """
    # Default 가이드 (Template이 없을 때)
    default_guidance = """
**보고서 계획 작성 가이드:**
- 보고서는 다음 구조를 따라야 합니다:
  1. 요약: 보고서의 핵심 내용 요약
  2. 배경: 보고서의 배경과 필요성
  3. 주요 내용: 상세한 분석 및 설명 (3-5개 소제목 포함)
  4. 결론: 요약과 향후 조치사항
- 각 섹션은 명확하고 구조화된 내용을 포함해야 합니다.
- 전문적이고 객관적인 톤을 유지하세요.
"""

    if not template_id or not user_id:
        logger.info("No template_id provided, using default guidance")
        return default_guidance

    try:
        # Template 조회
        template = TemplateDB.get_template_by_id(template_id, user_id)

        if not template:
            logger.warning(
                f"Template not found - template_id={template_id}, using default guidance"
            )
            return default_guidance

        # Template의 prompt_system 추출 및 필터링
        if hasattr(template, 'prompt_system') and template.prompt_system:
            # 섹션별 상세 지침만 추출하여 토큰 효율 최적화
            filtered_prompt = filter_guidance_prompt(template.prompt_system)

            if filtered_prompt:
                logger.info(
                    f"Using filtered template prompt_system - template_id={template_id}, "
                    f"original_size={len(template.prompt_system)}, filtered_size={len(filtered_prompt)}"
                )
                return filtered_prompt
            else:
                # 필터링 결과가 없으면 원본 사용
                logger.info(
                    f"Section guidelines not found, using full prompt_system - "
                    f"template_id={template_id}"
                )
                return template.prompt_system

        logger.info(f"Template has no prompt_system, using default guidance - template_id={template_id}")
        return default_guidance

    except Exception as e:
        logger.warning(f"Error loading template - error={str(e)}, using default guidance")
        return default_guidance


def _create_planning_prompt(topic: str, guidance_prompt: str) -> str:
    """
    Sequential Planning용 입력 프롬프트 생성

    Args:
        topic: 보고서 주제
        guidance_prompt: Template의 가이드 프롬프트

    Returns:
        최종 입력 프롬프트
    """
    return f"""당신은 금융 보고서 작성의 전문가입니다.

사용자가 요청한 주제에 대해 체계적이고 구조화된 보고서 계획을 세워주세요.

**요청 주제:** {topic}

{guidance_prompt}

**계획 작성 지침:**
1. 보고서의 제목 결정
2. 각 섹션의 제목과 설명 작성
3. 각 섹션에서 다룰 주요 포인트 1개 추출

**반드시 다음 JSON 구조로만 응답하세요 (다른 텍스트 없이):**

{{
    "title": "보고서 제목",
    "sections": [
        {{
            "title": "섹션 제목",
            "description": "섹션 설명 (1문장)",
            "key_points": ["포인트1", "포인트2", "포인트3"],
            "order": 1
        }},
        {{
            "title": "섹션 제목",
            "description": "섹션 설명 (1문장)",
            "key_points": ["포인트1", "포인트2", "포인트3"],
            "order": 2
        }}
    ],
    "estimated_word_count": 5000,
    "estimated_sections_count": 5
}}

**중요:**
- JSON만 응답하세요. 마크다운, 설명, 주석은 절대 포함하지 마세요.
- 응답 전체는 유효한 JSON이어야 합니다.
- 응답은 반드시 2초 이내 생성 가능하도록 **과도하게 장문 금지**
- 불필요한 마크다운, 주석, 텍스트 출력 금지"""



def _extract_json_from_response(response_text: str) -> str:
    """
    Claude 응답에서 JSON 추출
    마크다운 코드블록(```json ... ```)에 감싸져 있을 수 있음

    Args:
        response_text: Claude API 원본 응답

    Returns:
        정제된 JSON 문자열
    """
    text = response_text.strip()

    # 마크다운 코드블록 패턴: ```json ... ``` 또는 ``` ... ```
    if text.startswith("```"):
        # 시작 마크다운 제거
        lines = text.split("\n")

        # 첫 줄에서 ``` 제거 (```json 또는 ```)
        start_idx = 0
        if lines[0].startswith("```"):
            start_idx = 1

        # 마지막 줄에서 ``` 제거
        end_idx = len(lines)
        if lines[-1].strip() == "```":
            end_idx = len(lines) - 1

        text = "\n".join(lines[start_idx:end_idx]).strip()

    return text


async def _call_sequential_planning(
    input_prompt: str,
    is_web_search: bool = False
) -> str:
    """
    Claude API를 호출하여 Sequential Planning 실행

    Args:
        input_prompt: 입력 프롬프트
        is_web_search: Claude 웹 검색 활성화 여부

    Returns:
        Claude API 응답 (JSON 문자열)

    Raises:
        SequentialPlanningError: API 호출 실패
    """
    try:
        logger.info(f"Calling Claude API for sequential planning - using fast model")

        # ClaudeClient 초기화 및 빠른 모델 사용
        claude = ClaudeClient()
        
        # 메시지 구성
        messages = [
            {
                "role": "user",
                "content": input_prompt
            }
        ]

        # 빠른 모델로 호출 (Haiku - 응답 속도 우선)
        plan_text, input_tokens, output_tokens = claude.chat_completion_fast(
            messages=messages,
            system_prompt="You are an expert in creating structured report plans. Respond only with valid JSON.",
            isWebSearch=is_web_search
        )

        logger.info(
            f"Claude API response received - "
            f"input_tokens={input_tokens}, "
            f"output_tokens={output_tokens}"
        )

        return plan_text

    except Exception as e:
        logger.error(f"Claude API call failed - error={str(e)}", exc_info=True)
        raise SequentialPlanningError(f"Claude API call failed: {str(e)}")


def _parse_plan_response(plan_text: str) -> Dict[str, Any]:
    """
    Claude 응답을 파싱하여 plan과 sections 추출

    Args:
        plan_text: Claude API 응답 텍스트 (JSON)

    Returns:
        {
            "plan": "마크다운 형식의 계획",
            "sections": [...]
        }

    Raises:
        SequentialPlanningError: JSON 파싱 실패
    """
    try:
        # 응답 텍스트 로깅 (디버깅용)
        logger.debug(f"Parsing plan response - length={len(plan_text)}, first_100_chars={plan_text[:100]}")

        # 응답 정제
        cleaned_text = _extract_json_from_response(plan_text)

        if not cleaned_text.strip():
            logger.error(f"Empty response after cleaning - original_length={len(plan_text)}")
            raise SequentialPlanningError("Received empty response from Claude API")

        # JSON 파싱
        plan_json = json.loads(cleaned_text)

        # Sections 추출
        sections = plan_json.get("sections", [])

        # 마크다운 형식의 plan 생성
        plan_md = _build_markdown_plan(plan_json)

        return {
            "plan": plan_md,
            "sections": sections
        }

    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to parse plan JSON - error={str(e)}, "
            f"response_preview={plan_text[:200] if plan_text else 'EMPTY'}"
        )
        raise SequentialPlanningError(f"Failed to parse plan response as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to parse plan response - error={str(e)}", exc_info=True)
        raise SequentialPlanningError(f"Failed to parse plan response: {str(e)}")


def _build_markdown_plan(plan_json: Dict[str, Any]) -> str:
    """
    JSON 계획을 마크다운 형식으로 변환

    Args:
        plan_json: Claude 응답 JSON

    Returns:
        마크다운 형식의 계획 텍스트
    """
    title = plan_json.get("title", "보고서 계획")
    sections = plan_json.get("sections", [])
    estimated_word_count = plan_json.get("estimated_word_count", 0)

    lines = [
        f"# {title}",
        "",
        f"**예상 분량:** {estimated_word_count}자",
        f"**예상 섹션 수:** {len(sections)}개",
        "",
    ]

    # 섹션별 계획 추가
    for section in sections:
        section_title = section.get("title", "무제")
        description = section.get("description", "")
        key_points = section.get("key_points", [])

        lines.append(f"## {section_title}")
        lines.append("")

        if description:
            lines.append(f"**설명:** {description}")
            lines.append("")

        if key_points:
            lines.append("**주요 포인트:**")
            for point in key_points:
                lines.append(f"- {point}")
            lines.append("")

    return "\n".join(lines)
