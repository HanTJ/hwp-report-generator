# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HWP Report Generator: A FastAPI-based web system that automatically generates Korean HWP (Hangul Word Processor) format reports using Claude AI. Users input a report topic and the system generates a complete report following a bank's internal form template.

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Package Manager**: uv (recommended) or pip
- **AI**: Claude API (Anthropic) - Model: claude-sonnet-4-5-20250929, anthropic==0.71.0
- **HWP Processing**: olefile, zipfile (HWPX format)
- **Frontend**: React 18 + TypeScript + Vite
- **API Client**: Axios
- **Routing**: React Router DOM

## Architecture

### Core Components

**Backend** (`backend/app/`):
1. **main.py**: FastAPI application with endpoints for report generation
2. **routers/**: API route handlers (auth, reports, admin)
3. **models/**: Pydantic models for request/response validation
4. **database/**: SQLite database connection and operations
5. **utils/claude_client.py**: Claude API integration for content generation
6. **utils/hwp_handler.py**: HWPX file manipulation (unzip → modify XML → rezip)
7. **utils/auth.py**: JWT authentication and password hashing

**Frontend** (`frontend/src/`):
1. **components/**: Reusable React components
2. **pages/**: Page-level components
3. **services/**: API client services
4. **types/api.ts**: TypeScript type definitions for API responses
5. **App.tsx**: Main application component with routing

**Templates**:
- **backend/templates/report_template.hwpx**: HWP template with placeholders

### Data Flow

1. User submits report topic via web UI
2. FastAPI endpoint receives request
3. Claude API generates structured report content (title, summary, background, main content, conclusion)
4. HWP handler extracts HWPX (ZIP format), modifies XML content, replaces placeholders
5. System returns generated HWPX file for download

### HWP Template Placeholders

The HWPX template uses these placeholders that Claude's generated content replaces:

**Main Content Placeholders:**
- `{{TITLE}}` - Report title
- `{{DATE}}` - Generation date
- `{{BACKGROUND}}` - Background and purpose section content
- `{{MAIN_CONTENT}}` - Main body content
- `{{CONCLUSION}}` - Conclusion and recommendations content
- `{{SUMMARY}}` - Executive summary content

**Section Title Placeholders:**
- `{{TITLE_BACKGROUND}}` - Background section heading (default: "배경 및 목적")
- `{{TITLE_MAIN_CONTENT}}` - Main content section heading (default: "주요 내용")
- `{{TITLE_CONCLUSION}}` - Conclusion section heading (default: "결론 및 제언")
- `{{TITLE_SUMMARY}}` - Summary section heading (default: "요약")

Note: Section title placeholders allow customization of section headings while maintaining consistent template structure.

## Environment Setup

Create `backend/.env` file:
```
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Admin Account
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123!@#
ADMIN_USERNAME=관리자
```

**Security**: Never commit `.env` file to git. The `.gitignore` excludes all files starting with `.env`.

## Development Commands

### Backend Setup

**Install dependencies (using uv - recommended):**
```bash
cd backend
uv pip install -r requirements.txt
```

**Or using pip:**
```bash
cd backend
pip install -r requirements.txt
```

**Initialize database:**
```bash
cd backend
uv run python init_db.py
```

**Run backend server:**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or with standard python:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

**Install dependencies:**
```bash
cd frontend
npm install
```

**Run frontend dev server:**
```bash
cd frontend
npm run dev
```

**Build for production:**
```bash
cd frontend
npm run build
```

### Access the application:
```
http://localhost:5173       # Frontend (React)
http://localhost:8000       # Backend API
http://localhost:8000/docs  # API Documentation (Swagger)
```

### Running Both Servers

You need to run both backend and frontend servers simultaneously in separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## HWP File Handling Notes

- **Format**: Use HWPX (not HWP). HWPX is a ZIP archive containing XML files
- **Processing**: Unzip → Parse/modify XML → Rezip as HWPX
- **Compatibility**: HWPX format ensures cross-platform compatibility
- **Character encoding**: Ensure UTF-8 encoding for Korean text
- **Auto Template Generation**: If `templates/report_template.hwpx` doesn't exist, the system automatically creates a basic template on first report generation (main.py:113-161)

### Line Break Handling in HWPX

The system implements a sophisticated approach to handle line breaks in HWPX format:

1. **Paragraph Separation**: Double line breaks (`\n\n`) split text into separate `<hp:p>` (paragraph) tags
2. **Line Break Tags**: Single line breaks (`\n`) within paragraphs are converted to `<hp:lineBreak/>` XML tags
3. **Layout Cleanup**: Automatically removes incomplete `<hp:linesegarray>` elements that would prevent proper rendering
4. **Auto-calculation**: Hangul Word Processor automatically recalculates layout information when opening files without linesegarray data

This ensures that generated reports display with proper line breaks when opened in Hangul Word Processor, without requiring manual layout calculations.

## Project Structure (Monorepo)

```
hwp-report-generator/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py        # Authentication API
│   │   │   ├── reports.py     # Reports API
│   │   │   └── admin.py       # Admin API
│   │   ├── models/            # Pydantic models
│   │   │   ├── user.py
│   │   │   ├── report.py
│   │   │   └── token_usage.py
│   │   ├── database/          # Database layer
│   │   │   ├── connection.py
│   │   │   ├── user_db.py
│   │   │   ├── report_db.py
│   │   │   └── token_usage_db.py
│   │   └── utils/             # Utility functions
│   │       ├── claude_client.py
│   │       ├── hwp_handler.py
│   │       └── auth.py
│   ├── templates/             # HWPX templates only
│   │   └── report_template.hwpx
│   ├── output/                # Generated reports
│   ├── temp/                  # Temporary files
│   ├── data/                  # SQLite database
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── init_db.py
│   ├── migrate_db.py
│   └── .env                   # Backend environment variables
│
├── frontend/                  # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client services
│   │   ├── types/
│   │   │   └── api.ts         # TypeScript API types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts         # Vite config with proxy
│
├── templates/                 # Legacy HTML templates (will be removed)
├── static/                    # Legacy static files (will be removed)
├── .gitignore
├── CLAUDE.md                  # Project documentation
└── README.md
```

## API Key Configuration

The system expects `CLAUDE_API_KEY` in environment variables. Check API usage limits and network connectivity if generation fails.

## API Response Standard

All Backend-Frontend API communications follow a standardized response format for consistency and better error handling.

### ⚠️ MANDATORY COMPLIANCE RULE

**ALL new API endpoints MUST use the standard response format.**

- ✅ **REQUIRED**: Use `success_response()` and `error_response()` from `utils/response_helper.py`
- ❌ **FORBIDDEN**: Direct use of `HTTPException` or returning raw dictionaries/models
- ✅ **REQUIRED**: Use `ErrorCode` class constants for error codes
- ❌ **FORBIDDEN**: Hardcoded error code strings

**Pull requests that violate this standard will be rejected.**

### Current Implementation Status

| Router | Endpoints | Compliance | Status |
|--------|-----------|------------|--------|
| **Topics** | 5/5 | 100% ✅ | **Reference Implementation** |
| **Messages** | 4/4 | 100% ✅ | Fully Compliant |
| **Artifacts** | 5/5 | 100% ✅ | Fully Compliant |
| **Auth** | 5/5 | 100% ✅ | **Fully Compliant** ✨ |
| **Admin** | 6/6 | 100% ✅ | **Fully Compliant** ✨ |
| **Reports** | 3/3 | 100% ✅ | **Fully Compliant** ✨ |
| **Main Routes** | 0/4 | 0% ❌ | **Legacy - Deprecation Planned** |

**Overall Compliance**: 100% (28/28 active endpoints) ✨

**Legacy Routes**: 4 endpoints pending deprecation (Main Routes)

**Target**: ✅ **ACHIEVED** - 100% compliance for all active routers

### Standard Response Structure

**Success Response:**
```json
{
  "success": true,
  "data": { /* actual resource or result data */ },
  "error": null,
  "meta": {
    "requestId": "1c0c...f"
  },
  "feedback": [
    {
      "code": "PROFILE_INCOMPLETE",
      "level": "info",            // info | warning | error
      "feedbackCd": "프로필 사진을 등록하면 더 좋아요."
    }
  ]
}
```

**Failure Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_TOKEN",   // unique error code (DOMAIN.DETAIL)
    "httpStatus": 401,
    "message": "유효하지 않은 토큰입니다.",
    "details": { "reason": "expired" },
    "traceId": "1c0c...f",
    "hint": "다시 로그인해 주세요."
  },
  "meta": { "requestId": "1c0c...f" },
  "feedback": []
}
```

