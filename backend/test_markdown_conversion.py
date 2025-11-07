"""
Markdown to HWPX 변환 테스트 스크립트

기존 report.md 파일을 읽어서 강화된 markdown_parser.py의
markdown_to_plain_text() 함수를 통해 변환한 후 HWPX 파일을 생성합니다.
"""
import os
import sys
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.utils.markdown_parser import parse_markdown_to_content
from app.utils.hwp_handler import HWPHandler


def main():
    """테스트 메인 함수"""

    # 1. 경로 설정
    md_file_path = r"D:\WorkSpace\hwp-report\hwp-report-generator\backend\artifacts\6\v1\report.md"
    template_path = r"D:\WorkSpace\hwp-report\hwp-report-generator\backend\templates\report_template.hwpx"
    output_dir = r"D:\WorkSpace\hwp-report\hwp-report-generator\backend\artifacts\6\v1"
    output_filename = "report_converted_test.hwpx"

    print("=" * 80)
    print("Markdown → HWPX 변환 테스트")
    print("=" * 80)
    print(f"\n입력 파일: {md_file_path}")
    print(f"템플릿: {template_path}")
    print(f"출력 디렉토리: {output_dir}")
    print(f"출력 파일명: {output_filename}\n")

    # 2. Markdown 파일 읽기
    print("1단계: Markdown 파일 읽기...")
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        print(f"   ✅ 성공 (파일 크기: {len(md_text)} bytes)")
    except FileNotFoundError:
        print(f"   ❌ 실패: 파일을 찾을 수 없습니다: {md_file_path}")
        return
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return

    # 3. Markdown 파싱 (markdown_to_plain_text 적용)
    print("\n2단계: Markdown 파싱 (문법 제거 및 들여쓰기 적용)...")
    try:
        content = parse_markdown_to_content(md_text)
        print("   ✅ 성공")
        print(f"   - 제목: {content.get('title', 'N/A')[:50]}...")
        print(f"   - 요약 섹션 제목: {content.get('title_summary', 'N/A')}")
        print(f"   - 배경 섹션 제목: {content.get('title_background', 'N/A')}")
        print(f"   - 주요내용 섹션 제목: {content.get('title_main_content', 'N/A')}")
        print(f"   - 결론 섹션 제목: {content.get('title_conclusion', 'N/A')}")

        # 변환된 내용 샘플 출력
        print("\n   [변환된 내용 샘플 - 요약 섹션 첫 200자]")
        summary_sample = content.get('summary', '')[:200]
        print(f"   {summary_sample}...")

    except Exception as e:
        print(f"   ❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. HWPX 생성
    print("\n3단계: HWPX 파일 생성...")
    try:
        handler = HWPHandler(
            template_path=template_path,
            temp_dir=os.path.join(output_dir, "temp"),
            output_dir=output_dir
        )

        output_path = handler.generate_report(content, output_filename)
        print(f"   ✅ 성공: {output_path}")

        # 파일 크기 확인
        file_size = os.path.getsize(output_path)
        print(f"   - 파일 크기: {file_size:,} bytes")

    except Exception as e:
        print(f"   ❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. 완료
    print("\n" + "=" * 80)
    print("✅ 변환 완료!")
    print("=" * 80)
    print(f"\n생성된 파일을 한글 워드프로세서로 열어서 확인하세요:")
    print(f"→ {output_path}")
    print("\n확인 사항:")
    print("  1. Markdown 문법(###, **, *, _)이 제거되었는지 확인")
    print("  2. 문단 들여쓰기(2칸 공백)가 적용되었는지 확인")
    print("  3. 순서 있는 목록(1., 2.)이 유지되었는지 확인")
    print("  4. 줄바꿈이 올바르게 표시되는지 확인")
    print()


if __name__ == "__main__":
    main()
