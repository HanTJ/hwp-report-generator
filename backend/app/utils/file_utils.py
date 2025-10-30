"""
파일 처리 유틸리티

디렉토리 생성, 텍스트 쓰기, 해시 계산, 아티팩트 경로 구성 등을 제공합니다.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple

from shared.constants import ProjectPath
from shared.types.enums import ArtifactKind
from app.database.artifact_db import ArtifactDB


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(file_path: Path, text: str, encoding: str = "utf-8") -> int:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode(encoding)
    file_path.write_bytes(data)
    return len(data)


def sha256_of(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def next_artifact_version(topic_id: int, kind: ArtifactKind, locale: str = "ko") -> int:
    latest = ArtifactDB.get_latest_artifact_by_kind(topic_id, kind, locale)
    return (latest.version + 1) if latest else 1


def build_artifact_paths(topic_id: int, version: int, filename: str) -> Tuple[Path, Path]:
    """아티팩트 저장 디렉토리와 파일 전체 경로를 반환.

    구조: backend/artifacts/{topic_id}/v{version}/{filename}
    """
    base_dir = Path(ProjectPath.BACKEND) / "artifacts" / str(topic_id) / f"v{version}"
    file_path = base_dir / filename
    return base_dir, file_path

