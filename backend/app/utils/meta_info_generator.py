"""
메타정보 생성 유틸리티

Placeholder를 분석하여 각 Placeholder에 맞는 메타정보 JSON을 자동 생성합니다.
SystemPromptGenerate.md 규칙을 구현합니다.
"""

from typing import List, Dict, Any
from app.models.placeholder import PlaceholderMetadata, PlaceholdersMetadataCollection


def create_meta_info_from_placeholders(placeholders: List[Any]) -> List[Dict[str, Any]]:
    """Placeholder 리스트를 기반으로 메타정보 JSON 생성.

    Placeholder 이름에서 자동으로 타입을 분류하고, 각 타입별로 적절한
    display_name, description, examples를 생성합니다.

    Args:
        placeholders: Placeholder 객체 리스트. 각 객체는 placeholder_key 속성을 가짐
                     (예: "{{TITLE}}", "{{SUMMARY}}")

    Returns:
        메타정보 JSON 배열. 각 항목은 다음 필드를 가짐:
            - key: Placeholder 키 (예: "{{TITLE}}")
            - type: 분류 타입 ("section_title", "section_content", "metadata")
            - display_name: 한글 표시 이름
            - description: 상세 설명 (2-4문장)
            - examples: 예시 문장 리스트 (1-3개)
            - required: 필수 여부 (metadata 제외 true)
            - order_hint: 추천 순서 (0-2)

    Examples:
        >>> placeholders = [
        ...     type('P', (), {'placeholder_key': '{{TITLE}}'})(),
        ...     type('P', (), {'placeholder_key': '{{SUMMARY}}'})()
        ... ]
        >>> meta = create_meta_info_from_placeholders(placeholders)
        >>> meta[0]['type']
        'section_title'
        >>> meta[1]['type']
        'section_content'
    """
    meta_info = []

    # 키워드별 분류 규칙 (SystemPromptGenerate.md 참조)
    keyword_classification = {
        "TITLE": {"type": "section_title", "section": "제목"},
        "SUMMARY": {"type": "section_content", "section": "요약"},
        "BACKGROUND": {"type": "section_content", "section": "배경"},
        "CONCLUSION": {"type": "section_content", "section": "결론"},
        "DATE": {"type": "metadata", "section": "날짜"},
    }

    # 순서 힌트 정의
    order_hints = {
        "section_title": 1,
        "section_content": 2,
        "metadata": 0
    }

    for placeholder in placeholders:
        key = placeholder.placeholder_key  # "{{TITLE}}" 형태
        key_name = key.replace("{{", "").replace("}}", "")  # "TITLE"

        # 1. 유형 분류
        classification = None
        for keyword, config in keyword_classification.items():
            if keyword in key_name:
                classification = config
                break

        if not classification:
            # 기본값: section_content (안전한 기본값)
            classification = {"type": "section_content", "section": "내용"}

        # 2. 메타정보 구성
        meta_item = {
            "key": key,
            "type": classification["type"],
            "display_name": _get_display_name(key_name, classification["type"]),
            "description": _get_description(key_name, classification),
            "examples": _get_examples(key_name, classification),
            "required": classification["type"] != "metadata",
            "order_hint": order_hints.get(classification["type"], 2)
        }

        meta_info.append(meta_item)

    return meta_info


def _get_display_name(key_name: str, ph_type: str) -> str:
    """키 이름에서 한글 display_name 생성.

    Args:
        key_name: Placeholder 키 이름 (예: "TITLE", "RISK_ANALYSIS")
        ph_type: Placeholder 타입 (section_title, section_content, metadata)

    Returns:
        한글 표시 이름 (예: "보고서 제목", "RISK_ANALYSIS 섹션")
    """
    display_names = {
        "TITLE": "보고서 제목",
        "SUMMARY": "요약",
        "BACKGROUND": "배경",
        "CONCLUSION": "결론",
        "DATE": "작성 날짜",
        "MAIN_CONTENT": "주요 내용",
        "RISK": "위험 요소",
    }
    return display_names.get(key_name, f"{key_name} 섹션")


def _get_description(key_name: str, classification: Dict) -> str:
    """키 이름에 따른 상세 설명 생성.

    Args:
        key_name: Placeholder 키 이름
        classification: 분류 정보 (type, section 포함)

    Returns:
        상세 설명 문자열 (2-4문장)
    """
    descriptions = {
        "TITLE": "보고서의 명확하고 간결한 제목을 작성하세요. 주요 주제를 한 문장으로 표현해야 합니다.",
        "SUMMARY": "2-3문단으로 보고서의 핵심 내용을 요약합니다. 독자가 전체 내용을 빠르게 파악할 수 있도록 작성해주세요.",
        "BACKGROUND": "보고서를 작성하게 된 배경, 현황, 문제의식을 설명합니다. 독자가 이후 내용을 이해하는 데 필요한 최소한의 맥락을 제공해주세요.",
        "CONCLUSION": "보고서의 요약과 향후 조치사항을 제시합니다. 주요 결론과 제언을 명확하게 정리해주세요.",
        "DATE": "보고서 작성 날짜를 입력하세요. (예: 2025-11-08)",
        "MAIN_CONTENT": "3-5개의 소제목으로 구체적이고 상세한 분석 내용을 작성하세요.",
        "RISK": "고려해야 할 주요 위험 요소와 제약사항을 명시해주세요.",
    }

    desc = descriptions.get(key_name, f"{key_name}에 해당하는 내용을 작성해주세요.")

    # 애매한 경우 주석 추가
    if key_name not in descriptions:
        desc += " (이 키의 이름이 모호하여 일반적인 보고서 규칙에 따라 추론한 정의입니다.)"

    return desc


