"""
standard_report.py

- 표준 스펙(ReportSpec) 정의
- 스펙 기반 데이터 검증
- HWPX 템플릿 기반 렌더러 (section0.xml 수정)
- create_table() 포함
"""

from __future__ import annotations

import os
import shutil
import zipfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import xml.etree.ElementTree as ET

# ============================================================
# 1. Spec Models
# ============================================================

FieldType = Literal["string", "int", "float", "date", "code", "boolean"]


@dataclass
class FieldSpec:
    name: str
    label: str
    type: FieldType
    required: bool = True
    max_length: Optional[int] = None
    code_list: Optional[List[str]] = None
    description: str = ""


@dataclass
class ColumnSpec:
    name: str
    label: str
    type: FieldType = "string"
    required: bool = False
    width: Optional[int] = None
    description: str = ""


@dataclass
class TableSpec:
    id: str                 # 섹션 내 key 및 논리 ID
    title: str
    description: str = ""
    columns: List[ColumnSpec] = field(default_factory=list)
    min_rows: int = 0
    max_rows: Optional[int] = None


@dataclass
class SectionSpec:
    id: str
    title: str
    description: str = ""
    fields: List[FieldSpec] = field(default_factory=list)
    tables: List[TableSpec] = field(default_factory=list)


@dataclass
class ReportSpec:
    id: str
    title: str
    version: str
    description: str = ""
    sections: List[SectionSpec] = field(default_factory=list)

    def get_section(self, section_id: str) -> SectionSpec:
        for s in self.sections:
            if s.id == section_id:
                return s
        raise KeyError(f"Section not found: {section_id}")


# ============================================================
# 2. 실제 표준에 맞춘 ReportSpec 예시
#    (※ 여기 항목명은 링크의 표준 구조를 가정한 예시이므로,
#       네가 가진 PDF의 실제 필드/테이블 정의로 치환하면 된다.)
# ============================================================

def build_standard_report_spec() -> ReportSpec:
    """
    링크의 표준 문서가 요구하는 구조를 코드로 모델링한 예시.

    예시 구조:
      - 섹션 basic_info: 기관/작성일/보고 번호 등 메타 정보
      - 섹션 summary: 개요/목적
      - 섹션 detail_table: 규격에 맞는 주요 항목 테이블
    """

    basic_info = SectionSpec(
        id="basic_info",
        title="기본 정보",
        description="표준 양식 상단 메타 정보",
        fields=[
            FieldSpec(
                name="reportTitle",
                label="보고서 제목",
                type="string",
                required=True,
                max_length=200,
                description="표준에서 정의한 공식 문서 제목 또는 과업 명칭"
            ),
            FieldSpec(
                name="organizationName",
                label="기관명",
                type="string",
                required=True,
                max_length=100,
                description="작성 주체 기관/회사명"
            ),
            FieldSpec(
                name="writerName",
                label="작성자",
                type="string",
                required=True,
                max_length=50,
            ),
            FieldSpec(
                name="reportDate",
                label="작성일자",
                type="date",
                required=True,
                description="YYYY-MM-DD 형식"
            ),
            FieldSpec(
                name="referenceStandard",
                label="적용 표준 번호",
                type="string",
                required=True,
                max_length=50,
                description="해당 링크의 국가표준 번호"
            ),
        ],
    )

    summary = SectionSpec(
        id="summary",
        title="요약 및 목적",
        fields=[
            FieldSpec(
                name="purpose",
                label="목적",
                type="string",
                required=True,
                description="표준 문서에서 요구하는 보고 목적 기술"
            ),
            FieldSpec(
                name="scope",
                label="적용 범위",
                type="string",
                required=False,
                description="해당 보고가 적용되는 범위/대상"
            ),
        ],
    )

    detail_table = SectionSpec(
        id="detail_table",
        title="주요 항목 테이블",
        description="표준에서 정의한 항목/측정값/판정 결과를 테이블로 기재",
        tables=[
            TableSpec(
                id="items",
                title="세부 항목",
                description="표준 양식의 본문 표 구조",
                min_rows=1,
                max_rows=None,
                columns=[
                    ColumnSpec(
                        name="seq",
                        label="No.",
                        type="int",
                        required=True,
                        description="일련번호"
                    ),
                    ColumnSpec(
                        name="itemName",
                        label="항목명",
                        type="string",
                        required=True,
                        description="표준에서 정의한 검사/평가 항목명"
                    ),
                    ColumnSpec(
                        name="specValue",
                        label="기준값",
                        type="string",
                        required=False,
                        description="관련 규격상의 기준값"
                    ),
                    ColumnSpec(
                        name="measuredValue",
                        label="측정값",
                        type="string",
                        required=False,
                        description="실제 측정 결과"
                    ),
                    ColumnSpec(
                        name="judgement",
                        label="판정",
                        type="code",
                        required=False,
                        description="예: 적합/부적합 또는 표준 코드값",
                    ),
                    ColumnSpec(
                        name="remarks",
                        label="비고",
                        type="string",
                        required=False,
                    ),
                ],
            )
        ],
    )

    return ReportSpec(
        id="STD-REPORT-001",
        title="표준 양식 기반 보고서",
        version="1.0.0",
        description="standard.go.kr 링크 표준 양식을 기반으로 한 HWPX 자동 생성용 스펙",
        sections=[basic_info, summary, detail_table],
    )


