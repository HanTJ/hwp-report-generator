"""
HWPX 파일 처리 핸들러 테스트
"""
import pytest
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from app.utils.hwp_handler import HWPHandler


def create_simple_hwpx_template(output_path: str):
    """테스트용 간단한 HWPX 템플릿 생성

    Args:
        output_path: HWPX 파일 생성 경로
    """
    with zipfile.ZipFile(output_path, 'w') as zf:
        # mimetype 파일 (압축 없이)
        zf.writestr('mimetype', 'application/hwp+zip', compress_type=zipfile.ZIP_STORED)

        # Contents/section0.xml (간단한 XML)
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
    <hp:p id="1" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>제목: {{TITLE}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="2" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>날짜: {{DATE}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="3" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{TITLE_BACKGROUND}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="4" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{BACKGROUND}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="5" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{TITLE_MAIN_CONTENT}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="6" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{MAIN_CONTENT}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="7" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{TITLE_CONCLUSION}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="8" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{CONCLUSION}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="9" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{TITLE_SUMMARY}}</hp:t>
        </hp:run>
    </hp:p>
    <hp:p id="10" paraPrIDRef="1" styleIDRef="1">
        <hp:run charPrIDRef="1">
            <hp:t>{{SUMMARY}}</hp:t>
        </hp:run>
    </hp:p>
</root>'''
        zf.writestr('Contents/section0.xml', xml_content)


@pytest.fixture
def simple_hwpx_template(temp_dir):
    """테스트용 간단한 HWPX 템플릿 fixture"""
    template_path = os.path.join(temp_dir, "test_template.hwpx")
    create_simple_hwpx_template(template_path)
    return template_path


@pytest.fixture
def sample_report_content():
    """테스트용 보고서 내용 fixture"""
    return {
        "title": "테스트 보고서",
        "title_background": "배경",
        "background": "테스트 배경 내용입니다.",
        "title_main_content": "주요 내용",
        "main_content": "테스트 주요 내용입니다.",
        "title_conclusion": "결론",
        "conclusion": "테스트 결론입니다.",
        "title_summary": "요약",
        "summary": "테스트 요약입니다."
    }


@pytest.mark.unit
class TestHWPHandlerInit:
    """HWPHandler 초기화 테스트"""

    def test_init_success(self, simple_hwpx_template, temp_dir):
        """정상 초기화 테스트"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        assert handler.template_path == simple_hwpx_template
        assert handler.temp_dir == temp_work_dir
        assert handler.output_dir == output_dir

    def test_init_missing_template(self, temp_dir):
        """템플릿 파일 없을 시 에러"""
        non_existent_template = os.path.join(temp_dir, "non_existent.hwpx")

        with pytest.raises(FileNotFoundError):
            HWPHandler(
                template_path=non_existent_template,
                temp_dir=temp_dir,
                output_dir=temp_dir
            )

    def test_init_creates_directories(self, simple_hwpx_template, temp_dir):
        """출력/임시 디렉토리 자동 생성 확인"""
        output_dir = os.path.join(temp_dir, "output_new")
        temp_work_dir = os.path.join(temp_dir, "temp_new")

        # 디렉토리가 존재하지 않음
        assert not os.path.exists(output_dir)
        assert not os.path.exists(temp_work_dir)

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        # 디렉토리가 생성됨
        assert os.path.exists(output_dir)
        assert os.path.exists(temp_work_dir)


@pytest.mark.unit
class TestHWPHandlerGenerateReport:
    """보고서 생성 테스트"""

    def test_generate_report_success(self, simple_hwpx_template, temp_dir, sample_report_content):
        """보고서 생성 성공 테스트"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # 파일 생성 확인
        assert os.path.exists(output_path)
        assert output_path.endswith('.hwpx')
        assert os.path.getsize(output_path) > 0

    def test_generate_report_custom_filename(self, simple_hwpx_template, temp_dir, sample_report_content):
        """커스텀 파일명 지정"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        custom_filename = "custom_report.hwpx"
        output_path = handler.generate_report(sample_report_content, custom_filename)

        # 지정한 파일명으로 생성됨
        assert output_path.endswith(custom_filename)
        assert os.path.exists(output_path)

    def test_generate_report_auto_filename(self, simple_hwpx_template, temp_dir, sample_report_content):
        """자동 파일명 생성 (timestamp 포함)"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # report_{timestamp}.hwpx 형식
        filename = os.path.basename(output_path)
        assert filename.startswith("report_")
        assert filename.endswith(".hwpx")

    def test_generate_report_returns_path(self, simple_hwpx_template, temp_dir, sample_report_content):
        """생성된 파일 경로 반환 확인"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # 절대 경로 반환
        assert os.path.isabs(output_path)
        assert os.path.exists(output_path)


@pytest.mark.unit
class TestHWPHandlerReplaceContent:
    """플레이스홀더 치환 테스트"""

    def test_replace_content_all_placeholders(self, simple_hwpx_template, temp_dir, sample_report_content):
        """모든 플레이스홀더 치환 확인"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # 생성된 파일 내용 확인
        with zipfile.ZipFile(output_path, 'r') as zf:
            xml_content = zf.read('Contents/section0.xml').decode('utf-8')

            # 플레이스홀더가 치환되었는지 확인
            assert "{{TITLE}}" not in xml_content
            assert "{{BACKGROUND}}" not in xml_content
            assert "{{MAIN_CONTENT}}" not in xml_content
            assert "{{CONCLUSION}}" not in xml_content
            assert "{{SUMMARY}}" not in xml_content

            # 실제 내용이 들어갔는지 확인
            assert "테스트 보고서" in xml_content
            assert "테스트 배경 내용" in xml_content

    def test_replace_content_adds_date(self, simple_hwpx_template, temp_dir, sample_report_content):
        """날짜 자동 추가 확인"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # 생성된 파일에서 날짜 확인
        with zipfile.ZipFile(output_path, 'r') as zf:
            xml_content = zf.read('Contents/section0.xml').decode('utf-8')

            # {{DATE}} 플레이스홀더가 치환됨
            assert "{{DATE}}" not in xml_content
            # 날짜 형식 (년/월/일)이 포함됨
            assert "년" in xml_content


@pytest.mark.unit
class TestHWPHandlerFormatForHwp:
    """HWP XML 포맷팅 테스트"""

    def test_format_single_linebreak(self, simple_hwpx_template, temp_dir):
        """단일 줄바꿈을 <hp:lineBreak/> 태그로 변환"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        text = "첫 번째 줄\n두 번째 줄"
        formatted = handler._format_for_hwp(text)

        # 단일 줄바꿈은 <hp:lineBreak/> 태그로
        assert "<hp:lineBreak/>" in formatted

    def test_format_double_linebreak(self, simple_hwpx_template, temp_dir):
        """이중 줄바꿈을 새 문단으로 분리"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        text = "첫 번째 문단\n\n두 번째 문단"
        formatted = handler._format_for_hwp(text)

        # 이중 줄바꿈은 새 문단 태그로 분리
        assert "</hp:p>" in formatted
        assert "<hp:p" in formatted

    def test_format_xml_special_chars(self, simple_hwpx_template, temp_dir):
        """XML 특수문자 이스케이프 (&, <, >, ", ')"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        text = "특수문자: & < > \" '"
        formatted = handler._format_for_hwp(text)

        # XML 특수문자가 이스케이프됨
        assert "&amp;" in formatted
        assert "&lt;" in formatted
        assert "&gt;" in formatted
        assert "&quot;" in formatted or "&apos;" in formatted

    def test_format_empty_text(self, simple_hwpx_template, temp_dir):
        """빈 텍스트 처리"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        formatted = handler._format_for_hwp("")

        # 빈 문자열 반환
        assert formatted == ""


@pytest.mark.unit
class TestHWPHandlerCleanLinesegarray:
    """linesegarray 정리 테스트"""

    def test_clean_removes_linesegarray(self, simple_hwpx_template, temp_dir):
        """불완전한 linesegarray 제거 확인"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        content = """<hp:p>
    <hp:run><hp:t>테스트 내용</hp:t></hp:run>
    <hp:linesegarray>
        <hp:lineseg textpos="0" vertpos="0" linewidth="100"/>
    </hp:linesegarray>
</hp:p>"""

        cleaned = handler._clean_linesegarray(content)

        # linesegarray가 제거됨
        assert "<hp:linesegarray>" not in cleaned
        assert "</hp:linesegarray>" not in cleaned

    def test_clean_preserves_other_content(self, simple_hwpx_template, temp_dir):
        """다른 내용은 유지"""
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )

        content = """<hp:p>
    <hp:run><hp:t>테스트 내용</hp:t></hp:run>
    <hp:linesegarray>
        <hp:lineseg/>
    </hp:linesegarray>
</hp:p>"""

        cleaned = handler._clean_linesegarray(content)

        # 다른 태그와 내용은 유지
        assert "<hp:p>" in cleaned
        assert "<hp:run>" in cleaned
        assert "<hp:t>테스트 내용</hp:t>" in cleaned
        assert "</hp:run>" in cleaned
        assert "</hp:p>" in cleaned


@pytest.mark.integration
class TestHWPHandlerEndToEnd:
    """전체 플로우 통합 테스트"""

    def test_full_report_generation(self, simple_hwpx_template, temp_dir, sample_report_content):
        """전체 보고서 생성 플로우 테스트"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        # 1. 핸들러 초기화
        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        # 2. 보고서 생성
        output_path = handler.generate_report(sample_report_content, "test_report.hwpx")

        # 3. 파일 확인
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # 4. 내용 검증
        with zipfile.ZipFile(output_path, 'r') as zf:
            xml_content = zf.read('Contents/section0.xml').decode('utf-8')
            assert "테스트 보고서" in xml_content
            assert "{{TITLE}}" not in xml_content

    def test_generated_file_is_valid_hwpx(self, simple_hwpx_template, temp_dir, sample_report_content):
        """생성된 파일이 유효한 HWPX인지 확인"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # ZIP으로 열기 가능
        with zipfile.ZipFile(output_path, 'r') as zf:
            # 필수 파일들 존재
            file_list = zf.namelist()
            assert 'mimetype' in file_list
            assert 'Contents/section0.xml' in file_list

            # mimetype 내용 확인
            mimetype = zf.read('mimetype').decode('utf-8')
            assert mimetype == 'application/hwp+zip'

    def test_placeholders_replaced_in_generated_file(self, simple_hwpx_template, temp_dir, sample_report_content):
        """생성된 파일에 플레이스홀더가 실제로 치환되었는지 확인"""
        output_dir = os.path.join(temp_dir, "output")
        temp_work_dir = os.path.join(temp_dir, "temp")

        handler = HWPHandler(
            template_path=simple_hwpx_template,
            temp_dir=temp_work_dir,
            output_dir=output_dir
        )

        output_path = handler.generate_report(sample_report_content)

        # 모든 플레이스홀더가 치환되었는지 확인
        with zipfile.ZipFile(output_path, 'r') as zf:
            xml_content = zf.read('Contents/section0.xml').decode('utf-8')

            # 플레이스홀더가 남아있지 않음
            placeholders = [
                "{{TITLE}}", "{{DATE}}", "{{TITLE_BACKGROUND}}", "{{BACKGROUND}}",
                "{{TITLE_MAIN_CONTENT}}", "{{MAIN_CONTENT}}",
                "{{TITLE_CONCLUSION}}", "{{CONCLUSION}}",
                "{{TITLE_SUMMARY}}", "{{SUMMARY}}"
            ]

            for placeholder in placeholders:
                assert placeholder not in xml_content, f"Placeholder {placeholder} not replaced"