def _get_examples(key_name: str, classification: Dict) -> List[str]:
    """키 이름에 따른 예시 문장 생성.

    Args:
        key_name: Placeholder 키 이름
        classification: 분류 정보

    Returns:
        예시 문장 리스트 (1-3개)
    """
    examples = {
        "TITLE": ["2025 디지털뱅킹 트렌드 분석", "모바일 뱅킹 고도화 방안"],
        "SUMMARY": ["최근 디지털 채널 이용률이 75%를 초과함에 따라 모바일 채널 고도화 필요성이 대두되었습니다."],
        "BACKGROUND": ["당 행의 전자금융 이용자는 전년도 대비 45% 증가하였으며, 특히 20-40대 이용자가 전체의 68%를 차지하고 있습니다."],
        "CONCLUSION": ["모바일 채널의 경쟁력 강화와 고객 경험 개선을 통해 시장 점유율을 15% 확대할 수 있을 것으로 기대됩니다."],
        "DATE": ["2025-11-08"],
        "MAIN_CONTENT": ["1) 시장 현황: 디지털뱅킹 시장은 연 30% 성장", "2) 고객 수요: 모바일 우선 사용자 비중 65%"],
        "RISK": ["규제 강화: 금융감독 기준 변경 가능성", "기술 위험: 사이버 보안 위협"],
    }

    return examples.get(key_name, [f"{key_name}에 해당하는 예시를 제공하세요."])


def generate_placeholder_metadata(
    raw_placeholders: List[str]
) -> PlaceholdersMetadataCollection:
    """Placeholder 키 목록에서 구조화된 메타정보 생성.

    HWPX 파일에서 추출된 raw placeholder 키 목록(예: ["{{TITLE}}", "{{SUMMARY}}"])을
    받아 각 Placeholder의 타입, 필수 여부, 길이 제한 등을 포함한
    구조화된 메타정보 JSON을 생성합니다.

    Args:
        raw_placeholders: Placeholder 키 목록 (예: ["{{TITLE}}", "{{SUMMARY}}"])

    Returns:
        PlaceholdersMetadataCollection: 구조화된 메타정보 컬렉션

    Raises:
        ValueError: 중복 Placeholder 감지 시

    Examples:
        >>> raw_placeholders = ["{{TITLE}}", "{{SUMMARY}}", "{{DATE}}"]
        >>> metadata = generate_placeholder_metadata(raw_placeholders)
        >>> print(metadata.total_count)
        3
        >>> print(metadata.required_count)
        2
    """
    # 중복 검사
    seen = set()
    for ph_key in raw_placeholders:
        if ph_key in seen:
            raise ValueError(
                f"중복된 Placeholder 발견: {ph_key}. "
                "각 Placeholder는 템플릿에서 한 번만 정의되어야 합니다."
            )
        seen.add(ph_key)

    # 타입별 분류 규칙
    type_mapping = {
        "TITLE": "section_title",
        "SUMMARY": "section_content",
        "BACKGROUND": "section_content",
        "MAIN_CONTENT": "section_content",
        "CONCLUSION": "section_content",
        "DATE": "meta",
        "RISK": "section_content",
    }

    # 각 Placeholder의 메타정보 생성
    metadatas: List[PlaceholderMetadata] = []
    required_count = 0
    optional_count = 0

    for position, ph_key in enumerate(raw_placeholders):
        # 키 이름 추출 (예: "{{TITLE}}" -> "TITLE")
        ph_name = ph_key.replace("{{", "").replace("}}", "")

        # 타입 결정
        ph_type = type_mapping.get(ph_name, "section_content")

        # 필수 여부 (meta 타입 제외)
        is_required = ph_type != "meta"
        if is_required:
            required_count += 1
        else:
            optional_count += 1

        # display_name과 description 조회
        display_name = _get_display_name(ph_name, ph_type)
        description = _get_description(ph_name, {"type": ph_type})
        example_list = _get_examples(ph_name, {"type": ph_type})
        example_value = example_list[0] if example_list else None

        # 길이 제한 설정 (타입별)
        max_length = None
        min_length = None
        if ph_type == "section_title":
            max_length = 200
        elif ph_type == "section_content":
            min_length = 100
            max_length = 10000
        elif ph_type == "meta":
            max_length = 100

        # PlaceholderMetadata 객체 생성
        metadata = PlaceholderMetadata(
            name=ph_name,
            placeholder_key=ph_key,
            type=ph_type,
            required=is_required,
            position=position,
            max_length=max_length,
            min_length=min_length,
            description=description,
            example=example_value
        )

        metadatas.append(metadata)

    # PlaceholdersMetadataCollection 생성
    return PlaceholdersMetadataCollection(
        placeholders=metadatas,
        total_count=len(raw_placeholders),
        required_count=required_count,
        optional_count=optional_count
    )
