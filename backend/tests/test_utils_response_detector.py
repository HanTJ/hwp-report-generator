"""
응답 형태 자동 판별 유틸리티 (response_detector.py) 테스트
"""

import pytest
from app.utils.response_detector import (
    is_report_content,
    extract_h2_sections,
    get_section_content,
    count_empty_sections,
    has_question_keywords,
    remove_code_blocks,
)


@pytest.mark.unit
@pytest.mark.response_detector
class TestExtractH2Sections:
    """H2 섹션 추출 테스트"""

    def test_extract_single_h2_section(self):
        """단일 H2 섹션 추출"""
        text = "## 요약\n내용"
        result = extract_h2_sections(text)
        assert result == ["요약"]

    def test_extract_multiple_h2_sections(self):
        """복수 H2 섹션 추출"""
        text = "## 요약\n내용\n## 배경\n내용\n## 결론\n내용"
        result = extract_h2_sections(text)
        assert result == ["요약", "배경", "결론"]

    def test_extract_no_h2_sections(self):
        """H2 섹션 없는 경우"""
        text = "# 제목\n내용\n### 소제목\n내용"
        result = extract_h2_sections(text)
        assert result == []

    def test_extract_h2_with_special_characters(self):
        """특수문자 포함 H2 섹션"""
        text = "## 주요 내용 (2025-11-11)"
        result = extract_h2_sections(text)
        assert result == ["주요 내용 (2025-11-11)"]


@pytest.mark.unit
@pytest.mark.response_detector
class TestGetSectionContent:
    """섹션 본문 추출 테스트"""

    def test_get_content_single_section(self):
        """단일 섹션 본문 추출"""
        text = "## 요약\n상세 분석 내용입니다."
        result = get_section_content(text, "요약")
        assert result == "상세 분석 내용입니다."

    def test_get_content_between_sections(self):
        """섹션 사이 내용 추출 (다음 H2까지)"""
        text = "## 요약\n내용1\n내용2\n## 배경\n내용3"
        result = get_section_content(text, "요약")
        assert result == "내용1\n내용2"

    def test_get_content_last_section(self):
        """마지막 섹션 본문 추출"""
        text = "## 요약\n내용1\n## 결론\n마지막 내용"
        result = get_section_content(text, "결론")
        assert result == "마지막 내용"

    def test_get_content_empty_section(self):
        """빈 섹션 추출"""
        text = "## 요약\n\n## 배경\n내용"
        result = get_section_content(text, "요약")
        assert result == ""

    def test_get_content_nonexistent_section(self):
        """존재하지 않는 섹션"""
        text = "## 요약\n내용"
        result = get_section_content(text, "없는섹션")
        assert result == ""


@pytest.mark.unit
@pytest.mark.response_detector
class TestCountEmptySections:
    """빈 섹션 카운팅 테스트"""

    def test_count_no_empty_sections(self):
        """빈 섹션 없음"""
        text = "## 요약\n상세한 분석 내용이 여러 줄에 걸쳐 있습니다. 분석 결과를 포함합니다. 이것은 충분히 긴 내용입니다.\n## 배경\n배경 설명이 충분하게 제시됩니다. 여러 줄의 상세한 정보가 포함되어 있습니다. 충분한 길이입니다."
        result = count_empty_sections(text)
        assert result == 0

    def test_count_single_empty_section(self):
        """빈 섹션 1개"""
        text = "## 요약\n\n## 배경\n배경 설명이 충분합니다. 이 섹션은 50자 이상의 의미있는 내용입니다. 정말 충분한 내용."
        result = count_empty_sections(text)
        assert result == 1

    def test_count_multiple_empty_sections(self):
        """빈 섹션 2개 이상"""
        text = "## 요약\n\n## 배경\n\n## 내용\n"
        result = count_empty_sections(text)
        assert result == 3

    def test_count_short_content_as_empty(self):
        """짧은 내용(50자 미만)도 빈 섹션으로 카운트"""
        text = "## 요약\n짧은 내용\n## 배경\n그것도 짧은 내용"
        result = count_empty_sections(text)
        # "짧은 내용" = 5자 < 50자
        # "그것도 짧은 내용" = 8자 < 50자
        assert result == 2

    def test_count_exactly_50_chars_not_empty(self):
        """정확히 50자 = 빈 섹션 아님"""
        text = "## 요약\n" + "a" * 50  # 정확히 50자
        result = count_empty_sections(text)
        assert result == 0

    def test_count_49_chars_empty(self):
        """49자 = 빈 섹션"""
        text = "## 요약\n" + "a" * 49
        result = count_empty_sections(text)
        assert result == 1


