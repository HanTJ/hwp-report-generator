"""응답 형태 자동 판별 유틸리티 모듈.

Claude API 응답이 실제 보고서 콘텐츠인지 추가 질문/대화인지 판별합니다.
3단계 알고리즘: 구조 검사 → 내용 검사 → 의도 검사
"""

import re
from typing import List
import logging

logger = logging.getLogger(__name__)


def is_report_content(response_text: str) -> bool:
    """Claude 응답이 실제 보고서 콘텐츠인지 판별합니다.

    3단계 판별 알고리즘을 사용합니다:
    1. H2 섹션(##) 구조 검사 → 없으면 False (질문)
    2. 섹션별 내용 검사 → 빈 섹션 2개 이상이면 False (질문)
    3. 질문/대화 키워드 검사 → 키워드 있으면 False (질문)

    Args:
        response_text: Claude API 응답 텍스트

    Returns:
        True: 보고서 콘텐츠, False: 질문/대화

    Examples:
        >>> is_report_content("## 요약\\n상세 분석 내용입니다...")
        True

        >>> is_report_content("## 요약\\n\\n## 배경\\n\\n어떤 부분을 수정하시겠습니까?")
        False
    """

    if not response_text or not response_text.strip():
        logger.warning("[DETECT] Empty response, treating as non-report")
        return False

    # Step 1: H2 섹션 검사
    h2_sections = extract_h2_sections(response_text)

    if not h2_sections:
        logger.info("[DETECT] No H2 sections found → Question/Conversation")
        return False

    logger.info(f"[DETECT] Found {len(h2_sections)} H2 sections: {h2_sections[:3]}")

    # Step 2: 빈 섹션 검사
    empty_count = count_empty_sections(response_text)
    total_sections = len(h2_sections)
    empty_ratio = empty_count / total_sections if total_sections > 0 else 0

    logger.info(
        f"[DETECT] Empty sections check: {empty_count}/{total_sections} "
        f"(ratio={empty_ratio:.1%})"
    )

    if empty_count >= 2:
        logger.info(
            f"[DETECT] Too many empty sections ({empty_count}) → Question"
        )
        return False

    # Step 3: 질문 키워드 검사
    question_keywords = has_question_keywords(response_text)

    if question_keywords:
        logger.info(f"[DETECT] Question keywords detected: {question_keywords}")
        return False

    logger.info("[DETECT] All checks passed → Report content")
    return True


def extract_h2_sections(text: str) -> List[str]:
    """H2 마크다운 섹션(##)의 제목을 추출합니다.

    Args:
        text: 마크다운 텍스트

    Returns:
        H2 섹션 제목 리스트 (예: ["요약", "배경", "내용"])
    """
    pattern = r"^## (.+?)$"
    matches = re.findall(pattern, text, re.MULTILINE)
    return matches


