"""
Artifact management API router.

Handles artifact retrieval, download, and conversion operations.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from typing import Optional
import os
import time
import shutil
from pathlib import Path

from app.models.user import User
from app.models.artifact import ArtifactResponse, ArtifactListResponse, ArtifactContentResponse, ArtifactCreate
from app.database.topic_db import TopicDB
from app.database.artifact_db import ArtifactDB
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from app.utils.hwp_handler import HWPHandler
from app.utils.markdown_parser import parse_markdown_to_content
from app.utils.file_utils import next_artifact_version, build_artifact_paths, sha256_of
from shared.types.enums import ArtifactKind
from shared.constants import ProjectPath

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


@router.get("/{artifact_id}", summary="Get artifact by ID")
async def get_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves artifact metadata by ID.

    Path Parameters:
        - artifact_id: Artifact ID

    Returns:
        Standard ApiResponse with ArtifactResponse data

    Error Codes:
        - ARTIFACT.NOT_FOUND: Artifact not found
        - TOPIC.UNAUTHORIZED: User does not own the parent topic

    Examples:
        Request: GET /api/artifacts/1

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "topic_id": 1,
            "message_id": 2,
            "kind": "md",
            "locale": "ko",
            "version": 1,
            "filename": "report_v1.md",
            "file_path": "artifacts/topics/1/messages/report_v1.md",
            "file_size": 2048,
            "created_at": "2025-10-28T10:30:20"
          },
          "error": null,
          "meta": {"requestId": "req_abc123"},
          "feedback": []
        }
        ```
    """
    artifact = ArtifactDB.get_artifact_by_id(artifact_id)
    if not artifact:
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트를 찾을 수 없습니다."
        )

    # Check ownership
    topic = TopicDB.get_topic_by_id(artifact.topic_id)
    if not topic or (topic.user_id != current_user.id and not current_user.is_admin):
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 아티팩트에 접근할 권한이 없습니다."
        )

    return success_response(ArtifactResponse.model_validate(artifact))


