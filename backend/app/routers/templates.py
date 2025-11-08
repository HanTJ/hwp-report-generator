"""Template management API router.

Handles template upload, retrieval, and deletion operations.
"""

import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List

from app.models.user import User
from app.models.template import (
    UploadTemplateResponse,
    TemplateListResponse,
    TemplateDetailResponse,
    AdminTemplateResponse,
    PlaceholderResponse,
)
from app.database.template_db import TemplateDB, PlaceholderDB
from app.database.user_db import UserDB
from app.models.template import TemplateCreate
from app.utils.auth import get_current_active_user
from app.utils.response_helper import success_response, error_response, ErrorCode
from app.utils.templates_manager import TemplatesManager
from app.utils.prompts import create_dynamic_system_prompt

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.get("/admin/templates", summary="List all templates (admin only)")
async def admin_list_templates(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """모든 사용자의 템플릿을 조회합니다 (관리자 전용).

    반환(Returns):
        전체 템플릿 목록 (사용자명 포함)

    에러 코드(Error Codes):
        - AUTH.UNAUTHORIZED: 관리자 권한 없음

    예시(Examples):
        요청(Request): GET /api/admin/templates

        응답(Response, 200):
        ```json
        {
          "success": true,
          "data": [
            {
              "id": 1,
              "title": "재무보고서 템플릿",
              "username": "user1",
              "file_size": 45678,
              "placeholder_count": 5,
              "created_at": "2025-11-06T10:30:00"
            },
            ...
          ],
          "error": null,
          "meta": {"requestId": "uuid"}
        }
        ```
    """
    try:
        # 관리자 권한 검증
        if not current_user.is_admin:
            return error_response(
                code=ErrorCode.AUTH_UNAUTHORIZED,
                http_status=403,
                message="관리자 권한이 필요합니다.",
                hint="관리자에게 문의해주세요."
            )

        # 모든 템플릿 조회
        templates = TemplateDB.list_all_templates()
        response_data = []

        for template in templates:
            # 사용자 정보 조회
            user = UserDB.get_user_by_id(template.user_id)
            username = user.username if user else "Unknown"

            # 플레이스홀더 개수 조회
            placeholders = PlaceholderDB.get_placeholders_by_template(template.id)
            placeholder_count = len(placeholders)

            response_data.append(
                AdminTemplateResponse(
                    id=template.id,
                    title=template.title,
                    username=username,
                    file_size=template.file_size,
                    placeholder_count=placeholder_count,
                    created_at=template.created_at
                )
            )

        return success_response(response_data)
    except Exception as e:
        print(f"Error in admin_list_templates: {str(e)}")
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="템플릿 목록 조회 중 오류가 발생했습니다."
        )


