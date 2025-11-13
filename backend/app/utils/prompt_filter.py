"""프롬프트 필터링 및 최적화 모듈

Template의 prompt_system에서 필요한 부분만 추출하여
Sequential Planning 응답시간을 최적화합니다.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_section_guidelines(prompt_system: Optional[str]) -> Optional[str]:
    """
    템플릿 프롬프트에서 '## 섹션별 상세 지침:' 부터 '## 작성 가이드' 직전까지 추출

    Templates의 prompt_system에는 다음 구조로 저장됩니다:
    1. 기본 지침 (커스텀 템플릿 구조, 출력 마크다운 형식)
    2. 섹션별 상세 지침 (각 placeholder별 설명, 예시, 필수 여부) ← 이 부분만 추출
    3. 작성 가이드 (일반적인 작성 원칙) ← 제거됨

    Sequential Planning에서는 섹션별 상세 지침만 필요하므로,
    이 함수로 필터링하여 토큰 효율을 높입니다.

    Args:
        prompt_system: 원본 템플릿 프롬프트 문자열 (None 가능)

    Returns:
        "## 섹션별 상세 지침:"부터 "## 작성 가이드" 직전까지의 내용
        - 지침이 없으면 None 반환 (하위호환성)
        - 빈 문자열 입력 시 None 반환

    Example:
        >>> prompt = \"\"\"기본 지침...
        ... ## 섹션별 상세 지침:
        ... ### {{DATE}}
        ... **설명:** 보고서 작성 날짜
        ... ## 작성 가이드:
        ... 일반 작성 원칙...
        ... \"\"\"
        >>> result = extract_section_guidelines(prompt)
        >>> result.startswith('## 섹션별')
        True
        >>> '## 작성 가이드' in result
        False

    Performance:
        - 실행시간: < 1ms (일반적인 프롬프트)
        - 메모리: O(n) where n = 프롬프트 길이
    """
    # 입력 검증
    if not prompt_system:
        return None

    if not isinstance(prompt_system, str):
        logger.warning(f"extract_section_guidelines: invalid type {type(prompt_system)}")
        return None

    if not prompt_system.strip():
        return None

    try:
        # 정규식 패턴:
        # "## 섹션별 상세 지침:" 부터 시작하여 "## 작성 가이드" 직전까지 추출
        # (?=...) 는 lookahead assertion (positive lookahead)
        # "## 작성 가이드" 또는 문자열 끝까지 추출
        pattern = r"##\s*섹션별\s*상세\s*지침\s*:[\s\S]*?(?=\n##\s*작성\s*가이드|\Z)"
        match = re.search(pattern, prompt_system, re.MULTILINE)

        if not match:
            logger.debug("extract_section_guidelines: section guidelines not found")
            return None

        # 매칭된 부분 추출 및 정리
        guidelines = match.group(0).strip()

        if not guidelines:
            logger.debug("extract_section_guidelines: extracted content is empty")
            return None

        logger.debug(
            f"extract_section_guidelines: successfully extracted "
            f"guidelines ({len(guidelines)} chars)"
        )

        return guidelines

    except Exception as e:
        logger.error(
            f"extract_section_guidelines: error during extraction - {str(e)}",
            exc_info=True
        )
        # 에러 발생 시 None 반환 (fallback)
        return None


def filter_guidance_prompt(prompt_system: Optional[str]) -> Optional[str]:
    """
    Template의 prompt_system을 Sequential Planning용으로 필터링

    이 함수는 전체 prompt_system에서 불필요한 부분을 제거하고
    핵심 지침만 추출합니다.

    현재 전략:
    - 섹션별 상세 지침만 추출

    향후 확장 가능:
    - 추가 필터링 전략 적용
    - 프롬프트 최적화 로직 추가

    Args:
        prompt_system: 원본 프롬프트

    Returns:
        필터링된 프롬프트 (또는 None)
    """
    return extract_section_guidelines(prompt_system)