@pytest.mark.unit
@pytest.mark.response_detector
class TestHasQuestionKeywords:
    """질문 키워드 검사 테스트"""

    # 그룹 1: 피드백 요청
    def test_keyword_modification_request(self):
        """수정 요청 키워드"""
        text = "## 내용\n내용\n어떤 부분을 수정하시겠습니까?"
        result = has_question_keywords(text)
        assert result == "feedback_modification"

    def test_keyword_feedback_needed(self):
        """피드백 필요 키워드"""
        text = "수정이 필요하신 부분이 있으시면 말씀해주세요."
        result = has_question_keywords(text)
        assert result is not None

    def test_keyword_speech_request(self):
        """말씀해주세요 키워드"""
        text = "의견을 말씀해 주세요."
        result = has_question_keywords(text)
        assert result == "request_speech"

    # 그룹 2: 재확인 패턴
    def test_keyword_confirmed_question(self):
        """확인 + 맞나요 패턴"""
        text = "원문을 확인했습니다. 맞나요?"
        result = has_question_keywords(text)
        assert result == "confirmed_question"

    def test_keyword_structure_confirmed(self):
        """구조 파악 패턴"""
        text = "문서 구조를 파악했습니다. 이게 맞습니까?"
        result = has_question_keywords(text)
        assert result == "structure_confirmed"

    # 그룹 3: 조건부 제안
    def test_keyword_conditional_if(self):
        """조건부 패턴 (할 경우)"""
        text = "수정이 필요할 경우, 다시 연락주세요."
        result = has_question_keywords(text)
        assert result == "conditional_if"

    def test_keyword_future_case(self):
        """미래 조건부 (향후 ~ 있을 경우)"""
        text = "향후 추가 요청이 있을 경우 작업하겠습니다."
        result = has_question_keywords(text)
        assert result == "future_case"

    def test_keyword_possible_options(self):
        """가능한 옵션 패턴"""
        text = "다음과 같은 수정 작업이 가능합니다:"
        result = has_question_keywords(text)
        assert result == "possible_options"

    # 그룹 4: 사용자 선택
    def test_keyword_which_part(self):
        """어떤 부분 키워드"""
        text = "어떤 부분을 수정하시겠습니까?"
        result = has_question_keywords(text)
        assert result is not None

    def test_keyword_what_choice(self):
        """무엇을 키워드"""
        text = "무엇을 선택하시겠습니까?"
        result = has_question_keywords(text)
        assert result == "what_choice"

    def test_no_question_keywords(self):
        """질문 키워드 없음"""
        text = "보고서 내용입니다. 여러 섹션의 상세 분석이 포함되어 있습니다."
        result = has_question_keywords(text)
        assert result is None


@pytest.mark.unit
@pytest.mark.response_detector
class TestRemoveCodeBlocks:
    """코드블록 제거 테스트"""

    def test_remove_triple_backtick_block(self):
        """``` 코드블록 제거"""
        text = "텍스트\n```python\ncode\n```\n텍스트"
        result = remove_code_blocks(text)
        assert "code" not in result
        assert "텍스트" in result

    def test_remove_triple_tilde_block(self):
        """~~~ 코드블록 제거"""
        text = "텍스트\n~~~\ncode\n~~~\n텍스트"
        result = remove_code_blocks(text)
        assert "code" not in result
        assert "텍스트" in result

    def test_remove_multiple_blocks(self):
        """복수 코드블록 제거"""
        text = "텍스트1\n```\ncode1\n```\n텍스트2\n~~~\ncode2\n~~~\n텍스트3"
        result = remove_code_blocks(text)
        assert "code1" not in result
        assert "code2" not in result
        assert "텍스트1" in result and "텍스트2" in result and "텍스트3" in result