### Field Descriptions

**Common Fields:**
- `success`: Boolean indicating request success/failure
- `data`: Actual response data (null on failure)
- `error`: Error details object (null on success)
- `meta`: Metadata including `requestId` for tracing
- `feedback`: Array of optional user feedback/hints

**Error Object Fields:**
- `code`: Unique error code in `DOMAIN.DETAIL` format
- `httpStatus`: HTTP status code (401, 404, 500, etc.)
- `message`: User-friendly error message
- `details`: Additional error details (optional)
- `traceId`: Unique ID for error tracing
- `hint`: Suggested action for user (optional)

**Feedback Object Fields:**
- `code`: Feedback identifier
- `level`: `"info"` | `"warning"` | `"error"`
- `feedbackCd`: Feedback message for user

### Backend Implementation (FastAPI)

**Type Definitions** (`models/api_response.py`):
```python
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from enum import Enum

class FeedbackLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class Feedback(BaseModel):
    code: str
    level: FeedbackLevel
    feedbackCd: str

class ErrorResponse(BaseModel):
    code: str
    httpStatus: int
    message: str
    details: Optional[Dict[str, Any]] = None
    traceId: str
    hint: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorResponse] = None
    meta: Dict[str, str]
    feedback: List[Feedback] = []
```

**Helper Functions** (`utils/response_helper.py`):
```python
import uuid
from fastapi.responses import JSONResponse

def success_response(data: Any, feedback: List[Feedback] = []):
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": {"requestId": str(uuid.uuid4())},
        "feedback": feedback
    }

def error_response(
    code: str,
    http_status: int,
    message: str,
    details: Dict = None,
    hint: str = None
):
    return JSONResponse(
        status_code=http_status,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "httpStatus": http_status,
                "message": message,
                "details": details,
                "traceId": str(uuid.uuid4()),
                "hint": hint
            },
            "meta": {"requestId": str(uuid.uuid4())},
            "feedback": []
        }
    )
```

