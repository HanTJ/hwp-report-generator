"""
Claude API를 활용한 Placeholder 메타정보 자동 생성

역할: Template의 Placeholder 목록을 Claude API로 분석하여
각 Placeholder의 메타정보(display_name, description, examples 등)를
동적으로 생성합니다.

참조: SystemPromptGenerate.md
"""

import json
import logging
from typing import Optional, Any
try:
    from typing import List, Dict
except ImportError:
    List = list
    Dict = dict

from app.utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)

# SystemPromptGenerate.md의 내용을 System Prompt로 사용
SYSTEM_PROMPT_GENERATOR = """당신은 "보고서 템플릿 스키마 설명 생성기"입니다.

입력:
- 사용자가 정의한 섹션 키 목록. 예: ["{{BACKGROUND}}", "{{CONCLUSION}}", "{{TITLE_SUMMARY}}", "{{DATE}}", "{{RISK}}"]

목표:
- 각 키가 어떤 역할을 하는지 추론하고, 보고서 작성 AI가 활용할 수 있도록
  구조화된 메타 정보를 JSON 형태로 반환합니다.

규칙:
1. 반드시 JSON 배열로만 응답합니다. 불필요한 문장은 쓰지 않습니다.
2. 각 항목은 다음 속성을 가집니다.
   - key: 문자열 (예: "{{BACKGROUND}}")
   - type: "section_content" | "section_title" | "metadata" 중 하나
   - display_name: 사람에게 보여줄 때 쓸 깔끔한 한글 이름
   - description: 이 섹션에 어떤 내용을 작성해야 하는지에 대한 상세 설명 (한국어, 2~4문장)
   - examples: 이 섹션에 들어갈 예시 문장 1~2개
   - required: true/false (일반적인 보고서 기준 필수인지)
   - order_hint: 숫자 (일반적인 보고서 작성 순서 기준 추천 위치)
3. 키 이름에서 다음을 추론합니다.
   - "TITLE"이 포함되면 기본적으로 제목 혹은 헤더 관련 → "section_title"
   - "SUMMARY" 또는 "SUMARY"가 포함되면 요약 섹션
   - "BACKGROUND"가 포함되면 배경/문제 인식 섹션
   - "CONCLUSION"이 포함되면 결론/제언 섹션
   - "DATE"는 날짜 메타데이터 → "metadata"
   - 그 외는 이름을 기반으로 의미를 합리적으로 추론합니다.
4. 애매한 경우:
   - description에 "이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다."를 덧붙입니다.
5. description은 보고서 작성 AI가 그대로 참고해도 될 정도로 구체적으로 작성합니다.
6. examples는 해당 섹션에 들어갈 문장 예를 실제처럼 작성합니다.

출력 형식 예시:
[
{
"key": "{{BACKGROUND}}",
"type": "section_content",
"display_name": "보고 배경",
"description": "해당 보고서를 작성하게 된 배경, 현황, 문제의식, 관련 정책 또는 사업 환경을 설명합니다. 독자가 이후 내용을 이해하는 데 필요한 최소한의 맥락을 제공합니다.",
"examples": [
"최근 디지털 채널 이용 비중이 75%를 초과함에 따라 모바일 채널 고도화 필요성이 대두되었습니다."
],
"required": true,
"order_hint": 2
}
]"""


