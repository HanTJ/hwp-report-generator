"""Markdown → HWPX 일괄 변환/검증 스크립트."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from DesktopApp.src.converter.engine import ConversionEngine, ConversionError, MissingDependencyError
from DesktopApp.src.converter.markdown_parser import MarkdownParser


def _resolve_markdown_files(target: Path, recursive: bool) -> List[Path]:
    if target.is_file():
        return [target]
    pattern = "**/*.md" if recursive else "*.md"
    return sorted(path for path in target.glob(pattern) if path.is_file())


def _convert_files(
    files: Sequence[Path],
    output_dir: Path,
    engine: ConversionEngine,
) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    successes: List[Path] = []
    failures: List[Tuple[Path, str]] = []
    for source in files:
        target = output_dir / f"{source.stem}.hwpx"
        try:
            engine.convert(source, target)
        except MissingDependencyError as exc:
            raise
        except ConversionError as exc:
            failures.append((source, str(exc)))
            print(f"[FAIL] {source}: {exc}")
        except Exception as exc:  # pragma: no cover - 보호적 로깅
            failures.append((source, str(exc)))
            print(f"[FAIL] {source}: {exc}")
        else:
            successes.append(target)
            print(f"[OK]  {target}")
    return successes, failures


def _dry_run_parse(files: Sequence[Path], parser: MarkdownParser) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    successes: List[Path] = []
    failures: List[Tuple[Path, str]] = []
    for source in files:
        try:
            parser.parse(source)
        except Exception as exc:
            failures.append((source, str(exc)))
            print(f"[FAIL] {source}: {exc}")
        else:
            successes.append(source)
            print(f"[OK]  {source}")
    return successes, failures


def run_batch(
    target: Path,
    output_dir: Path,
    recursive: bool,
    dry_run: bool,
) -> int:
    files = _resolve_markdown_files(target, recursive)
    if not files:
        print("지정한 경로에 Markdown 파일이 없습니다.")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        parser = MarkdownParser()
        successes, failures = _dry_run_parse(files, parser)
    else:
        engine = ConversionEngine()
        try:
            successes, failures = _convert_files(files, output_dir, engine)
        except MissingDependencyError as exc:
            print("pyhwpx 모듈 또는 한컴오피스가 준비되지 않았습니다.")
            print(f"세부 정보: {exc}")
            return 2

    print("\n=== 변환 요약 ===")
    print(f"성공: {len(successes)}건")
    print(f"실패: {len(failures)}건")
    if failures:
        print("\n실패 목록:")
        for source, reason in failures:
            print(f"- {source}: {reason}")
        return 1
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Markdown 파일을 일괄 변환하거나 파싱 검증합니다.")
    parser.add_argument("target", type=Path, help="변환 대상 Markdown 파일 또는 디렉터리")
    parser.add_argument(
        "-o",
        "--output",
        default=Path("./hwpx-output"),
        type=Path,
        help="변환 결과를 저장할 디렉터리 (기본: ./hwpx-output)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="디렉터리 지정 시 하위 폴더까지 재귀적으로 검색합니다.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="pyhwpx 변환 대신 Markdown 파싱만 수행해 문법 오류를 검출합니다.",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    return run_batch(args.target, args.output, args.recursive, args.dry_run)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