### Frontend Implementation (React/TypeScript)

**Type Definitions** (`types/api.ts` or `src/types/api.ts`):
```typescript
export type FeedbackLevel = 'info' | 'warning' | 'error';

export interface Feedback {
  code: string;
  level: FeedbackLevel;
  feedbackCd: string;
}

export interface ErrorResponse {
  code: string;
  httpStatus: number;
  message: string;
  details?: Record<string, any>;
  traceId: string;
  hint?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ErrorResponse | null;
  meta: {
    requestId: string;
  };
  feedback: Feedback[];
}
```

**Usage Example**:
```typescript
import { ApiResponse } from '@/types/api';

async function generateReport(topic: string): Promise<ApiResponse<ReportData>> {
  const response = await fetch('/api/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic })
  });

  const result: ApiResponse<ReportData> = await response.json();

  if (result.success) {
    console.log('Report generated:', result.data);
  } else {
    console.error('Error:', result.error?.message);
    if (result.error?.hint) {
      console.log('Hint:', result.error.hint);
    }
  }

  return result;
}
```

### Error Code Conventions

Error codes follow the `DOMAIN.DETAIL` format:

**Authentication (`AUTH.*`):**
- `AUTH.INVALID_TOKEN` - Invalid authentication token
- `AUTH.TOKEN_EXPIRED` - Token has expired
- `AUTH.UNAUTHORIZED` - Insufficient permissions
- `AUTH.INVALID_CREDENTIALS` - Wrong email/password

**Reports (`REPORT.*`):**
- `REPORT.GENERATION_FAILED` - Report generation failed
- `REPORT.NOT_FOUND` - Report not found
- `REPORT.INVALID_TOPIC` - Invalid topic provided
- `REPORT.DOWNLOAD_FAILED` - Download failed

**Templates (`TEMPLATE.*`):**
- `TEMPLATE.INVALID_FORMAT` - Invalid HWPX format
- `TEMPLATE.UPLOAD_FAILED` - Upload failed
- `TEMPLATE.NOT_FOUND` - Template not found
- `TEMPLATE.PERMISSION_DENIED` - No permission to modify

**Validation (`VALIDATION.*`):**
- `VALIDATION.REQUIRED_FIELD` - Required field missing
- `VALIDATION.INVALID_FORMAT` - Invalid format
- `VALIDATION.MAX_LENGTH_EXCEEDED` - Maximum length exceeded