def generate_placeholder_metadata(
    placeholders: List[str],
) -> Optional[List[Dict[str, Any]]]:
    """
    Claude API를 호출하여 Placeholder 메타정보 생성.

    Args:
        placeholders: Placeholder 키 목록 (예: ["{{TITLE}}", "{{SUMMARY}}"])

    Returns:
        메타정보 JSON 배열, 실패 시 None
        각 항목 구조:
        {
            "key": "{{TITLE}}",
            "type": "section_title",
            "display_name": "제목",
            "description": "...",
            "examples": [...],
            "required": true,
            "order_hint": 1
        }

    Raises:
        None - 모든 예외는 로깅되고 None 반환
    """
    if not placeholders:
        logger.info("[METADATA_GEN] No placeholders provided, returning None")
        return None

    try:
        # Step 1: 메타정보 생성용 프롬프트 구성
        placeholder_str = ", ".join(placeholders)
        user_prompt = f"""다음 Placeholder 목록에 대한 메타정보를 JSON 배열로 생성해주세요:

[{placeholder_str}]

반드시 JSON 배열로만 응답하세요. 다른 설명 없이 JSON만 반환하세요."""

        logger.info(
            f"[METADATA_GEN] Calling Claude API - placeholders={len(placeholders)}"
        )
        logger.debug(f"[METADATA_GEN] Placeholder list: {placeholders}")

        # Step 2: Claude API 호출
        claude = ClaudeClient()
        response_tuple = claude.chat_completion(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=SYSTEM_PROMPT_GENERATOR,
        )

        # chat_completion()은 tuple을 반환: (content, input_tokens, output_tokens)
        response = response_tuple[0]  # 첫 번째 요소: 응답 텍스트

        logger.info(f"[METADATA_GEN] Claude response received - length={len(response)}")
        logger.debug(f"[METADATA_GEN] Response preview: {response[:200]}...")

        # Step 3: JSON 파싱
        metadata = _parse_json_response(response)

        if metadata is None:
            logger.warning("[METADATA_GEN] Failed to parse Claude response as JSON")
            return None

        if not isinstance(metadata, list):
            logger.warning("[METADATA_GEN] Parsed response is not a list")
            return None

        logger.info(
            f"[METADATA_GEN] Metadata generated successfully - count={len(metadata)}"
        )
        return metadata

    except Exception as e:
        logger.error(f"[METADATA_GEN] Error generating metadata: {str(e)}", exc_info=True)
        return None