# ============================================================
# 3. Validation
# ============================================================

class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


def _validate_type(ftype: FieldType, value: Any) -> bool:
    if value is None:
        return True
    if ftype == "string":
        return isinstance(value, str)
    if ftype == "int":
        return isinstance(value, int)
    if ftype == "float":
        return isinstance(value, (int, float))
    if ftype == "boolean":
        return isinstance(value, bool)
    if ftype == "date":
        # 간단 체크: "YYYY-MM-DD"
        if not isinstance(value, str):
            return False
        parts = value.split("-")
        return len(parts) == 3 and all(p.isdigit() for p in parts)
    if ftype == "code":
        # 별도 code_list로 검증
        return isinstance(value, str)
    return True


def validate_report_data(spec: ReportSpec, data: Dict[str, Any]) -> None:
    errors: List[str] = []

    for section in spec.sections:
        section_data = data.get(section.id, {})
        section_path = f"sections.{section.id}"

        # fields
        for f in section.fields:
            value = section_data.get(f.name)
            path = f"{section_path}.{f.name}"

            if value is None:
                if f.required:
                    errors.append(f"{path}: 필수값 누락")
                continue

            if not _validate_type(f.type, value):
                errors.append(f"{path}: 타입 불일치 (기대: {f.type})")

            if f.max_length and isinstance(value, str) and len(value) > f.max_length:
                errors.append(f"{path}: 최대 길이 {f.max_length} 초과")

            if f.code_list and value not in f.code_list:
                errors.append(f"{path}: 허용되지 않은 코드값 '{value}'")

        # tables
        for t in section.tables:
            rows = section_data.get(t.id)
            t_path = f"{section_path}.{t.id}"

            if rows is None:
                if t.min_rows > 0:
                    errors.append(f"{t_path}: 최소 {t.min_rows}행 필요 (데이터 없음)")
                continue

            if not isinstance(rows, list):
                errors.append(f"{t_path}: 리스트 형식이어야 합니다.")
                continue

            if t.min_rows and len(rows) < t.min_rows:
                errors.append(f"{t_path}: 최소 {t.min_rows}행 필요 (현재 {len(rows)}행)")
            if t.max_rows and len(rows) > t.max_rows:
                errors.append(f"{t_path}: 최대 {t.max_rows}행 초과 (현재 {len(rows)}행)")

            col_map = {c.name: c for c in t.columns}
            for i, row in enumerate(rows):
                if not isinstance(row, dict):
                    errors.append(f"{t_path}[{i}]: dict 형식이어야 합니다.")
                    continue
                for col in t.columns:
                    v = row.get(col.name)
                    c_path = f"{t_path}[{i}].{col.name}"
                    if v is None:
                        if col.required:
                            errors.append(f"{c_path}: 필수값 누락")
                        continue
                    if not _validate_type(col.type, v):
                        errors.append(f"{c_path}: 타입 불일치 (기대: {col.type})")

    if errors:
        raise ValidationError(errors)