@router.post("", summary="Upload new template", status_code=201)
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """사용자가 커스텀 HWPX 템플릿을 업로드합니다.

    요청(Request):
        - file: HWPX 파일 (multipart/form-data)
        - title: 템플릿 제목 (string)

    반환(Returns):
        업로드된 템플릿 메타데이터와 플레이스홀더 목록

    에러 코드(Error Codes):
        - VALIDATION.INVALID_FORMAT: .hwpx 파일만 업로드 가능
        - TEMPLATE.INVALID_FORMAT: HWPX 파일이 손상됨
        - TEMPLATE.DUPLICATE_PLACEHOLDER: 플레이스홀더 중복
        - SERVER.INTERNAL_ERROR: 서버 오류

    예시(Examples):
        요청(Request):
        ```
        POST /api/templates
        Content-Type: multipart/form-data

        file: [binary HWPX file]
        title: "재무보고서 템플릿"
        ```

        응답(Response, 201):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "title": "재무보고서 템플릿",
            "filename": "template_20251106_123456.hwpx",
            "file_size": 45678,
            "placeholders": [
              {"key": "{{TITLE}}"},
              {"key": "{{SUMMARY}}"}
            ],
            "created_at": "2025-11-06T10:30:00"
          },
          "error": null,
          "meta": {"requestId": "uuid"}
        }
        ```
    """
    try:
        manager = TemplatesManager()

        # 1. 파일 확장자 검증
        if not file.filename.lower().endswith('.hwpx'):
            return error_response(
                code=ErrorCode.VALIDATION_INVALID_FORMAT,
                http_status=400,
                message=".hwpx 파일만 업로드 가능합니다.",
                hint="파일 형식을 확인해주세요."
            )

        # 2. 파일 내용 읽기
        file_content = await file.read()
        if not file_content:
            return error_response(
                code=ErrorCode.VALIDATION_INVALID_FORMAT,
                http_status=400,
                message="파일이 비어있습니다.",
                hint="유효한 HWPX 파일을 업로드해주세요."
            )

        # 3. HWPX 파일 검증 (Magic Byte)
        if not manager.validate_hwpx(file_content):
            return error_response(
                code=ErrorCode.TEMPLATE_INVALID_FORMAT,
                http_status=400,
                message="HWPX 파일이 손상되었습니다.",
                hint="파일을 다시 저장하거나 다른 파일을 시도해주세요."
            )

        # 4. 임시 파일 저장
        temp_filename = f"upload_{uuid.uuid4().hex}.hwpx"
        temp_file_path = manager.temp_dir / temp_filename
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)

        try:
            # 5. HWPX 압축 해제
            work_dir = manager.extract_hwpx(str(temp_file_path))

            try:
                # 6. 플레이스홀더 추출
                placeholders = manager.extract_placeholders(work_dir)
                placeholder_list = sorted(placeholders)

                # 7. 플레이스홀더 중복 검증
                if manager.has_duplicate_placeholders(placeholder_list):
                    duplicate_keys = manager.get_duplicate_placeholders(placeholder_list)
                    return error_response(
                        code=ErrorCode.TEMPLATE_DUPLICATE_PLACEHOLDER,
                        http_status=400,
                        message=f"플레이스홀더 {duplicate_keys[0]}이 중복되었습니다.",
                        details={"duplicate_keys": duplicate_keys},
                        hint="템플릿에서 중복된 플레이스홀더를 제거해주세요."
                    )

                # 8. SHA256 계산
                sha256 = manager.calculate_sha256(str(temp_file_path))

                # [신규] 9단계: 동적 System Prompt 생성
                # Placeholder 객체로부터 Placeholder 리스트 생성
                from app.models.template import Placeholder as PlaceholderModel
                placeholder_objects = [
                    PlaceholderModel(
                        id=i,
                        template_id=0,  # 임시값 (아직 template_id 없음)
                        placeholder_key=key,
                        created_at=datetime.now()
                    )
                    for i, key in enumerate(placeholder_list, start=1)
                ]
                prompt_system = create_dynamic_system_prompt(placeholder_objects)

                # prompt_user: placeholder 목록을 쉼표로 구분된 문자열로 저장
                prompt_user = ", ".join(placeholder_list)

                # [신규] 10단계: DB 트랜잭션으로 Template + Placeholders 원자적 저장
                template_data = TemplateCreate(
                    title=title,
                    description=None,
                    filename=file.filename,
                    file_path="",  # 임시값, 아래에서 업데이트
                    file_size=len(file_content),
                    sha256=sha256,
                    prompt_user=prompt_user,         # 신규: Placeholder 목록
                    prompt_system=prompt_system      # 신규: 생성된 System Prompt
                )

                # create_template_with_transaction: Template + Placeholder 원자적 저장
                template = TemplateDB.create_template_with_transaction(
                    current_user.id,
                    template_data,
                    placeholder_list
                )

                # [기존] 11단계: 최종 파일 저장 경로로 이동
                final_file_path = manager.save_template_file(
                    str(temp_file_path),
                    current_user.id,
                    template.id
                )

                # [기존] 12단계: 응답 생성
                placeholder_responses = [
                    PlaceholderResponse(key=key)
                    for key in placeholder_list
                ]

                response_data = UploadTemplateResponse(
                    id=template.id,
                    title=template.title,
                    filename=template.filename,
                    file_size=template.file_size,
                    placeholders=placeholder_responses,
                    prompt_user=template.prompt_user,         # 신규
                    prompt_system=template.prompt_system,     # 신규
                    created_at=template.created_at
                )

                return success_response(response_data.model_dump())

            finally:
                # 임시 파일 정리
                manager.cleanup_temp_files(work_dir)

        except Exception as e:
            # 압축 해제 실패 시 임시 파일 정리
            if temp_file_path.exists():
                temp_file_path.unlink()
            raise e

    except Exception as e:
        # 최종 오류 처리
        print(f"Error in upload_template: {str(e)}")
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="템플릿 업로드 중 오류가 발생했습니다.",
            hint="관리자에게 문의해주세요."
        )