# 배치 처리 전용 시스템 프롬프트
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
    "description": "2-3문단으로 보고서의 핵심 내용을 요약",
    "examples": ["최근 시장 동향을 분석한 결과..."],
    "max_length": 1000,
    "required": true
  }
}
"""


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
        placeholders: Placeholder 키 목록 (예: ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"])
        template_context: 템플릿 컨텍스트 (기본값: "보고서")
        timeout: API 호출의 타임아웃 시간 (None이면 무제한)

    Returns:
        Dict[str, Optional[Dict[str, Any]]]:
            {"{{TITLE}}": {메타정보}, "{{SUMMARY}}": {...}, ...}
            실패한 Placeholder는 None으로 표시

    Raises:
        Exception: Claude API 호출 실패 시
    """
    if not placeholders:
        logger.warning("[BATCH_METADATA] Empty placeholders list")
        return {}

    try:
        # Step 1: 프롬프트 구성
        placeholder_str = ", ".join(placeholders)
        user_prompt = f"""다음 Placeholder들에 대한 메타정보를 JSON 객체 형식으로 생성해주세요:

{placeholder_str}

템플릿 컨텍스트: {template_context}

반드시 JSON 객체(배열이 아님)로만 응답하세요. 각 Placeholder를 키로 하는 메타정보를 작성해주세요."""

        logger.info(f"[BATCH_METADATA] Calling Claude API for {len(placeholders)} placeholders")

        # Step 2: Claude API 호출
        import asyncio
        client = ClaudeClient()

        response_tuple = await asyncio.to_thread(
            client.chat_completion,
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=BATCH_SYSTEM_PROMPT_GENERATOR,
        )

        # chat_completion()은 tuple을 반환: (content, input_tokens, output_tokens)
        response = response_tuple[0] if isinstance(response_tuple, tuple) else response_tuple

        logger.info(f"[BATCH_METADATA] Claude response received - length={len(response)}")

        # Step 3: JSON 파싱
        metadata = _parse_batch_json_response(response)

        if metadata is None:
            logger.warning("[BATCH_METADATA] Failed to parse Claude response as JSON")
            return {ph_key: None for ph_key in placeholders}

        logger.info(f"[BATCH_METADATA] Metadata generated - count={len(metadata)}")
        return metadata

    except Exception as e:
        logger.error(f"[BATCH_METADATA] Error: {str(e)}", exc_info=True)
        return {ph_key: None for ph_key in placeholders}


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
        response: Claude API의 응답 문자열

    Returns:
        Optional[Dict[str, Dict[str, Any]]]:
            파싱 성공: {"{{TITLE}}": {type, description, ...}, ...}
            파싱 실패: None
    """
    try:
        # 1. 마크다운 코드블록 확인
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end == -1:
                logger.warning("[BATCH_METADATA] Unclosed markdown code block")
                return None
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end == -1:
                logger.warning("[BATCH_METADATA] Unclosed code block")
                return None
            json_str = response[start:end].strip()
        else:
            # JSON 객체 시작과 끝 찾기
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start == -1 or json_end == -1 or json_start >= json_end:
                logger.warning("[BATCH_METADATA] No JSON object found in response")
                return None
            json_str = response[json_start : json_end + 1].strip()

        logger.debug(f"[BATCH_METADATA] Extracted JSON: {json_str[:200]}...")

        # 2. JSON 파싱
        metadata = json.loads(json_str)

        # 3. 유효성 검사
        if not isinstance(metadata, dict):
            logger.warning("[BATCH_METADATA] Parsed JSON is not an object")
            return None

        if len(metadata) == 0:
            logger.warning("[BATCH_METADATA] Parsed JSON object is empty")
            return None

        logger.debug(f"[BATCH_METADATA] Successfully parsed {len(metadata)} items")
        return metadata

    except json.JSONDecodeError as e:
        logger.error(f"[BATCH_METADATA] JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"[BATCH_METADATA] Unexpected error in JSON parsing: {str(e)}")
        return None


def _parse_json_response(response: str) -> Optional[List[Dict[str, Any]]]:
    """
    Claude 응답에서 JSON 배열 추출 및 파싱.

    응답 형식 처리:
    1. 순수 JSON: [...] → 바로 파싱
    2. 마크다운 코드블록: ```json [...] ``` → 추출 후 파싱
    3. 기타 형식: JSON 부분 자동 추출 시도

    Args:
        response: Claude API 응답 문자열

    Returns:
        파싱된 JSON 배열, 실패 시 None
    """
    try:
        # 1. 마크다운 코드블록 확인
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end == -1:
                logger.warning("[METADATA_GEN] Unclosed markdown code block")
                return None
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end == -1:
                logger.warning("[METADATA_GEN] Unclosed code block")
                return None
            json_str = response[start:end].strip()
        else:
            # JSON 배열 시작과 끝 찾기
            json_start = response.find("[")
            json_end = response.rfind("]")
            if json_start == -1 or json_end == -1 or json_start >= json_end:
                logger.warning("[METADATA_GEN] No JSON array found in response")
                return None
            json_str = response[json_start : json_end + 1].strip()

        logger.debug(f"[METADATA_GEN] Extracted JSON: {json_str[:200]}...")

        # 2. JSON 파싱
        metadata = json.loads(json_str)

        # 3. 유효성 검사
        if not isinstance(metadata, list):
            logger.warning("[METADATA_GEN] Parsed JSON is not an array")
            return None

        if len(metadata) == 0:
            logger.warning("[METADATA_GEN] Parsed JSON array is empty")
            return None

        logger.debug(f"[METADATA_GEN] Successfully parsed {len(metadata)} items")
        return metadata

    except json.JSONDecodeError as e:
        logger.error(f"[METADATA_GEN] JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"[METADATA_GEN] Unexpected error in JSON parsing: {str(e)}")
        return None