@router.get("/{artifact_id}/content", summary="Get artifact content")
async def get_artifact_content(
    artifact_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves artifact file content (for MD files).

    Path Parameters:
        - artifact_id: Artifact ID

    Returns:
        Standard ApiResponse with ArtifactContentResponse data

    Error Codes:
        - ARTIFACT.NOT_FOUND: Artifact not found
        - TOPIC.UNAUTHORIZED: User does not own the parent topic
        - ARTIFACT.INVALID_KIND: Only MD files can be read as text

    Note:
        This endpoint only supports MD files. For HWPX files, use the download endpoint.

    Examples:
        Request: GET /api/artifacts/1/content

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "artifact_id": 1,
            "content": "# 디지털뱅킹 트렌드 분석 보고서\\n\\n## 요약\\n...",
            "filename": "report_v1.md",
            "kind": "md"
          },
          "error": null,
          "meta": {"requestId": "req_def456"},
          "feedback": []
        }
        ```
    """
    artifact = ArtifactDB.get_artifact_by_id(artifact_id)
    if not artifact:
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트를 찾을 수 없습니다."
        )

    # Check ownership
    topic = TopicDB.get_topic_by_id(artifact.topic_id)
    if not topic or (topic.user_id != current_user.id and not current_user.is_admin):
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 아티팩트에 접근할 권한이 없습니다."
        )

    # Only support MD files for content reading
    if artifact.kind != ArtifactKind.MD:
        return error_response(
            code=ErrorCode.ARTIFACT_INVALID_KIND,
            http_status=400,
            message="MD 파일만 내용 조회가 가능합니다.",
            hint="HWPX 파일은 다운로드를 사용하세요."
        )

    try:
        # Read file content
        with open(artifact.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = ArtifactContentResponse(
            artifact_id=artifact.id,
            content=content,
            filename=artifact.filename,
            kind=artifact.kind
        )

        return success_response(result)

    except FileNotFoundError:
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트 파일을 찾을 수 없습니다.",
            details={"file_path": artifact.file_path}
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="아티팩트 내용 조회에 실패했습니다.",
            details={"error": str(e)}
        )


@router.get("/{artifact_id}/download", summary="Download artifact file")
async def download_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Downloads artifact file (MD, HWPX, etc.).

    Path Parameters:
        - artifact_id: Artifact ID

    Returns:
        File as attachment

    Error Codes:
        - ARTIFACT.NOT_FOUND: Artifact not found
        - TOPIC.UNAUTHORIZED: User does not own the parent topic
        - ARTIFACT.DOWNLOAD_FAILED: File download failed

    Examples:
        Request: GET /api/artifacts/2/download

        Response (200): File download with Content-Disposition header
    """
    artifact = ArtifactDB.get_artifact_by_id(artifact_id)
    if not artifact:
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트를 찾을 수 없습니다."
        )

    # Check ownership
    topic = TopicDB.get_topic_by_id(artifact.topic_id)
    if not topic or (topic.user_id != current_user.id and not current_user.is_admin):
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 아티팩트를 다운로드할 권한이 없습니다."
        )

    # Check file exists
    if not os.path.exists(artifact.file_path):
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트 파일을 찾을 수 없습니다.",
            details={"file_path": artifact.file_path}
        )

    try:
        # Determine media type
        media_types = {
            ArtifactKind.MD: "text/markdown",
            ArtifactKind.HWPX: "application/x-hwpx",
            ArtifactKind.PDF: "application/pdf"
        }
        media_type = media_types.get(artifact.kind, "application/octet-stream")

        return FileResponse(
            path=artifact.file_path,
            filename=artifact.filename,
            media_type=media_type
        )

    except Exception as e:
        return error_response(
            code=ErrorCode.ARTIFACT_DOWNLOAD_FAILED,
            http_status=500,
            message="파일 다운로드에 실패했습니다.",
            details={"error": str(e)}
        )


@router.get("/topics/{topic_id}", summary="Get artifacts by topic")
async def get_artifacts_by_topic(
    topic_id: int,
    kind: Optional[ArtifactKind] = None,
    locale: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves artifacts for a topic with optional filters.

    Path Parameters:
        - topic_id: Topic ID

    Query Parameters:
        - kind: Filter by artifact kind (md/hwpx/pdf) (optional)
        - locale: Filter by locale (ko/en) (optional)
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50, max: 100)

    Returns:
        Standard ApiResponse with ArtifactListResponse data

    Error Codes:
        - TOPIC.NOT_FOUND: Topic not found
        - TOPIC.UNAUTHORIZED: User does not own the topic

    Examples:
        Request: GET /api/artifacts/topics/1?kind=md&locale=ko&page=1&page_size=10

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "artifacts": [...],
            "total": 5,
            "topic_id": 1
          },
          "error": null,
          "meta": {"requestId": "req_ghi789"},
          "feedback": []
        }
        ```
    """
    # Check topic exists and user owns it
    topic = TopicDB.get_topic_by_id(topic_id)
    if not topic:
        return error_response(
            code=ErrorCode.TOPIC_NOT_FOUND,
            http_status=404,
            message="주제를 찾을 수 없습니다."
        )

    if topic.user_id != current_user.id and not current_user.is_admin:
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 주제의 아티팩트를 조회할 권한이 없습니다."
        )

    try:
        # Validate page_size
        if page_size > 100:
            page_size = 100

        offset = (page - 1) * page_size
        artifacts, total = ArtifactDB.get_artifacts_by_topic(
            topic_id=topic_id,
            kind=kind,
            locale=locale,
            limit=page_size,
            offset=offset
        )

        artifact_responses = [ArtifactResponse.model_validate(a) for a in artifacts]
        result = ArtifactListResponse(
            artifacts=artifact_responses,
            total=total,
            topic_id=topic_id
        )

        return success_response(result)

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="아티팩트 목록 조회에 실패했습니다.",
            details={"error": str(e)}
        )


@router.post("/{artifact_id}/convert", summary="Convert MD artifact to HWPX")
async def convert_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Converts MD artifact to HWPX format.

    Path Parameters:
        - artifact_id: Source MD artifact ID

    Returns:
        Standard ApiResponse with new HWPX ArtifactResponse data

    Error Codes:
        - ARTIFACT.NOT_FOUND: Artifact not found
        - ARTIFACT.INVALID_KIND: Source must be MD file
        - TOPIC.UNAUTHORIZED: User does not own the parent topic
        - ARTIFACT.CREATION_FAILED: Conversion failed

    Note:
        This endpoint will be implemented in Phase 6 with actual conversion logic.
        Currently returns a placeholder response.

    Examples:
        Request: POST /api/artifacts/1/convert

        Response (200):
        ```json
        {
          "success": true,
          "data": {
            "id": 2,
            "topic_id": 1,
            "message_id": 2,
            "kind": "hwpx",
            "locale": "ko",
            "version": 1,
            "filename": "report_v1.hwpx",
            "file_path": "artifacts/topics/1/messages/report_v1.hwpx",
            "file_size": 15360,
            "created_at": "2025-10-28T10:35:00"
          },
          "error": null,
          "meta": {"requestId": "req_jkl012"},
          "feedback": []
        }
        ```
    """
    artifact = ArtifactDB.get_artifact_by_id(artifact_id)
    if not artifact:
        return error_response(
            code=ErrorCode.ARTIFACT_NOT_FOUND,
            http_status=404,
            message="아티팩트를 찾을 수 없습니다."
        )

    # Check ownership
    topic = TopicDB.get_topic_by_id(artifact.topic_id)
    if not topic or (topic.user_id != current_user.id and not current_user.is_admin):
        return error_response(
            code=ErrorCode.TOPIC_UNAUTHORIZED,
            http_status=403,
            message="이 아티팩트를 변환할 권한이 없습니다."
        )

    # Validate source is MD
    if artifact.kind != ArtifactKind.MD:
        return error_response(
            code=ErrorCode.ARTIFACT_INVALID_KIND,
            http_status=400,
            message="MD 파일만 HWPX로 변환할 수 있습니다."
        )

    try:
        # 4. MD 파일 읽기
        md_file_path = Path(artifact.file_path)
        if not md_file_path.exists():
            return error_response(
                code=ErrorCode.ARTIFACT_NOT_FOUND,
                http_status=404,
                message="아티팩트 파일을 찾을 수 없습니다.",
                details={"file_path": str(md_file_path)}
            )

        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # 5. MD → content dict 변환
        content = parse_markdown_to_content(md_text)

        # 6. HWPX 생성 (HWPHandler 사용)
        template_path = ProjectPath.BACKEND / "templates" / "report_template.hwpx"
        if not template_path.exists():
            return error_response(
                code=ErrorCode.ARTIFACT_CONVERSION_FAILED,
                http_status=500,
                message="HWPX 템플릿 파일을 찾을 수 없습니다.",
                details={"template_path": str(template_path)},
                hint="backend/templates/report_template.hwpx 파일이 있는지 확인해주세요."
            )

        # 임시 디렉토리 설정
        temp_dir = ProjectPath.BACKEND / "temp"
        temp_dir.mkdir(exist_ok=True)

        # HWPHandler로 HWPX 생성
        hwp_handler = HWPHandler(
            template_path=str(template_path),
            temp_dir=str(temp_dir),
            output_dir=str(temp_dir)  # 임시로 temp에 저장
        )

        # 임시 HWPX 파일 생성
        temp_hwpx_filename = f"temp_{artifact_id}_{int(time.time())}.hwpx"
        temp_hwpx_path = hwp_handler.generate_report(content, temp_hwpx_filename)

        # 7. Artifact 저장 경로 생성
        version = next_artifact_version(artifact.topic_id, ArtifactKind.HWPX, artifact.locale)
        base_dir, hwpx_path = build_artifact_paths(
            artifact.topic_id,
            version,
            "report.hwpx"
        )

        # 8. HWPX 파일 이동
        shutil.move(temp_hwpx_path, hwpx_path)

        # 9. 파일 정보 계산
        file_size = hwpx_path.stat().st_size
        file_hash = sha256_of(hwpx_path)

        # 10. Artifact DB 레코드 생성
        hwpx_artifact = ArtifactDB.create_artifact(
            artifact.topic_id,
            artifact.message_id,  # 동일한 message에 연결
            ArtifactCreate(
                kind=ArtifactKind.HWPX,
                locale=artifact.locale,
                version=version,
                filename=hwpx_path.name,
                file_path=str(hwpx_path),
                file_size=file_size,
                sha256=file_hash
            )
        )

        # 11. 성공 응답
        return success_response({
            "artifact_id": hwpx_artifact.id,
            "kind": hwpx_artifact.kind,
            "filename": hwpx_artifact.filename,
            "file_path": hwpx_artifact.file_path,
            "file_size": hwpx_artifact.file_size,
            "created_at": hwpx_artifact.created_at.isoformat()
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.ARTIFACT_CONVERSION_FAILED,
            http_status=500,
            message="HWPX 변환 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
