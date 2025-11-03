"""
보고서 관련 API 라우터
"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.models.report import ReportCreate, ReportResponse
from app.models.token_usage import TokenUsageCreate
from app.database.report_db import ReportDB
from app.database.token_usage_db import TokenUsageDB
from app.utils.auth import get_current_active_user
from app.utils.claude_client import ClaudeClient
from app.utils.hwp_handler import HWPHandler
from app.utils.response_helper import success_response, error_response, ErrorCode

router = APIRouter(prefix="/api/reports", tags=["보고서"])

# Backend 디렉토리 설정 (PATH_PROJECT_HOME 환경 변수 기반)
_path_project_home = os.getenv("PATH_PROJECT_HOME")
if not _path_project_home:
    raise RuntimeError("PATH_PROJECT_HOME 환경 변수가 설정되지 않았습니다.")

BACKEND_DIR = Path(_path_project_home) / "backend"
TEMPLATE_PATH = str(BACKEND_DIR / "templates" / "report_template.hwpx")


# @router.post("/generate")
# async def generate_report(
#     request: ReportCreate,
#     current_user = Depends(get_current_active_user)
# ):
#     """보고서 생성 API.

#     로그인한 사용자만 접근 가능.
#     토큰 사용량 자동 기록.

#     Args:
#         request: 보고서 생성 요청 (토픽)
#         current_user: 현재 로그인한 사용자

#     Returns:
#         표준 API 응답 (생성된 보고서 정보)
#     """
#     try:
#         # Claude 클라이언트 초기화
#         claude_client = ClaudeClient()

#         # 보고서 내용 생성
#         content = claude_client.generate_report(request.topic)

#         # HWP 파일 생성
#         hwp_handler = HWPHandler(
#             template_path=TEMPLATE_PATH,
#             temp_dir=str(BACKEND_DIR / "temp"),
#             output_dir=str(BACKEND_DIR / "output")
#         )

#         output_path = hwp_handler.generate_report(content)
#         filename = os.path.basename(output_path)
#         file_size = os.path.getsize(output_path)

#         # 데이터베이스에 보고서 정보 저장
#         report = ReportDB.create_report(
#             user_id=current_user.id,
#             topic=request.topic,
#             title=content.get("title", request.topic),
#             filename=filename,
#             file_path=output_path,
#             file_size=file_size
#         )

#         # 토큰 사용량 기록
#         input_tokens = getattr(claude_client, 'last_input_tokens', 0)
#         output_tokens = getattr(claude_client, 'last_output_tokens', 0)
#         total_tokens = input_tokens + output_tokens

#         if total_tokens > 0:
#             token_usage = TokenUsageCreate(
#                 user_id=current_user.id,
#                 report_id=report.id,
#                 input_tokens=input_tokens,
#                 output_tokens=output_tokens,
#                 total_tokens=total_tokens
#             )
#             TokenUsageDB.create_token_usage(token_usage)

#         report_data = ReportResponse(
#             id=report.id,
#             user_id=report.user_id,
#             topic=report.topic,
#             title=report.title,
#             filename=report.filename,
#             file_size=report.file_size,
#             created_at=report.created_at
#         )

#         return success_response(report_data.dict())

#     except Exception as e:
#         return error_response(
#             code=ErrorCode.REPORT_GENERATION_FAILED,
#             http_status=500,
#             message="보고서 생성 중 오류가 발생했습니다.",
#             details={"error": str(e)}
#         )


@router.get("/my-reports")
async def get_my_reports(current_user = Depends(get_current_active_user)):
    """내 보고서 목록 조회.

    현재 로그인한 사용자가 생성한 보고서만 조회.

    Args:
        current_user: 현재 로그인한 사용자

    Returns:
        표준 API 응답 (보고서 목록)
    """
    try:
        reports = ReportDB.get_reports_by_user(current_user.id)

        report_responses = [
            ReportResponse(
                id=r.id,
                user_id=r.user_id,
                topic=r.topic,
                title=r.title,
                filename=r.filename,
                file_size=r.file_size,
                created_at=r.created_at
            ).dict()
            for r in reports
        ]

        return success_response({
            "total": len(report_responses),
            "reports": report_responses
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="보고서 목록 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    current_user = Depends(get_current_active_user)
):
    """보고서 다운로드.

    본인이 생성한 보고서만 다운로드 가능.
    관리자는 모든 보고서 다운로드 가능.

    Args:
        report_id: 다운로드할 보고서 ID
        current_user: 현재 로그인한 사용자

    Returns:
        FileResponse (HWPX 파일) 또는 표준 에러 응답
    """
    try:
        # 보고서 조회
        report = ReportDB.get_report_by_id(report_id)
        if not report:
            return error_response(
                code=ErrorCode.REPORT_NOT_FOUND,
                http_status=404,
                message="보고서를 찾을 수 없습니다."
            )

        # 소유권 확인
        if report.user_id != current_user.id and not current_user.is_admin:
            return error_response(
                code=ErrorCode.REPORT_UNAUTHORIZED,
                http_status=403,
                message="본인이 생성한 보고서만 다운로드할 수 있습니다."
            )

        # 파일 존재 확인
        if not os.path.exists(report.file_path):
            return error_response(
                code=ErrorCode.REPORT_FILE_NOT_FOUND,
                http_status=404,
                message="파일을 찾을 수 없습니다.",
                hint="파일이 삭제되었을 수 있습니다. 관리자에게 문의하세요."
            )

        return FileResponse(
            path=report.file_path,
            filename=report.filename,
            media_type="application/octet-stream"
        )

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="파일 다운로드 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