**Server (`SERVER.*`):**
- `SERVER.INTERNAL_ERROR` - Internal server error
- `SERVER.SERVICE_UNAVAILABLE` - Service temporarily unavailable
- `SERVER.DATABASE_ERROR` - Database operation failed

### API Endpoints Coverage

This standard applies to **ALL** API endpoints:

1. **Authentication API** (`/api/auth/*`)
   - Login, Register, Logout, Token refresh

2. **Reports API** (`/api/reports/*`)
   - Generate, List, Download, Delete reports

3. **Templates API** (`/api/templates/*`)
   - Template CRUD, Placeholder management

4. **Prompts API** (`/api/prompts/*`)
   - Prompt preset CRUD

5. **Admin API** (`/api/admin/*`)
   - User management, System settings

### Examples

**Report Generation Success:**
```json
{
  "success": true,
  "data": {
    "reportId": 123,
    "filename": "2025년_디지털뱅킹_트렌드.hwpx",
    "filePath": "/output/report_123.hwpx",
    "createdAt": "2025-10-27T10:30:00Z"
  },
  "error": null,
  "meta": {
    "requestId": "req_abc123"
  },
  "feedback": []
}
```

**Login Failure:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_CREDENTIALS",
    "httpStatus": 401,
    "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
    "details": { "field": "password" },
    "traceId": "trace_xyz789",
    "hint": "비밀번호를 잊으셨다면 '비밀번호 찾기'를 이용해주세요."
  },
  "meta": {
    "requestId": "req_def456"
  },
  "feedback": []
}
```

**Template Upload with Warning:**
```json
{
  "success": true,
  "data": {
    "templateId": 45,
    "name": "분기보고서_템플릿",
    "placeholders": ["TITLE", "DATE", "CONTENT"]
  },
  "error": null,
  "meta": {
    "requestId": "req_ghi789"
  },
  "feedback": [
    {
      "code": "TEMPLATE.MISSING_PLACEHOLDERS",
      "level": "warning",
      "feedbackCd": "SUMMARY 플레이스홀더가 누락되어 있습니다. 추가하시겠습니까?"
    }
  ]
}
```

---

## Migration Guide: Legacy to Standard Response Format

### Why Migrate?

**Problems with Legacy Approach:**
- ❌ Inconsistent error handling across endpoints
- ❌ Difficult to parse responses on frontend
- ❌ No standardized error codes
- ❌ Missing request tracing capability
- ❌ No support for user feedback/hints

**Benefits of Standard Format:**
- ✅ Consistent structure across all endpoints
- ✅ Easy to parse and handle on frontend
- ✅ Standardized error codes (DOMAIN.DETAIL)
- ✅ Built-in request tracing (requestId, traceId)
- ✅ Support for user feedback and hints

### Step-by-Step Migration

#### Step 1: Import Required Modules

**Before:**
```python
from fastapi import APIRouter, HTTPException
from app.models.user import UserResponse
```

**After:**
```python
from fastapi import APIRouter, Depends
from app.models.user import UserResponse
from app.utils.response_helper import success_response, error_response, ErrorCode
```

#### Step 2: Replace HTTPException with error_response()

**Before (❌ Non-compliant):**
```python
@router.post("/login")
async def login(credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="계정이 비활성화되었습니다."
        )

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
```

**After (✅ Compliant):**
```python
@router.post("/login")
async def login(credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        return error_response(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            http_status=401,
            message="이메일 또는 비밀번호가 올바르지 않습니다.",
            hint="입력 정보를 다시 확인해주세요."
        )

    if not user.is_active:
        return error_response(
            code=ErrorCode.AUTH_UNAUTHORIZED,
            http_status=403,
            message="계정이 비활성화되었습니다.",
            hint="관리자에게 문의하여 계정을 활성화해주세요."
        )

    token = create_access_token(data={"sub": user.email})
    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    })
```

#### Step 3: Wrap Success Responses

**Before (❌ Non-compliant):**
```python
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_admin)):
    users = UserDB.get_all_users()
    return [UserResponse.from_orm(u) for u in users]
```

**After (✅ Compliant):**
```python
@router.get("/users")
async def get_all_users(current_user: User = Depends(get_current_admin)):
    try:
        users = UserDB.get_all_users()
        return success_response({
            "users": [UserResponse.from_orm(u) for u in users],
            "total": len(users)
        })
    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="사용자 목록 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
