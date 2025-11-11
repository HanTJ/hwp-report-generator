"""
Claude API System Prompts
보고서 생성에 사용되는 system prompt 상수 정의

구조:
1. BASE_REPORT_SYSTEM_PROMPT: 모든 보고서에 적용되는 기본 지침 (섹션 정의 없음)
2. FINANCIAL_REPORT_SYSTEM_PROMPT: BASE + 5개 섹션 정의 (Placeholder 없을 때만 사용)
3. create_dynamic_system_prompt(): Placeholder 기반 동적 규칙 생성 (meta_info_generator와 동기화)
"""

# ============================================================
# Step 1: BASE_REPORT_SYSTEM_PROMPT - 공통 기본 지침
# ============================================================
# 역할: 모든 보고서에 적용되는 보편적인 가이드라인
# 특징: 섹션 정의 없음 (meta_info_generator와의 충돌 회피)

BASE_REPORT_SYSTEM_PROMPT = """당신은 금융 기관의 전문 보고서 작성자입니다.
사용자가 제공하는 주제에 대해 금융 업무보고서를 작성해주세요.

전문적이고 격식있는 문체로 작성하되, 명확하고 이해하기 쉽게 작성해주세요.
금융 용어와 데이터를 적절히 활용하여 신뢰성을 높여주세요."""

# ============================================================
# Step 2: FINANCIAL_REPORT_SYSTEM_PROMPT - 기본 5개 섹션 정의
# ============================================================
# 역할: Placeholder가 없는 기본 보고서용 (기존 호환성 유지)
# 사용 시점: create_dynamic_system_prompt([]) 호출 시

FINANCIAL_REPORT_SYSTEM_PROMPT = BASE_REPORT_SYSTEM_PROMPT + """

**기본 보고서 구조 (5개 섹션):**

아래 형식에 맞춰 각 섹션을 작성해주세요:

1. **제목** - 간결하고 명확하게
2. **요약 섹션** - 2-3문단으로 핵심 내용 요약
   - 섹션 제목 예: "요약", "핵심 요약", "Executive Summary" 등
3. **배경 섹션** - 왜 이 보고서가 필요한지 설명
   - 섹션 제목 예: "배경 및 목적", "추진 배경", "사업 배경" 등
4. **주요 내용 섹션** - 구체적이고 상세한 분석 및 설명 (3-5개 소제목 포함)
   - 섹션 제목 예: "주요 내용", "분석 결과", "세부 내역" 등
5. **결론 섹션** - 요약과 향후 조치사항
   - 섹션 제목 예: "결론 및 제언", "향후 계획", "시사점" 등

각 섹션 제목은 보고서 내용과 맥락에 맞게 자유롭게 작성하되,
반드시 위의 4개 섹션(요약, 배경, 주요내용, 결론) 순서를 따라야 합니다.

**출력은 반드시 다음 Markdown 형식을 사용하세요:**
- # {제목} (H1)
- ## {요약 섹션 제목} (H2)
- ## {배경 섹션 제목} (H2)
- ## {주요내용 섹션 제목} (H2)
- ## {결론 섹션 제목} (H2)"""



# ============================================================
# Step 3: create_dynamic_system_prompt() - 동적 규칙 생성
# ============================================================
# 역할: Placeholder 기반 동적 System Prompt 생성
# 특징: meta_info_generator의 분류 결과와 자동 동기화
# 규칙:
#   - Placeholder 없으면: FINANCIAL_REPORT_SYSTEM_PROMPT 반환 (5개 섹션 강제)
#   - Placeholder 있으면: 해당 Placeholder만 강제 (동적 규칙 생성)