@router.get("", summary="List user's templates")
async def list_templates(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """사용자의 템플릿 목록을 조회합니다.

    반환(Returns):
        사용자 소유 템플릿 목록

    예시(Examples):
        요청(Request): GET /api/templates

        응답(Response, 200):
        ```json
        {
          "success": true,
          "data": [
            {
              "id": 1,
              "title": "재무보고서 템플릿",
              "filename": "template_20251106_123456.hwpx",
              "file_size": 45678,
              "created_at": "2025-11-06T10:30:00"
            },
            {
              "id": 2,
              "title": "영업보고서 템플릿",
              "filename": "template_20251105_234567.hwpx",
              "file_size": 52341,
              "created_at": "2025-11-05T14:15:00"
            }
          ],
          "error": null,
          "meta": {"requestId": "uuid"}
        }
        ```
    """
    try:
        templates = TemplateDB.list_templates_by_user(current_user.id)
        response_data = [
            TemplateListResponse(
                id=t.id,
                title=t.title,
                filename=t.filename,
                file_size=t.file_size,
                created_at=t.created_at
            )
            for t in templates
        ]
        return success_response(response_data)
    except Exception as e:
        print(f"Error in list_templates: {str(e)}")
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="템플릿 목록 조회 중 오류가 발생했습니다."
        )


@router.get("/{template_id}", summary="Get template details")
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """템플릿 상세 정보를 조회합니다 (메타데이터 + 플레이스홀더).

    경로 파라미터(Path Parameters):
        - template_id: 조회할 템플릿 ID

    반환(Returns):
        템플릿 메타데이터와 플레이스홀더 목록

    에러 코드(Error Codes):
        - TEMPLATE.NOT_FOUND: 템플릿을 찾을 수 없음
        - TEMPLATE.UNAUTHORIZED: 접근 권한 없음

    예시(Examples):
        요청(Request): GET /api/templates/1

        응답(Response, 200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "title": "재무보고서 템플릿",
            "filename": "template_20251106_123456.hwpx",
            "file_size": 45678,
            "placeholders": [
              {"key": "{{TITLE}}"},
              {"key": "{{SUMMARY}}"},
              {"key": "{{BACKGROUND}}"},
              {"key": "{{MAIN_CONTENT}}"},
              {"key": "{{CONCLUSION}}"}
            ],
            "created_at": "2025-11-06T10:30:00"
          },
          "error": null,
          "meta": {"requestId": "uuid"}
        }
        ```
    """
    try:
        # 템플릿 조회 (권한 검증 포함)
        template = TemplateDB.get_template_by_id(template_id, current_user.id)

        if not template:
            return error_response(
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                http_status=404,
                message="템플릿을 찾을 수 없습니다.",
                hint="템플릿 ID를 확인해주세요."
            )

        # 플레이스홀더 조회
        placeholders = PlaceholderDB.get_placeholders_by_template(template.id)
        placeholder_responses = [
            PlaceholderResponse(key=p.placeholder_key)
            for p in placeholders
        ]

        response_data = TemplateDetailResponse(
            id=template.id,
            title=template.title,
            filename=template.filename,
            file_size=template.file_size,
            placeholders=placeholder_responses,
            created_at=template.created_at
        )

        return success_response(response_data)
    except Exception as e:
        print(f"Error in get_template: {str(e)}")
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="템플릿 조회 중 오류가 발생했습니다."
        )


@router.delete("/{template_id}", summary="Delete template")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """템플릿을 삭제합니다 (소프트 삭제).

    경로 파라미터(Path Parameters):
        - template_id: 삭제할 템플릿 ID

    반환(Returns):
        삭제 결과 메시지

    에러 코드(Error Codes):
        - TEMPLATE.NOT_FOUND: 템플릿을 찾을 수 없음
        - TEMPLATE.UNAUTHORIZED: 접근 권한 없음

    예시(Examples):
        요청(Request): DELETE /api/templates/1

        응답(Response, 200):
        ```json
        {
          "success": true,
          "data": {
            "id": 1,
            "message": "템플릿이 삭제되었습니다."
          },
          "error": null,
          "meta": {"requestId": "uuid"}
        }
        ```
    """
    try:
        # 권한 검증
        template = TemplateDB.get_template_by_id(template_id, current_user.id)
        if not template:
            return error_response(
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                http_status=404,
                message="템플릿을 찾을 수 없습니다."
            )

        # 삭제 (soft delete)
        success = TemplateDB.delete_template(template_id, current_user.id)
        if not success:
            return error_response(
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                http_status=404,
                message="템플릿을 찾을 수 없습니다."
            )

        return success_response({
            "id": template_id,
            "message": "템플릿이 삭제되었습니다."
        })
    except Exception as e:
        print(f"Error in delete_template: {str(e)}")
        return error_response(
            code=ErrorCode.SERVER_INTERNAL_ERROR,
            http_status=500,
            message="템플릿 삭제 중 오류가 발생했습니다."
        )