```

#### Step 4: Handle Exceptions Properly

**Before (❌ Non-compliant):**
```python
@router.delete("/reports/{report_id}")
async def delete_report(report_id: int, current_user: User = Depends(get_current_user)):
    report = ReportDB.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    ReportDB.delete_report(report_id)
    return {"message": "Report deleted successfully"}
```

**After (✅ Compliant):**
```python
@router.delete("/reports/{report_id}")
async def delete_report(report_id: int, current_user: User = Depends(get_current_user)):
    try:
        report = ReportDB.get_report_by_id(report_id)
        if not report:
            return error_response(
                code=ErrorCode.REPORT_NOT_FOUND,
                http_status=404,
                message="보고서를 찾을 수 없습니다."
            )

        if report.user_id != current_user.id:
            return error_response(
                code=ErrorCode.REPORT_UNAUTHORIZED,
                http_status=403,
                message="이 보고서에 대한 권한이 없습니다."
            )

        ReportDB.delete_report(report_id)
        return success_response({
            "message": "보고서가 성공적으로 삭제되었습니다.",
            "deleted_id": report_id
        })

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="보고서 삭제 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
```

### Migration Checklist

Use this checklist when migrating an endpoint:

- [ ] Import `success_response`, `error_response`, `ErrorCode` from `response_helper`
- [ ] Replace all `HTTPException` with `error_response()`
- [ ] Wrap all success returns with `success_response()`
- [ ] Use `ErrorCode` constants instead of hardcoded strings
- [ ] Add meaningful `hint` messages to error responses
- [ ] Add try-except blocks for database/external operations
- [ ] Remove `response_model` from decorator (if it was direct model return)
- [ ] Test both success and error cases
- [ ] Update API documentation/examples

---

## Reference Implementation: Topics Router

The `topics.py` router serves as the **reference implementation** for the standard response format. Study this file when implementing new endpoints.

### Example: Create Topic Endpoint

**File**: `backend/app/routers/topics.py`

```python
from fastapi import APIRouter, Depends
from app.database.topic_db import TopicDB
from app.models.topic import TopicCreate, TopicResponse
from app.utils.response_helper import success_response, error_response, ErrorCode
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/api/topics")
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation topic.

    Args:
        topic_data: Topic creation data (input_prompt, language)
        current_user: Authenticated user from JWT token

    Returns:
        Standard API response with created topic data
    """
    try:
        # Business logic
        topic = TopicDB.create_topic(
            user_id=current_user.id,
            topic_data=topic_data
        )

        # Success response with created resource
        return success_response({
            "id": topic.id,
            "input_prompt": topic.input_prompt,
            "language": topic.language,
            "status": topic.status,
            "created_at": topic.created_at.isoformat()
        })

    except ValueError as e:
        # Handle validation errors
        return error_response(
            code=ErrorCode.VALIDATION_INVALID_FORMAT,
            http_status=400,
            message="입력 데이터가 올바르지 않습니다.",
            details={"error": str(e)}
        )

    except Exception as e:
        # Handle unexpected errors
        return error_response(
            code=ErrorCode.TOPIC_CREATION_FAILED,
            http_status=500,
            message="토픽 생성 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )


@router.get("/api/topics/{topic_id}")
async def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific topic by ID.

    Args:
        topic_id: Topic ID to retrieve
        current_user: Authenticated user from JWT token

    Returns:
        Standard API response with topic data or error
    """
    try:
        topic = TopicDB.get_topic_by_id(topic_id)

        # Check if topic exists
        if not topic:
            return error_response(
                code=ErrorCode.TOPIC_NOT_FOUND,
                http_status=404,
                message="토픽을 찾을 수 없습니다."
            )

        # Check authorization
        if topic.user_id != current_user.id:
            return error_response(
                code=ErrorCode.TOPIC_UNAUTHORIZED,
                http_status=403,
                message="이 토픽에 대한 접근 권한이 없습니다."
            )

        # Return topic data
        return success_response(TopicResponse.from_orm(topic).dict())

    except Exception as e:
        return error_response(
            code=ErrorCode.SERVER_DATABASE_ERROR,
            http_status=500,
            message="토픽 조회 중 오류가 발생했습니다.",
            details={"error": str(e)}
        )
