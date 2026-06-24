"""
보고서 관련 API 라우터
"""
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from models.report import ReportCreate, ReportResponse, ReportListResponse
from models.token_usage import TokenUsageCreate
from database.report_db import ReportDB
from database.token_usage_db import TokenUsageDB
from utils.auth import get_current_active_user
from utils.claude_client import ClaudeClient
from utils.hwp_handler import HWPHandler

router = APIRouter(prefix="/api/reports", tags=["보고서"])

TEMPLATE_PATH = "templates/report_template.hwpx"


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportCreate,
    current_user = Depends(get_current_active_user)
):
    """
    보고서 생성 API

    - 로그인한 사용자만 접근 가능
    - 토큰 사용량 자동 기록
    """
    try:
        # Claude 클라이언트 초기화
        claude_client = ClaudeClient()

        # 보고서 내용 생성
        content = claude_client.generate_report(request.topic)

        # 토큰 사용량 추출 (Claude API 응답에서)
        # Note: anthropic SDK의 Message 객체에서 usage 정보 가져오기
        # 실제 구현 시 claude_client에서 usage 정보를 반환하도록 수정 필요

        # HWP 파일 생성
        hwp_handler = HWPHandler(
            template_path=TEMPLATE_PATH,
            temp_dir="temp",
            output_dir="output"
        )

        output_path = hwp_handler.generate_report(content)
        filename = os.path.basename(output_path)
        file_size = os.path.getsize(output_path)

        # 데이터베이스에 보고서 정보 저장
        report = ReportDB.create_report(
            user_id=current_user.id,
            topic=request.topic,
            title=content.get("title", request.topic),
            filename=filename,
            file_path=output_path,
            file_size=file_size
        )

        # 토큰 사용량 기록 (임시값 - 실제로는 Claude API 응답에서 가져와야 함)
        # TODO: ClaudeClient를 수정하여 usage 정보를 반환하도록 개선
        input_tokens = getattr(claude_client, 'last_input_tokens', 0)
        output_tokens = getattr(claude_client, 'last_output_tokens', 0)
        total_tokens = input_tokens + output_tokens

        if total_tokens > 0:
            token_usage = TokenUsageCreate(
                user_id=current_user.id,
                report_id=report.id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens
            )
            TokenUsageDB.create_token_usage(token_usage)

        return ReportResponse(
            id=report.id,
            user_id=report.user_id,
            topic=report.topic,
            title=report.title,
            filename=report.filename,
            file_size=report.file_size,
            created_at=report.created_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/my-reports", response_model=ReportListResponse)
async def get_my_reports(current_user = Depends(get_current_active_user)):
    """
    내 보고서 목록 조회

    - 현재 로그인한 사용자가 생성한 보고서만 조회
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
            )
            for r in reports
        ]

        return ReportListResponse(
            total=len(report_responses),
            reports=report_responses
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"보고서 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    current_user = Depends(get_current_active_user)
):
    """
    보고서 다운로드

    - 본인이 생성한 보고서만 다운로드 가능
    """
    try:
        # 보고서 조회
        report = ReportDB.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")

        # 소유권 확인
        if report.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="본인이 생성한 보고서만 다운로드할 수 있습니다."
            )

        # 파일 존재 확인
        if not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

        return FileResponse(
            path=report.file_path,
            filename=report.filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파일 다운로드 중 오류가 발생했습니다: {str(e)}"
        )