@pytest.mark.unit
@pytest.mark.response_detector
class TestIsReportContent:
    """응답 형태 판별 통합 테스트"""

    # TC-DETECT-001: 실제 보고서
    def test_detect_actual_report(self):
        """TC-DETECT-001: 실제 보고서 응답"""
        text = """## 요약
상세한 분석 내용이 포함된 요약입니다. 이것은 실제 보고서 본문입니다. 충분히 긴 설명이 포함되어 있습니다.

## 배경
배경 설명이 상세하게 제시됩니다. 여러 줄의 중요한 정보가 포함되어 있습니다. 이것도 의미있는 내용입니다.

## 주요 내용
주요 분석 결과를 제시합니다. 이것은 의미있는 콘텐츠입니다. 50자를 넘는 충분한 내용입니다."""
        assert is_report_content(text) is True

    # TC-DETECT-002: 빈 섹션 많음
    def test_detect_empty_sections(self):
        """TC-DETECT-002: 빈 섹션 많은 경우"""
        text = """## 요약


## 배경


## 내용
아주 짧음"""
        assert is_report_content(text) is False

    # TC-DETECT-003: 질문 키워드 포함
    def test_detect_question_keyword(self):
        """TC-DETECT-003: 질문 키워드 포함"""
        text = """## 요약
이것은 분석 내용입니다.
충분한 길이의 본문입니다.

## 배경
배경 설명입니다.

어떤 부분을 수정하시겠습니까?"""
        assert is_report_content(text) is False

    # TC-DETECT-004: 피드백 요청
    def test_detect_feedback_request(self):
        """TC-DETECT-004: 피드백 요청"""
        text = """## 요약
분석 내용이 충분합니다.
이것은 의미있는 콘텐츠입니다.

수정이 필요하신 부분이 있으시면 말씀해주세요."""
        assert is_report_content(text) is False

    # TC-DETECT-005: 재확인 패턴
    def test_detect_confirm_pattern(self):
        """TC-DETECT-005: 재확인 패턴"""
        text = """## 요약
내용 분석입니다.
충분한 길이의 본문입니다.

원문을 확인했습니다. 맞나요?"""
        assert is_report_content(text) is False

    # TC-DETECT-006: 조건부 제안
    def test_detect_conditional_proposal(self):
        """TC-DETECT-006: 조건부 제안"""
        text = """## 요약
분석 내용입니다.
충분한 본문입니다.

## 제안사항
수정이 필요할 경우, 말씀해주세요."""
        assert is_report_content(text) is False

    # TC-DETECT-007: 섹션 1개, 의미있는 내용
    def test_detect_single_meaningful_section(self):
        """TC-DETECT-007: 섹션 1개만 있어도 의미있으면 보고서"""
        text = """## 결론
금융시장 전망에 대한 상세한 분석입니다.
이것은 실제 보고서 본문입니다.
충분한 길이의 의미있는 내용입니다."""
        assert is_report_content(text) is True

    # TC-DETECT-008: 혼합 (일부 질문)
    def test_detect_mixed_with_question(self):
        """TC-DETECT-008: 일부 질문 포함"""
        text = """## 요약
분석 내용입니다.

## 구조
문서 구조 설명입니다.
충분한 길이입니다.

어떤 부분을 수정하시겠습니까?"""
        assert is_report_content(text) is False

    # 추가: 빈 응답
    def test_detect_empty_response(self):
        """빈 응답 처리"""
        assert is_report_content("") is False
        assert is_report_content(None) is False
        assert is_report_content("   ") is False

    # 추가: H2 섹션 없음
    def test_detect_no_h2_sections(self):
        """H2 섹션 없음 = 질문"""
        text = "이것은 간단한 질문입니다. 어떻게 생각하시나요?"
        assert is_report_content(text) is False

    # 추가: 실제 사례
    def test_detect_real_case_assistant_response(self):
        """실제 사례: Claude 재확인 응답"""
        text = """#

_생성일: 2025-11-11 16:20:16_


## 요약




## 배경 및 목적




## 주요 내용

원문을 확인했습니다. 향후 이 보고서에 대한 수정 요청이 있을 경우, 제공해주신 마크다운 원문을 기준으로 작업하겠습니다.

현재 원문의 구조는 다음과 같이 파악됩니다:

## 문서 구조
- **제목**: 2026년 금융권 코스피 전망 보고서
- **생성일**: 2025-11-11 16:14:08
- **주요 섹션**:
  1. 보고서 개요
  2. 배경 및 현황 (글로벌 경제 환경, 국내 금융시장 현황, 규제 환경)
  3. 주요 내용 (은행권/증권권/보험권 전망, 섹터별 투자 전략)
  4. 결론 및 제언 (종합 평가, 코스피 금융지수 전망, 투자 제언, 최종 의견)

수정이 필요하신 부분이 있으시면 말씀해 주세요. 다음과 같은 수정 작업이 가능합니다:

- 특정 섹션의 내용 수정/추가/삭제
- 수치 데이터 업데이트
- 전망치 조정
- 새로운 분석 항목 추가
- 문체 또는 표현 개선
- 표 또는 목록 형식 변경

어떤 부분을 수정하시겠습니까?


## 결론 및 제언
"""
        result = is_report_content(text)
        # 빈 섹션 (요약, 배경 및 목적, 결론 및 제언) = 3개
        # 질문 키워드 ("수정하시겠습니까?", "말씀해 주세요")
        assert result is False
