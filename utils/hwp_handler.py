"""
HWP 파일 처리 모듈
HWPX 형식 파일을 열고, 내용을 수정하고, 저장하는 기능 제공
"""
import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict


class HWPHandler:
    """HWPX 파일을 처리하는 핸들러 클래스"""

    def __init__(self, template_path: str, temp_dir: str = "temp", output_dir: str = "output"):
        """
        HWP 핸들러 초기화

        Args:
            template_path: HWPX 템플릿 파일 경로
            temp_dir: 임시 파일 디렉토리
            output_dir: 출력 파일 디렉토리
        """
        self.template_path = template_path
        self.temp_dir = temp_dir
        self.output_dir = output_dir

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, content: Dict[str, str], output_filename: str = None) -> str:
        """
        템플릿을 기반으로 보고서를 생성합니다.

        Args:
            content: 보고서 내용 딕셔너리
                - title: 제목
                - summary: 요약
                - background: 배경
                - main_content: 주요 내용
                - conclusion: 결론
            output_filename: 출력 파일명 (없으면 자동 생성)

        Returns:
            str: 생성된 파일 경로
        """
        # 출력 파일명 생성
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"report_{timestamp}.hwpx"

        output_path = os.path.join(self.output_dir, output_filename)

        # 임시 작업 디렉토리 생성
        work_dir = os.path.join(self.temp_dir, f"work_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(work_dir, exist_ok=True)

        try:
            # 1. HWPX 파일 압축 해제
            self._extract_hwpx(self.template_path, work_dir)

            # 2. 내용 치환
            self._replace_content(work_dir, content)

            # 3. 다시 압축
            self._compress_to_hwpx(work_dir, output_path)

            return output_path

        finally:
            # 임시 디렉토리 정리
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)

    def _extract_hwpx(self, hwpx_path: str, extract_dir: str):
        """
        HWPX 파일을 압축 해제합니다.

        Args:
            hwpx_path: HWPX 파일 경로
            extract_dir: 압축 해제 디렉토리
        """
        with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

    def _replace_content(self, work_dir: str, content: Dict[str, str]):
        """
        압축 해제된 HWPX의 XML 파일에서 플레이스홀더를 실제 내용으로 치환합니다.

        Args:
            work_dir: 작업 디렉토리
            content: 치환할 내용
        """
        # 현재 날짜 추가
        content["date"] = datetime.now().strftime("%Y년 %m월 %d일")

        # Contents 디렉토리 내의 모든 XML 파일 처리
        contents_dir = os.path.join(work_dir, "Contents")
        if not os.path.exists(contents_dir):
            raise FileNotFoundError("Contents 디렉토리를 찾을 수 없습니다.")

        # 플레이스홀더 매핑
        placeholders = {
            "{{TITLE}}": content.get("title", ""),
            "{{SUMMARY}}": content.get("summary", ""),
            "{{BACKGROUND}}": content.get("background", ""),
            "{{MAIN_CONTENT}}": content.get("main_content", ""),
            "{{CONCLUSION}}": content.get("conclusion", ""),
            "{{DATE}}": content.get("date", "")
        }

        # 모든 XML 파일 순회
        for root_dir, dirs, files in os.walk(contents_dir):
            for filename in files:
                if filename.endswith('.xml'):
                    file_path = os.path.join(root_dir, filename)
                    self._replace_in_file(file_path, placeholders)

    def _replace_in_file(self, file_path: str, placeholders: Dict[str, str]):
        """
        파일 내용에서 플레이스홀더를 치환합니다.

        Args:
            file_path: 파일 경로
            placeholders: 치환할 플레이스홀더 딕셔너리
        """
        try:
            # 파일을 텍스트로 읽어서 치환 (XML 파싱 대신 단순 텍스트 치환)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 플레이스홀더 치환
            modified = False
            for placeholder, value in placeholders.items():
                if placeholder in content:
                    # 줄바꿈을 XML 형식에 맞게 변환
                    value_formatted = self._format_for_hwp(value)
                    content = content.replace(placeholder, value_formatted)
                    modified = True

            # 변경사항이 있으면 파일에 쓰기
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        except Exception as e:
            # XML 파싱 에러는 무시 (바이너리 파일일 수 있음)
            pass

    def _format_for_hwp(self, text: str) -> str:
        """
        텍스트를 HWP XML 형식에 맞게 포맷팅합니다.

        Args:
            text: 원본 텍스트

        Returns:
            str: 포맷팅된 텍스트
        """
        # 특수 문자 이스케이프
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')

        return text

    def _compress_to_hwpx(self, work_dir: str, output_path: str):
        """
        작업 디렉토리를 HWPX 파일로 압축합니다.

        Args:
            work_dir: 작업 디렉토리
            output_path: 출력 HWPX 파일 경로
        """
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(work_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, work_dir)
                    zipf.write(file_path, arcname)

    def create_simple_template(self, output_path: str):
        """
        간단한 HWPX 템플릿을 생성합니다.
        (실제 한글 프로그램이 없을 때 테스트용으로 사용)

        Args:
            output_path: 출력 템플릿 경로
        """
        work_dir = os.path.join(self.temp_dir, "template_creation")
        os.makedirs(work_dir, exist_ok=True)

        try:
            # 기본 HWPX 구조 생성
            self._create_hwpx_structure(work_dir)

            # 압축
            self._compress_to_hwpx(work_dir, output_path)

        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)

    def _create_hwpx_structure(self, work_dir: str):
        """
        기본 HWPX 파일 구조를 생성합니다.

        Args:
            work_dir: 작업 디렉토리
        """
        # Contents 디렉토리 생성
        contents_dir = os.path.join(work_dir, "Contents")
        os.makedirs(contents_dir, exist_ok=True)

        # section0.xml 생성 (메인 문서)
        section_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<section>
    <p>
        <text>제목: {{TITLE}}</text>
    </p>
    <p>
        <text>작성일: {{DATE}}</text>
    </p>
    <p>
        <text>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</text>
    </p>
    <p>
        <text>1. 요약</text>
    </p>
    <p>
        <text>{{SUMMARY}}</text>
    </p>
    <p>
        <text>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</text>
    </p>
    <p>
        <text>2. 배경 및 목적</text>
    </p>
    <p>
        <text>{{BACKGROUND}}</text>
    </p>
    <p>
        <text>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</text>
    </p>
    <p>
        <text>3. 주요 내용</text>
    </p>
    <p>
        <text>{{MAIN_CONTENT}}</text>
    </p>
    <p>
        <text>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</text>
    </p>
    <p>
        <text>4. 결론 및 제언</text>
    </p>
    <p>
        <text>{{CONCLUSION}}</text>
    </p>
</section>"""

        section_path = os.path.join(contents_dir, "section0.xml")
        with open(section_path, 'w', encoding='utf-8') as f:
            f.write(section_content)

        # version.xml 생성
        version_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<version>5.0.0.0</version>"""

        with open(os.path.join(work_dir, "version.xml"), 'w', encoding='utf-8') as f:
            f.write(version_content)