```

### Key Patterns to Follow

1. **Always use try-except blocks**
   - Catch specific exceptions first (ValueError, KeyError, etc.)
   - Catch generic Exception last as fallback
   - Never let exceptions bubble up unhandled

2. **Return appropriate HTTP status codes**
   - 200: Success (GET, PATCH, DELETE)
   - 201: Created (POST for new resources) - but we use 200 for consistency
   - 400: Bad Request (validation errors)
   - 401: Unauthorized (authentication failed)
   - 403: Forbidden (authorization failed)
   - 404: Not Found (resource doesn't exist)
   - 500: Internal Server Error (unexpected errors)

3. **Use descriptive error messages in Korean**
   - User-facing messages should be in Korean
   - Add helpful `hint` for common errors
   - Include technical details in `details` field for debugging

4. **Use ErrorCode constants**
   - Never hardcode error code strings
   - Use `ErrorCode.DOMAIN_DETAIL` pattern
   - Add new constants to `ErrorCode` class if needed

5. **Validate authorization**
   - Check if resource exists first (404)
   - Check if user has permission second (403)
   - Return appropriate error codes

---

## Available Error Codes

All error codes are defined in `backend/app/utils/response_helper.py` as `ErrorCode` class constants.

### Authentication & Authorization
- `ErrorCode.AUTH_INVALID_TOKEN` - Invalid or malformed JWT token
- `ErrorCode.AUTH_TOKEN_EXPIRED` - JWT token has expired
- `ErrorCode.AUTH_UNAUTHORIZED` - User lacks required permissions
- `ErrorCode.AUTH_INVALID_CREDENTIALS` - Wrong email/password

### Topics
- `ErrorCode.TOPIC_NOT_FOUND` - Topic with given ID doesn't exist
- `ErrorCode.TOPIC_UNAUTHORIZED` - User doesn't own this topic
- `ErrorCode.TOPIC_CREATION_FAILED` - Failed to create topic
- `ErrorCode.TOPIC_UPDATE_FAILED` - Failed to update topic
- `ErrorCode.TOPIC_DELETE_FAILED` - Failed to delete topic

### Messages
- `ErrorCode.MESSAGE_NOT_FOUND` - Message with given ID doesn't exist
- `ErrorCode.MESSAGE_CREATION_FAILED` - Failed to create message
- `ErrorCode.MESSAGE_UPDATE_FAILED` - Failed to update message
- `ErrorCode.MESSAGE_DELETE_FAILED` - Failed to delete message

### Artifacts
- `ErrorCode.ARTIFACT_NOT_FOUND` - Artifact with given ID doesn't exist
- `ErrorCode.ARTIFACT_INVALID_KIND` - Invalid artifact type
- `ErrorCode.ARTIFACT_DOWNLOAD_FAILED` - Failed to download artifact

### Validation
- `ErrorCode.VALIDATION_REQUIRED_FIELD` - Required field is missing
- `ErrorCode.VALIDATION_INVALID_FORMAT` - Data format is invalid
- `ErrorCode.VALIDATION_MAX_LENGTH_EXCEEDED` - Input exceeds maximum length

### Server Errors
- `ErrorCode.SERVER_INTERNAL_ERROR` - Unexpected server error
- `ErrorCode.SERVER_DATABASE_ERROR` - Database operation failed
- `ErrorCode.SERVER_SERVICE_UNAVAILABLE` - Service temporarily unavailable

**Note**: If you need a new error code, add it to the `ErrorCode` class in `response_helper.py` following the `DOMAIN_DETAIL` naming convention.

---

## Testing Standard Responses

When writing tests for endpoints, verify the standard response structure:

```python
def test_create_topic_success(client, auth_headers):
    response = client.post(
        "/api/topics",
        headers=auth_headers,
        json={"input_prompt": "Test topic", "language": "ko"}
    )

    assert response.status_code == 200
    body = response.json()

    # Verify standard structure
    assert body["success"] is True
    assert body["data"] is not None
    assert body["error"] is None
    assert "requestId" in body["meta"]
    assert isinstance(body["feedback"], list)

    # Verify data content
    assert body["data"]["input_prompt"] == "Test topic"


def test_get_topic_not_found(client, auth_headers):
    response = client.get("/api/topics/999999", headers=auth_headers)

    assert response.status_code == 404
    body = response.json()

    # Verify standard error structure
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"] is not None
    assert body["error"]["code"] == "TOPIC.NOT_FOUND"
    assert body["error"]["httpStatus"] == 404
    assert body["error"]["message"]
    assert "traceId" in body["error"]
```