def get_section_content(text: str, section_title: str) -> str:
    """특정 H2 섹션의 본문을 추출합니다.

    Args:
        text: 마크다운 텍스트
        section_title: 섹션 제목 (예: "요약", "## 제목" 형식 아님)

    Returns:
        섹션 본문 (다음 H2까지 또는 EOF까지)
    """
    # ## 섹션을 찾기 (정확히 매칭)
    escaped_title = re.escape(section_title)

    # 두 가지 패턴 시도: 정확한 매칭과 문자열 검색
    # 패턴 1: 정확한 ## 형식
    pattern1 = rf"^## {escaped_title}$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern1, text, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()

    # 패턴 2: ## 제목 형식 (공백 변동)
    pattern2 = rf"^##\s+{escaped_title}$\n(.*?)(?=^##|\Z)"
    match = re.search(pattern2, text, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


def count_empty_sections(text: str) -> int:
    """빈 섹션의 개수를 카운트합니다.

    빈 섹션: 본문이 50자 미만인 경우

    Args:
        text: 마크다운 텍스트

    Returns:
        빈 섹션 개수
    """
    sections = extract_h2_sections(text)
    empty_count = 0

    for section_title in sections:
        content = get_section_content(text, section_title)

        # 공백/줄바꿈 제거
        content_cleaned = content.strip()

        if len(content_cleaned) < 50:
            empty_count += 1
            logger.debug(
                f"[DETECT] Empty section: '{section_title}' "
                f"(length={len(content_cleaned)})"
            )

    return empty_count


def has_question_keywords(text: str) -> str | None:
    """질문/대화 의도를 나타내는 키워드를 검사합니다.

    Args:
        text: 마크다운 텍스트

    Returns:
        매칭된 패턴 설명 (예: "feedback_request"), None이면 키워드 없음
    """

    # 그룹 1: 피드백 요청
    feedback_keywords = [
        (r"수정이\s*필요하신\s*부분", "feedback_request"),
        (r"어떤\s*부분을\s*수정하시", "feedback_modification"),
        (r"피드백을\s*주세요", "request_feedback"),
        (r"의견을\s*주세요", "request_opinion"),
        (r"제안해\s*주세요", "request_suggestion"),
    ]

    # 그룹 2: 재확인 패턴 (확인 + 재질문)
    confirm_keywords = [
        (r"확인했습니다.*?맞", "confirmed_question"),
        (r"원문을\s*확인.*?제공해", "confirmed_provision"),
        (r"구조를\s*파악했습니다", "structure_confirmed"),
    ]

    # 그룹 3: 조건부/미래 제안 (더 구체적인 패턴)
    conditional_keywords = [
        # "수정이 필요할 경우" 같은 패턴 (단어 + "할 경우")
        (r"[가-힣\s]+할\s*경우[,.]", "conditional_if"),
        (r"향후.*?있을\s*경우", "future_case"),
        (r"다음과\s*같은.*?가능합니다", "possible_options"),
        (r"[가-힣]+시\s+[가-힣]+", "conditional_structure"),
    ]

    # 그룹 4: 사용자 선택 대기
    choice_keywords = [
        (r"어떤\s*부분을", "which_part"),
        (r"무엇을", "what_choice"),
        (r"어떤\s*것", "which_thing"),
        (r"어느\s*것", "which_one"),
    ]

    # 그룹 5: 말씀해주세요 (독립적으로 처리)
    speech_keywords = [
        (r"말씀해\s*주세요", "request_speech"),
        (r"말씀해주세요", "request_speech"),
    ]

    all_keywords = (
        feedback_keywords
        + confirm_keywords
        + conditional_keywords
        + choice_keywords
        + speech_keywords
    )

    for pattern, keyword_type in all_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            logger.debug(f"[DETECT] Question keyword matched: {keyword_type}")
            return keyword_type

    return None


def remove_code_blocks(text: str) -> str:
    """마크다운 코드블록을 제거합니다.

    Args:
        text: 마크다운 텍스트

    Returns:
        코드블록 제거된 텍스트
    """
    # ``` ... ``` 블록 제거
    text = re.sub(r"```[\s\S]*?```", "", text)

    # ~~~ ... ~~~ 블록 제거
    text = re.sub(r"~~~[\s\S]*?~~~", "", text)

    return text



def extract_question_content(text: str) -> str:
    """질문 응답에서 H2 섹션을 제거하고 순수 본문만 추출합니다.

    System Prompt의 마크다운 섹션 구조(##)를 제거하여 자연스러운 대화체로 변환합니다.
    
    4단계 추출 알고리즘:
    1. H2 마크다운 섹션(##) 감지 → 없으면 원본 반환
    2. 각 섹션의 본문 추출 → 50자 미만의 빈 섹션 제외
    3. 개행 정규화 → 과도한 줄바꿈 제거 (3개 이상 → 1개)
    4. 최종 정규화 → 선행/후행 공백 제거

    Args:
        text: Claude API 응답 텍스트 (H2 섹션 포함 가능)

    Returns:
        순수 질문/답변 텍스트 (섹션 구조 제거됨)

    Examples:
        >>> text = "## 요약\\n\\n## 배경\\n배경 내용\\n## 결론\\n"
        >>> extract_question_content(text)
        '배경 내용'

        >>> text = "## 요약\\n\\n어떤 부분을 수정하시겠습니까?"
        >>> extract_question_content(text)
        '어떤 부분을 수정하시겠습니까?'
    """
    if not text or not text.strip():
        logger.debug("[EXTRACT] Empty text, returning empty string")
        return ""

    # Step 1: H2 섹션 감지
    h2_sections = extract_h2_sections(text)
    
    if not h2_sections:
        logger.debug("[EXTRACT] No H2 sections found, returning original text")
        return text.strip()

    logger.debug(f"[EXTRACT] Found {len(h2_sections)} sections: {h2_sections}")

    # Step 2: 각 섹션의 본문 추출
    extracted_contents = []
    
    for section_title in h2_sections:
        section_content = get_section_content(text, section_title)
        
        # 공백/줄바꿈만 있는 빈 섹션 제외
        if len(section_content.strip()) >= 1:  # 1자 이상만 포함
            extracted_contents.append(section_content)
            logger.debug(f"[EXTRACT] Section '{section_title}': {len(section_content)} chars")

    # Step 3 & 4: 개행 정규화 및 최종 정규화
    if not extracted_contents:
        logger.debug("[EXTRACT] All sections are empty, returning empty string")
        return ""

    # 모든 섹션 본문을 줄바꿈으로 연결
    combined_text = "\n".join(extracted_contents)
    
    # 연속된 개행 정규화: 3개 이상 → 1개로
    combined_text = re.sub(r"\n{3,}", "\n\n", combined_text)
    
    # 선행/후행 공백 제거
    final_text = combined_text.strip()
    
    logger.debug(f"[EXTRACT] Final extracted text length: {len(final_text)} chars")
    
    return final_text