def create_dynamic_system_prompt(placeholders: list) -> str:
    """Template의 placeholder를 기반으로 동적 system prompt를 생성합니다.

    중요: meta_info_generator의 분류 결과를 따라 "유연한" 규칙을 생성합니다.
    - Placeholder가 없으면: 기본 5개 섹션 강제 (FINANCIAL_REPORT_SYSTEM_PROMPT)
    - Placeholder가 있으면: 해당 Placeholder만 강제 (동적 규칙, meta_info_generator와 동기화)

    이렇게 하면 meta_info_generator의 "유연한 분류"와 일치합니다.

    Args:
        placeholders: Template에 정의된 Placeholder 객체 리스트
                     각 Placeholder는 placeholder_key 속성 (예: "{{TITLE}}")을 가짐

    Returns:
        동적으로 생성된 system prompt (Markdown 형식 지시사항 포함)

    Examples:
        >>> class MockPlaceholder:
        ...     def __init__(self, key):
        ...         self.placeholder_key = key
        >>> placeholders = [
        ...     MockPlaceholder("{{TITLE}}"),
        ...     MockPlaceholder("{{SUMMARY}}")
        ... ]
        >>> prompt = create_dynamic_system_prompt(placeholders)
        >>> "TITLE" in prompt and "SUMMARY" in prompt
        True
    """
    if not placeholders:
        return FINANCIAL_REPORT_SYSTEM_PROMPT

    # 1. Placeholder 키 추출 및 정리 (중복 제거)
    placeholder_names = []
    for ph in placeholders:
        # placeholder_key에서 {{ }} 제거
        key = ph.placeholder_key.replace("{{", "").replace("}}", "")
        placeholder_names.append(key)

    # 중복 제거 (순서 유지)
    seen = set()
    unique_placeholders = []
    for name in placeholder_names:
        if name not in seen:
            seen.add(name)
            unique_placeholders.append(name)

    # 2. 명확한 Markdown 형식 규칙 생성 (Placeholder 기반, meta_info_generator와 동기화)
    markdown_rules = ["**출력은 반드시 다음 Markdown 형식을 사용하세요:**"]

    for i, placeholder in enumerate(unique_placeholders):
        if i == 0:
            # 첫 번째는 제목 (H1)
            markdown_rules.append(f"- # {{{{{placeholder}}}}} (H1)")
        else:
            # 나머지는 섹션 (H2)
            markdown_rules.append(f"- ## {{{{{placeholder}}}}} (H2)")

    markdown_section = "\n".join(markdown_rules)

    # 3. BASE + 동적 섹션 + Markdown 규칙 조합
    dynamic_prompt = f"""{BASE_REPORT_SYSTEM_PROMPT}

**커스텀 템플릿 구조 (다음 placeholder들을 포함하여 작성):**

""" + "\n".join([f"- {name}" for name in unique_placeholders]) + f"""

{markdown_section}

**작성 가이드:**
- 각 섹션은 Markdown heading (#, ##)으로 시작하세요
- 위에 명시된 placeholder와 heading 구조를 정확히 따르세요
- 새로운 placeholder를 임의로 추가하지 마세요
- 각 섹션은 명확하고 구조화된 내용을 포함하세요
- 전문적이고 객관적인 톤을 유지하세요
- 마크다운 형식을 엄격히 준수하세요"""

    return dynamic_prompt

def create_topic_context_message(topic_input_prompt: str) -> dict:
    """대화 주제를 포함하는 context message를 생성합니다.

    이 함수는 Topics API의 MessageAsk 엔드포인트에서 사용되며,
    대화의 주제를 첫 번째 user message로 추가하여
    Claude가 일관된 맥락을 유지하도록 돕습니다.

    Args:
        topic_input_prompt: 대화 주제 (예: "2025 디지털뱅킹 트렌드 분석")

    Returns:
        Claude API messages 형식의 딕셔너리
        {
            "role": "user",
            "content": "대화 주제: {topic}\\n\\n이전 메시지를 참고하세요."
        }

    Examples:
        >>> msg = create_topic_context_message("디지털뱅킹 트렌드")
        >>> msg["role"]
        'user'
        >>> "디지털뱅킹 트렌드" in msg["content"]
        True
    """
    return {
        "role": "user",
        "content": f"**대화 주제**: {topic_input_prompt}\n\n이전 메시지들을 문맥으로 활용하여 일관된 문체와 구조로 답변하세요."
    }