# ============================================================
# 4. HWPX Renderer with create_table()
# ============================================================

class HwpxRenderer:
    """
    HWPX 템플릿(section0.xml)을 기반으로,
    ReportSpec + 데이터에 맞춰 본문을 구성하는 렌더러.

    전제:
      - 템플릿 HWPX에 Contents/section0.xml 존재
      - body/section 끝에 우리가 만든 문단/표를 append
    """

    def __init__(self, template_path: Path):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"HWPX 템플릿 없음: {self.template_path}")

    def render(self, spec: ReportSpec, data: Dict[str, Any], output_path: Path) -> Path:
        # temp 작업 폴더
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            work_hwpx = tmpdir / "work.hwpx"
            shutil.copy2(self.template_path, work_hwpx)

            with zipfile.ZipFile(work_hwpx, "r") as zf:
                zf.extractall(tmpdir)

            section_xml_path = tmpdir / "Contents" / "section0.xml"
            if not section_xml_path.exists():
                raise FileNotFoundError("Contents/section0.xml 을 찾을 수 없습니다.")

            tree = ET.parse(section_xml_path)
            root = tree.getroot()

            # HWPX 네임스페이스 (필요 시 커스터마이징)
            # 실제 템플릿의 루트에서 nsmap 추출하여 맞춰주는게 베스트.
            ns = {
                "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
            }

            # 가장 단순하게: 루트 하위 마지막 section/body 에 append
            # 템플릿 구조에 맞게 수정 필요
            body = root

            # 섹션별로 문단/테이블 생성
            for section in spec.sections:
                sdata = data.get(section.id, {})

                # 섹션 제목
                self.create_paragraph(
                    parent=body,
                    text=f"{section.title}",
                    style_id="Heading1"
                )

                # 필드들은 '라벨: 값' 한 줄씩
                for f in section.fields:
                    value = sdata.get(f.name)
                    if value is not None:
                        text = f"{f.label}: {value}"
                        self.create_paragraph(
                            parent=body,
                            text=text,
                            style_id="BodyText"
                        )

                # 테이블들
                for t in section.tables:
                    rows = sdata.get(t.id, [])
                    if not rows:
                        continue
                    self.create_paragraph(
                        parent=body,
                        text=t.title,
                        style_id="Heading2"
                    )
                    self.create_table(
                        parent=body,
                        table_spec=t,
                        rows=rows,
                    )

            # XML 저장
            tree.write(section_xml_path, encoding="utf-8", xml_declaration=True)

            # 다시 hwpx로 압축
            output_path = Path(output_path)
            if output_path.exists():
                output_path.unlink()

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root_dir, _, files in os.walk(tmpdir):
                    for f in files:
                        full_path = Path(root_dir) / f
                        rel_path = full_path.relative_to(tmpdir)
                        # 임시 work.hwpx는 제외
                        if full_path == work_hwpx:
                            continue
                        zf.write(full_path, rel_path.as_posix())

        return output_path

    # --------------------------------------------------------
    # 4-1. Paragraph 생성 (아주 단순화 버전)
    # --------------------------------------------------------

    def create_paragraph(self, parent: ET.Element, text: str, style_id: str = "BodyText"):
        """
        매우 단순화된 HWPX 문단 생성.
        실제로는 템플릿의 <hp:pPr> 구조에 맞게 style-id 설정하는게 좋다.
        """
        hp_ns = "http://www.hancom.co.kr/hwpml/2011/paragraph"

        p = ET.SubElement(parent, f"{{{hp_ns}}}p")
        pPr = ET.SubElement(p, f"{{{hp_ns}}}pPr")
        # 스타일 참조 (필요 시 template 내 스타일 ID와 맞추기)
        ET.SubElement(pPr, f"{{{hp_ns}}}styleRef", attrib={"id": style_id})

        run = ET.SubElement(p, f"{{{hp_ns}}}run")
        text_el = ET.SubElement(run, f"{{{hp_ns}}}text")
        text_el.text = text

        return p

    # --------------------------------------------------------
    # 4-2. create_table(): 표준 스펙 기반 HWPX 테이블 생성
    # --------------------------------------------------------

    def create_table(self, parent: ET.Element, table_spec: TableSpec, rows: List[Dict[str, Any]]):
        """
        TableSpec + rows 기반으로 HWPX <tbl> 생성.

        - 첫 행: 컬럼 헤더
        - 이후: 데이터 행
        - HWPX의 실제 스타일/셀 속성은 템플릿에 맞게 조정 가능
        """
        hp_ns = "http://www.hancom.co.kr/hwpml/2011/paragraph"

        # <hp:tbl>
        tbl = ET.SubElement(parent, f"{{{hp_ns}}}tbl")

        # (선택) 테이블 속성
        tblPr = ET.SubElement(tbl, f"{{{hp_ns}}}tblPr")
        # 여기서 테두리, 정렬, 열 너비 등 설정 가능

        # 헤더 행
        tr_head = ET.SubElement(tbl, f"{{{hp_ns}}}tr")
        for col in table_spec.columns:
            tc = ET.SubElement(tr_head, f"{{{hp_ns}}}tc")
            p = ET.SubElement(tc, f"{{{hp_ns}}}p")
            run = ET.SubElement(p, f"{{{hp_ns}}}run")
            text_el = ET.SubElement(run, f"{{{hp_ns}}}text")
            text_el.text = col.label

        # 데이터 행
        for row in rows:
            tr = ET.SubElement(tbl, f"{{{hp_ns}}}tr")
            for col in table_spec.columns:
                value = row.get(col.name, "")
                # None 방지
                if value is None:
                    value = ""
                tc = ET.SubElement(tr, f"{{{hp_ns}}}tc")
                p = ET.SubElement(tc, f"{{{hp_ns}}}p")
                run = ET.SubElement(p, f"{{{hp_ns}}}run")
                text_el = ET.SubElement(run, f"{{{hp_ns}}}text")
                text_el.text = str(value)

        return tbl


# ============================================================
# 5. High-level Service
# ============================================================

class StandardReportService:
    def __init__(self, spec: ReportSpec, hwpx_template: Path):
        self.spec = spec
        self.renderer = HwpxRenderer(hwpx_template)

    def generate_hwpx(self, data: Dict[str, Any], output_path: Path) -> Path:
        validate_report_data(self.spec, data)
        return self.renderer.render(self.spec, data, output_path)


# ============================================================
# 6. 사용 예시
# ============================================================

if __name__ == "__main__":
    spec = build_standard_report_spec()
    service = StandardReportService(spec, Path("template.hwpx"))

    sample_data = {
        "basic_info": {
            "reportTitle": "표준 기반 자동 생성 보고서 예시",
            "organizationName": "주식회사 예시",
            "writerName": "홍길동",
            "reportDate": "2025-11-11",
            "referenceStandard": "KS XXXX:2025",
        },
        "summary": {
            "purpose": "해당 표준에 따른 결과를 체계적으로 보고하기 위함.",
            "scope": "본 프로젝트 수행 범위에 한정.",
        },
        "detail_table": {
            "items": [
                {
                    "seq": 1,
                    "itemName": "항목A",
                    "specValue": "기준 1.0 이하",
                    "measuredValue": "0.85",
                    "judgement": "적합",
                    "remarks": "",
                },
                {
                    "seq": 2,
                    "itemName": "항목B",
                    "specValue": "기준 10 이상",
                    "measuredValue": "9",
                    "judgement": "부적합",
                    "remarks": "재검토 필요",
                },
            ]
        },
    }

    out = service.generate_hwpx(sample_data, Path("output_standard_report.hwpx"))
    print(f"생성 완료: {out}")
