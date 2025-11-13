# Backend Development Guidelines

This document provides development guidelines for **Claude Code** when working on the **HWP Report Generator backend**.

---

## Table of Contents

1. [Code Style and Documentation](#code-style-and-documentation)
2. [Testing Guidelines](#testing-guidelines)
3. [References](#references)

---

## Code Style and Documentation

### DocString Rules

**All Python functions and classes MUST include a Google-style DocString.**

#### DocString Format Example

```python
def generate_report(topic: str, user_id: int) -> dict:
    """Generates a report and returns metadata.

    Args:
        topic: Report generation topic (e.g., "Digital Banking Trends 2025")
        user_id: ID of the user creating the report

    Returns:
        Dictionary containing generated report info:
            - id: Report ID
            - filename: Generated file name
            - file_path: File storage path

    Raises:
        ValueError: When topic is empty
        APIError: When Claude API call fails

    Examples:
        >>> report = generate_report("AI Trends", user_id=1)
        >>> print(report['filename'])
        'report_20251027_103954.hwpx'
    """
    pass

def get_user_by_id(user_id: int) -> User:
    """Retrieves a user by ID."""
    pass
```

For class DocStrings, include attributes in the docstring header. Private functions (prefixed with `_`) should also have DocStrings but can be shorter.

#### Required Sections

| Section | When Required | Format |
|---------|---------------|--------|
| **Summary** | Always | One-line description ending with period |
| **Args** | If parameters exist | `param_name: description` |
| **Returns** | If return value exists | Describe structure and meaning |
| **Raises** | If exceptions possible | `ExceptionType: Condition` |
| **Examples** | For complex functions | Use doctest format (`>>>`) |

#### Key Rules

1. **Summary:** Start with imperative verb ("Generates", "Returns", "Calculates"), end with period
2. **Args:** Omit types (use type hints), indicate optional params, use indentation for nested structures
3. **Returns:** Describe structure, list key fields for dicts/objects
4. **Raises:** List exceptions with conditions
5. **Examples:** Use `>>>` format, show input and output

#### Common Mistakes

❌ No DocString, incomplete summary, wrong format (`@param`, `@return`)
✅ Complete Google-style DocString with all required sections

### Scope

Apply to: `app/routers/*.py`, `app/models/*.py`, `app/database/*.py`, `app/utils/*.py`, and all backend Python files.

**Exceptions:** `__init__.py` (imports only), simple getters/setters, test functions (optional).

---

## File Management Guidelines

### Artifact Storage

**ALWAYS use `ArtifactManager` for artifact file operations.**

#### ✅ DO - Use ArtifactManager

```python
from app.utils.artifact_manager import ArtifactManager
from shared.types.enums import ArtifactKind

# Generate standardized file path
filepath = ArtifactManager.generate_artifact_path(
    topic_id=topic.id,
    message_id=message.id,
    filename=f"report_v{version}.md"
)

# Store artifact
file_size = ArtifactManager.store_artifact(
    content=markdown_content,
    filepath=filepath,
    is_binary=False  # False for MD, True for HWPX
)

# Calculate hash for integrity
sha256 = ArtifactManager.calculate_sha256(filepath)

# Store metadata in database
artifact = ArtifactDB.create_artifact(
    topic_id=topic.id,
    message_id=message.id,
    kind=ArtifactKind.MD,
    filename=os.path.basename(filepath),
    file_path=filepath,
    file_size=file_size,
    sha256=sha256
)
```

#### ❌ DON'T - Direct file operations

```python
# DON'T do this!
with open(f"artifacts/topic_{topic_id}/file.md", "w") as f:
    f.write(content)
```

**Why?** `ArtifactManager` provides:
- Consistent file path structure
- Automatic directory creation
- UTF-8 encoding for text files
- File size and hash calculation
- Support for future storage backends (S3, Azure Blob)

### Markdown File Operations

**Use `MarkdownHandler` for Markdown file operations.**

#### ✅ DO - Use MarkdownHandler

```python
from app.utils.md_handler import MarkdownHandler

# Format report data as Markdown
report_data = {
    "title": "Digital Banking Report",
    "summary": "Executive summary...",
    "background": "Background information...",
    "main_content": "Detailed analysis...",
    "conclusion": "Conclusions and recommendations..."
}

md_content = MarkdownHandler.format_report_as_md(report_data)

# Save Markdown file
MarkdownHandler.save_md_file(md_content, filepath)

# Read Markdown file
content = MarkdownHandler.read_md_file(filepath)

# Parse Markdown back to structured data
parsed_data = MarkdownHandler.parse_md_report(content)
```

**Report Structure Standard:**
- `# {Title}` - Main title (H1)
- `## 요약` - Summary section (H2)
- `## 배경 및 목적` - Background section (H2)
- `## 주요 내용` - Main content section (H2)
- `## 결론 및 제언` - Conclusion section (H2)

### Transformation Tracking

**ALWAYS record transformations when converting artifacts.**

#### ✅ DO - Track transformations

```python
from app.database.transformation_db import TransformationDB
from app.models.transformation import TransformationCreate
from shared.types.enums import TransformOperation

# After converting MD to HWPX
transformation = TransformationDB.create_transformation(
    TransformationCreate(
        from_artifact_id=md_artifact.id,
        to_artifact_id=hwpx_artifact.id,
        operation=TransformOperation.CONVERT,
        params_json='{"template": "report_template.hwpx"}'
    )
)
```

**Benefits:**
- Lineage tracking (which HWPX came from which MD)
- Audit trail for conversions
- Support for conversion chains (MD → HWPX → PDF)
- Debugging conversion issues

#### Common Transformation Operations

```python
from shared.types.enums import TransformOperation

# Format conversion
TransformOperation.CONVERT  # MD → HWPX, HWPX → PDF, etc.

# Language translation (future use)
TransformOperation.TRANSLATE  # KO → EN, EN → KO, etc.
```

---

## Testing Guidelines

> **📖 For detailed testing guide, see [BACKEND_TEST.md](./BACKEND_TEST.md)**

### Test Environment Setup

**⚠️ IMPORTANT: Python Interpreter Configuration**

The project uses **uv** as the package manager and requires the following Python interpreter:

```
Project Root: /Users/jaeyoonmo/workspace/hwp-report-generator
Backend Venv: backend/.venv/bin/python
```

**Claude Code Configuration:**
- Set IDE Python interpreter to: `backend/.venv/bin/python`
- Package manager: `uv`
- When running tests, Claude Code will automatically use this interpreter

**Verification:**

```bash
# Check the Python interpreter path
which python
# Expected: /Users/jaeyoonmo/workspace/hwp-report-generator/backend/.venv/bin/python

# Verify uv is configured
cd backend && uv --version
```

---

### Quick Start

**Run all tests with coverage:**

```bash
cd backend
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

**Install test dependencies:**

```bash
uv pip install -r requirements-dev.txt
```

---

### Current Coverage Status

**Overall Coverage: 52%** ✅ (Target: ≥70%, topics.py: 78%)

- **Total Tests:** 88+ tests (88 passed, 0 failed)
- **Test Files:** 20+ files covering auth, claude_client, hwp_handler, API endpoints, and templates
- **Coverage Increase:** +6% (from 46% to 52% in this session)

**Top Modules:**
- `routers/topics.py`: 78% ✅ (+39% improvement)
- `utils/markdown_builder.py`: 100% ✅
- `utils/response_helper.py`: 96% ✅
- `utils/markdown_parser.py`: 92% ✅
- `utils/auth.py`: 80% ✅
- `utils/file_utils.py`: 96% ✅

---

### Coverage Goals

- **Overall:** ≥ 70%
- **Core business logic:** ≥ 90%
- **Utility functions:** ≥ 85%

---

### Best Practices

**DO ✅:**
- Mock all external API calls (Claude API, etc.)
- Use `@patch('app.utils.module.Class')` at point of use
- Keep tests independent and isolated
- Use fixtures for common setup
- Test both success and error scenarios

**DON'T ❌:**
- Never call actual APIs in tests
- Don't use production database
- Don't use incorrect mock paths (`@patch('anthropic.Anthropic')` → use `@patch('app.utils.claude_client.Anthropic')`)
- Don't skip error handling tests

**For detailed information on:**
- Test structure and fixtures
- Mocking patterns and examples
- Test writing patterns
- Troubleshooting common issues
- CI/CD integration

**→ See [BACKEND_TEST.md](./BACKEND_TEST.md)**

---

### Claude Code Testing Checklist

**Before running tests, Claude Code MUST verify:**

- [ ] **Python Interpreter**: Verify using `/Users/jaeyoonmo/workspace/hwp-report-generator/backend/.venv/bin/python`
  ```bash
  which python
  # Should output: .../backend/.venv/bin/python
  ```

- [ ] **Package Manager**: Confirm `uv` is configured
  ```bash
  cd backend && uv --version
  ```

- [ ] **Working Directory**: Always run tests from `backend/` directory
  ```bash
  cd backend && uv run pytest tests/ -v --cov=app --cov-report=term-missing
  ```

- [ ] **Virtual Environment**: Ensure `.venv` is activated or `uv run` is used
  ```bash
  # Option 1: Use uv run (recommended)
  uv run pytest tests/ -v

  # Option 2: Activate venv manually
  source .venv/bin/activate
  pytest tests/ -v
  ```

- [ ] **Dependencies**: Confirm test dependencies installed
  ```bash
  uv pip install -r requirements-dev.txt
  ```

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Wrong working directory | Run from `backend/` directory with `uv run` |
| `pytest: command not found` | pytest not installed | Run `uv pip install -r requirements-dev.txt` |
| `Python interpreter not found` | Wrong venv path | Verify path: `backend/.venv/bin/python` |
| Import errors in tests | Package manager mismatch | Use `uv run pytest` instead of raw `pytest` |

---

## DocString Review Checklist

- [ ] Does every public function/class have a DocString?
- [ ] Is the summary line clear and concise?
- [ ] Are Args and Returns sections complete?
- [ ] Is there a Raises section if exceptions may occur?
- [ ] Do complex functions include Examples?
- [ ] Is it written in English and follows Google style?

---

## Recent Improvements (v2.2)

### Bug Fix: /ask Artifact Markdown Parsing

**Problem:**
- `/api/topics/{topic_id}/ask` endpoint was saving raw Claude response to artifact
- Expected: Parse markdown through `parse_markdown_to_content()` → `build_report_md()`

**Solution:**
- Added markdown parsing and building logic to /ask function (lines 884-892)
- Now consistent with `generate_topic_report` implementation
- 3 new test cases added (TC-ASK-001, TC-ASK-003, TC-ASK-004)

**Test Results:**
```
tests/test_routers_topics.py::TestTopicsRouter
- 28/28 tests PASSED (100%)
- /ask tests: 15/15 PASSED (100%)
- New markdown validation tests: 3/3 PASSED (100%)
```

**Files Modified:**
- `app/routers/topics.py` (lines 880-906)
- `tests/test_routers_topics.py` (new test methods added)

**Reference:**
- Spec: `backend/doc/specs/20251110_fix_ask_artifact_markdown_parsing.md`

---

## Unit Spec Workflow

**Before implementing any feature or fix, Claude Code MUST create a Unit Spec document.**

### Workflow Steps

1. **User Request** → User describes a feature, bug fix, or change
2. **Unit Spec Creation** → Claude creates a spec document following `backend/doc/Backend_UnitSpec.md` template
3. **Review & Approval** → User reviews and approves the spec
4. **Implementation** → Claude implements according to the approved spec
5. **Testing** → Verify all test cases defined in the spec

### Unit Spec Template Structure

Each Unit Spec MUST include:

#### 1. Requirements Summary
- **Purpose:** One-line description of what the feature/fix does
- **Type:** ☐ New ☐ Change ☐ Delete
- **Core Requirements:**
  - Input: Expected parameters (e.g., topic, userId)
  - Output: Return values (e.g., markdown, json, status code)
  - Constraints: Validation rules, timeouts, error conditions
  - Processing Flow: One-line summary of operation

#### 2. Implementation Target Files
| Type | Path | Description |
|------|------|-------------|
| New | backend/app/api/... | New endpoint |
| Change | backend/app/services/... | Modified logic |
| Reference | backend/app/utils/... | Reference implementation |

#### 3. Flow Diagram (Mermaid)
```mermaid
flowchart TD
    A[Client] -->|Request| B(API)
    B --> C[Service Layer]
    C --> D{Logic}
    D --> E[Response]
```

#### 4. Test Plan
- **Principles:** TDD, Layer Coverage (Unit → Integration → API), Independence
- **Test Cases:** Use table format with:
  - TC ID
  - Layer (API/Unit/Integration)
  - Scenario
  - Purpose
  - Input/Precondition
  - Expected Result

### Example Workflow

```
User: "Add a feature to export reports to PDF"

Claude: "I'll create a Unit Spec for this feature first."

→ Creates: backend/doc/specs/export_pdf_feature.md
→ Presents: Spec summary with requirements, files, flow, tests
→ Asks: "Please review this spec. Should I proceed with implementation?"

User: "Approved, but change the endpoint path"

Claude: "Updated. Starting implementation..."
→ Implements according to spec
→ Writes tests from test plan
→ Reports completion with test results
```

### Unit Spec File Naming

- Location: `backend/doc/specs/`
- Format: `YYYYMMDD_feature_name.md`
- Example: `20251106_export_pdf_feature.md`

### Benefits

- **Clear Requirements:** Prevents misunderstandings
- **Test-First:** Tests are defined before implementation
- **Documentation:** Specs serve as implementation documentation
- **Review Point:** User can correct course before coding begins
- **Consistency:** All features follow same planning process

### Reference

- Template: `backend/doc/Backend_UnitSpec.md`
- Test Guide: `backend/BACKEND_TEST.md`

---

## Keyword Management Strategy for Placeholder Classification

### Overview

When `meta_info_generator.py` extracts Placeholders from Templates, unknown keywords (e.g., `{{RISK}}`, `{{POSITION}}`) may not match predefined keyword patterns. This section outlines the strategy for managing such keywords over time.

**Current Strategy (Phase 1):** Progressive keyword expansion with data-driven decision making.

### Phase 1: Current Implementation (MVP)

**Predefined Keywords (5):**
```python
PHASE_1_KEYWORDS = {
    "TITLE": {"type": "section_title", "section": "제목"},
    "SUMMARY": {"type": "section_content", "section": "요약"},
    "BACKGROUND": {"type": "section_content", "section": "배경"},
    "CONCLUSION": {"type": "section_content", "section": "결론"},
    "DATE": {"type": "metadata", "section": "날짜"},
}

# Location: backend/app/utils/meta_info_generator.py
KEYWORD_CLASSIFICATION = PHASE_1_KEYWORDS
```

**Key Features:**
- Unknown keywords fall back to safe defaults (`section_content`)
- Usage patterns are logged for analysis (see below)
- No Admin page required

**Logging Requirement:**
Add `KeywordUsageLog` table to track which keywords are matched vs. unmatched:
```sql
CREATE TABLE keyword_usage_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    matched_keyword TEXT,  -- NULL if default is used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(template_id) REFERENCES templates(id)
);
```

### Phase 2: Progressive Keyword Expansion (1 month after Phase 1)

**Objective:** Analyze usage patterns and add frequently used keywords to `PHASE_2_KEYWORDS`.

**Candidate Keywords to Monitor:**
- `RISK` (위험 분석)
- `OVERVIEW` (개요)
- `MARKET` (시장 분석)
- `REGULATION` (규제 현황)
- `EXECUTIVE` (요약)

**Implementation:**
1. Run monthly analysis on `keyword_usage_logs`
2. Identify top 5-10 unmatched keywords
3. Add to `PHASE_2_KEYWORDS` in code
4. Update `KEYWORD_CLASSIFICATION = PHASE_2_KEYWORDS`

**Monitoring Target:**
- Goal: Matched keywords ≥ 80% (unmatched < 20%)

### Phase 3: Hybrid Strategy (3-6 months after Phase 1)

**Objective:** Support organization-specific and custom keywords via Admin interface.

**Strategy:** Combine code-based keywords + database-managed custom keywords.

**Required Implementation:**
1. **Database Schema:**
   ```sql
   CREATE TABLE custom_keywords (
       id INTEGER PRIMARY KEY,
       keyword TEXT UNIQUE NOT NULL,
       type TEXT NOT NULL,  -- section_title, section_content, metadata
       display_name TEXT NOT NULL,
       description TEXT,
       examples JSON,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **Admin API Endpoints:**
   ```
   POST /api/admin/custom-keywords
   GET /api/admin/custom-keywords
   PUT /api/admin/custom-keywords/{id}
   DELETE /api/admin/custom-keywords/{id}
   ```

3. **Merge Logic in meta_info_generator.py:**
   ```python
   def create_meta_info_from_placeholders(placeholders, custom_keywords=None):
       # Merge built-in + custom keywords (custom overrides built-in)
       all_keywords = {**BUILT_IN_KEYWORDS, **(custom_keywords or {})}
       # ... rest of logic
   ```

### Reference Documents

- **Detailed Analysis:** `backend/doc/keyword_management_strategies.md`
- **Implementation Guide:** `backend/doc/meta_info_generator_guide.md`
- **Why Keyword Matching:** `backend/doc/why_keyword_matching.md`

---

---

## Backend Architecture Overview

### Directory Structure

```
backend/app/
├── main.py                          # FastAPI entry point (router registration, initialization)
│
├── routers/                         # API endpoints (6 modules)
│   ├── auth.py                      # Authentication (signup, login, JWT)
│   ├── topics.py                    # Topic/report generation (message chaining)
│   ├── messages.py                  # Message retrieval
│   ├── artifacts.py                 # Artifact (MD, HWPX) download/convert
│   ├── templates.py                 # ✨ Template upload/management
│   └── admin.py                     # Admin API
│
├── models/                          # Pydantic data models (9 modules)
│   ├── user.py                      # User, UserCreate, UserUpdate
│   ├── topic.py                     # Topic, TopicCreate (+ template_id)
│   ├── message.py                   # Message, AskRequest (+ template_id)
│   ├── template.py                  # ✨ Template, Placeholder, TemplateCreate
│   ├── artifact.py                  # Artifact, ArtifactCreate, ArtifactKind
│   ├── ai_usage.py                  # AiUsage, AiUsageCreate
│   ├── transformation.py            # Transformation, TransformOperation
│   ├── token_usage.py               # TokenUsage (legacy)
│   └── report.py                    # Report (legacy, Deprecated)
│
├── database/                        # SQLite CRUD layer (11 modules)
│   ├── connection.py                # DB initialization, table creation, migration
│   ├── user_db.py                   # User CRUD
│   ├── topic_db.py                  # Topic CRUD
│   ├── message_db.py                # Message CRUD (seq_no management)
│   ├── artifact_db.py               # Artifact CRUD (version management)
│   ├── template_db.py               # ✨ Template CRUD + transaction
│   ├── ai_usage_db.py               # AI usage tracking
│   ├── transformation_db.py         # Transformation history (MD→HWPX)
│   ├── token_usage_db.py            # Legacy token tracking
│   ├── report_db.py                 # Legacy reports
│   └── __init__.py                  # DB initialization export
│
└── utils/                           # Business logic & helpers (13 modules)
    ├── prompts.py                   # ✨ System Prompt central management
    ├── templates_manager.py         # ✨ HWPX file/Placeholder handling
    ├── claude_client.py             # Claude API call (Markdown response)
    ├── markdown_parser.py           # Markdown → structured data (dynamic sections)
    ├── markdown_builder.py          # Structured data → Markdown
    ├── hwp_handler.py               # HWPX modify/create (XML manipulation)
    ├── artifact_manager.py          # Artifact file management (store, hash)
    ├── file_utils.py                # File I/O utilities (write, read, hash)
    ├── md_handler.py                # Markdown file I/O
    ├── response_helper.py           # API standard response (success, error)
    ├── auth.py                      # JWT, password hashing
    └── meta_info_generator.py       # Placeholder metadata generation (future)
```

### Key Database Tables

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Topics table (conversation threads)
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    input_prompt TEXT NOT NULL,
    generated_title TEXT,
    language TEXT NOT NULL DEFAULT 'ko',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    role TEXT NOT NULL,                 -- user, assistant, system
    content TEXT NOT NULL,
    seq_no INTEGER NOT NULL,            -- sequence number (conversation order)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    UNIQUE(topic_id, seq_no)
);

-- Artifacts table
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    message_id INTEGER,
    kind TEXT NOT NULL,                 -- MD, HWPX, PDF
    locale TEXT NOT NULL,               -- language (ko, en)
    version INTEGER NOT NULL,           -- version number
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- ✨ Templates table (new)
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    prompt_user TEXT DEFAULT NULL,      -- ✨ Placeholder list
    prompt_system TEXT DEFAULT NULL,    -- ✨ Dynamic System Prompt
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Placeholders table
CREATE TABLE placeholders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    placeholder_key TEXT NOT NULL,      -- {{TITLE}}, {{SUMMARY}}, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
);

-- AI usage table
CREATE TABLE ai_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    message_id INTEGER,
    model TEXT NOT NULL,                -- claude-sonnet-4-5-20250929
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);
```

### Core API Endpoints

#### Topics Router (`/api/topics`)

```python
POST   /api/topics                         # Create topic
POST   /api/topics/generate                # Generate report (select template)
GET    /api/topics                         # List my topics
GET    /api/topics/{id}                    # Get topic details
PUT    /api/topics/{id}                    # Update topic
DELETE /api/topics/{id}                    # Delete topic
POST   /api/topics/{id}/ask                # Message chaining (conversation)
```

#### Templates Router (`/api/templates`)

```python
POST   /api/templates              # Upload template (HWPX)
GET    /api/templates              # List my templates
GET    /api/templates/{id}         # Get template details
DELETE /api/templates/{id}         # Delete template
GET    /api/admin/templates        # Admin: List all templates
```

#### Artifacts Router (`/api/artifacts`)

```python
GET    /api/artifacts/{id}                 # Get metadata
GET    /api/artifacts/{id}/content         # Get content (MD only)
GET    /api/artifacts/{id}/download        # Download file
POST   /api/artifacts/{id}/convert         # MD → HWPX conversion
GET    /api/artifacts/messages/{msg_id}/hwpx/download  # Auto-convert & download
```

---

## Core Functions & Step-by-Step Flows

### generate_topic_report() - 9-Step Flow

```python
@router.post("/generate", summary="Topic input → MD report generation")
async def generate_topic_report(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] Input validation
        - input_prompt required, minimum 3 characters

    [Step 2] Select System Prompt (based on template)
        IF topic_data.template_id:
            - Load Template
            - Fetch Placeholders
            - create_dynamic_system_prompt() call
        ELSE:
            - Use FINANCIAL_REPORT_SYSTEM_PROMPT

    [Step 3] Call Claude API
        - user_message = create_topic_context_message(input_prompt)
        - system_prompt = (Step 2 result)
        - response = claude.chat_completion([user_message], system_prompt)

    [Step 4] Parse Markdown
        - content = parse_markdown_to_content(response)
        - Dynamic section extraction (title, summary, background, ...)

    [Step 5] Create Topic
        - topic = TopicDB.create_topic(...)
        - Update generated_title

    [Step 6] Save messages
        - user_msg = MessageDB.create_message(USER)
        - assistant_msg = MessageDB.create_message(ASSISTANT)

    [Step 7] Save Artifact (MD)
        - md_text = build_report_md(content)
        - artifact = ArtifactDB.create_artifact(kind=MD)

    [Step 8] Record AI Usage
        - AiUsageDB.create_ai_usage(input_tokens, output_tokens, latency_ms)

    [Step 9] Return response
        - { topic_id, artifact_id, message_ids, usage }
    """
```

### ask() - 12-Step Flow (Message Chaining)

```python
@router.post("/{topic_id}/ask", summary="Message chaining (conversation)")
async def ask(
    topic_id: int,
    body: AskRequest,
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] Authorization & validation
        - Topic exists check
        - Ownership check (topic.user_id == current_user.id)
        - content required, minimum 1 character
        - content length validation (≤ 50,000 chars)

    [Step 2] Save user message
        - user_msg = MessageDB.create_message(topic_id, MessageCreate(role=USER))

    [Step 3] Select reference document
        IF body.artifact_id:
            - artifact = ArtifactDB.get_artifact_by_id(body.artifact_id)
            - Check authorization (artifact.topic_id == topic_id)
            - Verify type (kind == MD)
        ELSE:
            - artifact = ArtifactDB.get_latest_artifact_by_kind(topic_id, MD)

    [Step 4] Build context
        - all_messages = MessageDB.get_messages_by_topic(topic_id)
        - user_messages = [m for m in all_messages if m.role == USER]
        - If artifact_id specified → include up to that message only
        - Apply max_messages → recent N messages only

    [Step 5] Inject document content
        IF body.include_artifact_content AND artifact exists:
            - md_content = read(artifact.file_path)
            - artifact_message = "Current report(MD):\n\n{md_content}"
            - Add to context_messages

    [Step 6] Validate context size
        - total_chars = sum(len(m.content) for m in context_messages)
        - MAX_CONTEXT_CHARS = 50,000
        - Return error if exceeded

    [Step 7] Select System Prompt (priority order)
        IF body.system_prompt:
            - system_prompt = body.system_prompt
        ELIF body.template_id:
            - template = TemplateDB.get_template_by_id(body.template_id)
            - placeholders = PlaceholderDB.get_placeholders_by_template()
            - system_prompt = create_dynamic_system_prompt(placeholders)
        ELSE:
            - system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT

    [Step 8] Call Claude API
        - claude_messages = [topic_context] + [context_messages] + [user_msg]
        - response = claude.chat_completion(claude_messages, system_prompt)

    [Step 9] Save assistant message
        - assistant_msg = MessageDB.create_message(topic_id, MessageCreate(role=ASSISTANT))

    [Step 10] Save Artifact (MD)
        - result = parse_markdown_to_content(response)
        - md_text = build_report_md(result)
        - artifact = ArtifactDB.create_artifact(kind=MD, version++)

    [Step 11] Record AI Usage
        - AiUsageDB.create_ai_usage(...)

    [Step 12] Return response
        - {
            topic_id,
            user_message,
            assistant_message,
            artifact,
            usage { model, input_tokens, output_tokens, latency_ms }
          }
    """
```

### upload_template() - 9-Step Flow

```python
@router.post("", summary="HWPX template upload")
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] File validation
        - Check filename (.hwpx only)
        - Check file size (max 50MB)

    [Step 2] Validate HWPX file
        - TemplatesManager.validate_hwpx()
        - Check ZIP magic bytes (PK\\x03\\x04)

    [Step 3] Save file
        - Path: templates/user_{user_id}/template_{timestamp}.hwpx
        - Calculate SHA256 hash

    [Step 4] Extract Placeholders
        - TemplatesManager.extract_hwpx() → unpack to temp directory
        - TemplatesManager.extract_placeholders() → extract {{KEY}}
        - Result: ["{{TITLE}}", "{{SUMMARY}}", ...]

    [Step 5] Duplicate check
        - TemplatesManager.has_duplicate_placeholders()
        - Warn if duplicates found (don't reject)

    [Step 6] Generate metadata
        - prompt_user = ", ".join(unique_placeholders)
          → "TITLE, SUMMARY, BACKGROUND, ..."
        - placeholder_objs = [Placeholder(placeholder_key=ph) ...]
        - system_prompt = create_dynamic_system_prompt(placeholder_objs)
          → "You are a financial... {{TITLE}}... {{SUMMARY}}..."

    [Step 7] Save to DB (transaction)
        - TemplateDB.create_template_with_transaction(
            user_id,
            TemplateCreate(
              ..., prompt_user, prompt_system
            ),
            placeholder_keys
          )
        - Auto-rollback on failure

    [Step 8] Cleanup temp files
        - Delete temp unpack directory

    [Step 9] Return response
        - {
            id, title, filename, prompt_user, prompt_system,
            placeholders: [{ key, ... }, ...]
          }
    """
```

---

## E2E Workflows

### Scenario 1: Template Upload → Topic Creation → Report Generation

```
[1] User: Upload template file
POST /api/templates
- file: report_template.hwpx (binary)
- title: "Financial Report Template"
    ↓
[2] Backend: Save Template
- Validate HWPX file
- Extract Placeholders: {{TITLE}}, {{SUMMARY}}, ...
- Generate dynamic System Prompt
- Save to DB (Template + Placeholder + metadata)
✅ Response: { template_id: 1, placeholders: [...] }
    ↓
[3] User: Generate report (select template)
POST /api/topics/generate
{
  "input_prompt": "Digital Banking Trends 2025",
  "template_id": 1  ← Selected Template
}
    ↓
[4] Backend: Generate dynamic System Prompt & call Claude
a) Load Template #1
b) Fetch Placeholders: [{{TITLE}}, {{SUMMARY}}, ...]
c) create_dynamic_system_prompt(placeholders)
   → "You are a financial... {{TITLE}} to include..."
d) Call Claude API:
   system_prompt = (dynamic System Prompt)
   user_message = "Write report on Digital Banking Trends..."
e) Response: Markdown text
    ↓
[5] Backend: Parse Markdown & save report
a) parse_markdown_to_content(response)
   → {title, summary, background, main_content, ...}
b) build_report_md(content) → Markdown format
c) Create Topic, Message, Artifact (MD)
d) Record AI Usage
✅ Response: { topic_id: 42, artifact_id: 100 }
    ↓
[6] User: Convert MD → HWPX & download
POST /api/artifacts/100/convert
→ Generate HWPX file
GET /api/artifacts/{hwpx_artifact_id}/download
→ Download report (report.hwpx)
```

### Scenario 2: Conversational Message Chaining (Ask)

```
[1] User: Ask question (select template, specify reference document)
POST /api/topics/42/ask
{
  "content": "Explain this section in more detail",
  "template_id": 1,              ← Template selection
  "artifact_id": 100,            ← Reference MD document
  "include_artifact_content": true,  ← Include document content
  "max_messages": 10             ← Context limit
}
    ↓
[2] Backend: Build context
a) Check authorization: User owns Topic
b) Save user message
c) Collect context messages:
   - If artifact_id specified → include only up to that message
   - Apply max_messages → recent N messages only
d) Inject reference document content:
   "Current report(MD):\n\n[artifact content]"
    ↓
[3] Backend: Select System Prompt (priority order)
Priority 1: body.system_prompt (explicit)
Priority 2: body.template_id (template-based)
  → Load Template
  → Fetch Placeholders
  → create_dynamic_system_prompt()
Priority 3: FINANCIAL_REPORT_SYSTEM_PROMPT (default)
    ↓
[4] Backend: Call Claude API
a) claude_messages = [topic_context] + [previous_msgs]
b) claude.chat_completion(claude_messages, system_prompt)
c) Response: Markdown text
    ↓
[5] Backend: Save response & create artifact
a) Save Assistant message
b) Parse Markdown & build report
c) Create Artifact (MD v2)
d) Record AI Usage
✅ Response: {
     topic_id, user_message, assistant_message,
     artifact, usage (tokens, latency)
   }
    ↓
[6] User: Continue conversation or download
- Continue: POST /api/topics/42/ask (new message)
- Download latest MD: GET /api/artifacts/{artifact_id}/...
- Convert to HWPX: POST /api/artifacts/{artifact_id}/convert
```

---

## Development Checklist

### ✅ Step 0: Unit Spec (Mandatory, First)

**Cannot proceed without completing this step.**

```
User Request
    ↓
Claude: Create Unit Spec
    ↓
[Location] backend/doc/specs/YYYYMMDD_feature_name.md
[Template] backend/doc/Backend_UnitSpec.md
    ↓
User: Review & Approve Spec
    ↓
Approved ✅ → Proceed to Step 1
OR
Revision → Update spec & resubmit
```

**Required items in Unit Spec:**
- [ ] Requirements summary (Purpose, Type, Core Requirements)
- [ ] Implementation target files (New/Change/Reference)
- [ ] Flow diagram (Mermaid)
- [ ] Test plan (minimum 3 test cases)
- [ ] Error handling scenarios

---

### ✅ Step 1: Implementation (After Unit Spec Approval)

**Only proceed after Step 0 approval.**

#### 1-1. Define Data Models
- [ ] Define Pydantic models (`models/*.py`)
- [ ] Type hints complete & accurate
- [ ] Optional/required fields clear

#### 1-2. Database Logic
- [ ] Implement DB CRUD methods (`database/*.py`)
- [ ] Handle transactions (when needed)
- [ ] Parameterize SQL queries (prevent SQL injection)
- [ ] Consider indexes

#### 1-3. Router/API Implementation
- [ ] Implement router functions (`routers/*.py`)
- [ ] Use **only** `success_response()` / `error_response()`
- [ ] Use **only** `ErrorCode` constants
- [ ] Correct HTTP status codes

#### 1-4. Logging & Documentation
- [ ] Add logging (`logger.info()`, `logger.warning()`, `logger.error()`)
- [ ] Write DocStrings (Google style, all functions)
- [ ] Document parameters, return values, exceptions

#### 1-5. Write Tests
- [ ] Implement tests (`tests/test_*.py`)
- [ ] Cover all test cases from Unit Spec
- [ ] Test both success & error scenarios
- [ ] **All tests MUST pass**

---

### ✅ Step 2: Validation & Final Checks (After Implementation)

#### 2-1. Check Impact on Existing Code
- [ ] Run existing tests (no new failures)
- [ ] Verify compatibility (no breaking changes)
- [ ] Check dependency conflicts

#### 2-2. Update Documentation
- [ ] Update CLAUDE.md (new endpoints, models, DB)
- [ ] Update README.md if needed

#### 2-3. Git Commit
- [ ] Include Unit Spec document (`backend/doc/specs/YYYYMMDD_*.md`)
- [ ] Clear commit message: feat/fix/refactor
- [ ] Reference Unit Spec filename in commit

---

## Claude Model Selection (v2.5)

### Overview

The ClaudeClient now supports **three Claude models** for different use cases:

| Model | Name | Use Case | Response Time | Cost |
|-------|------|----------|----------------|------|
| **Sonnet** | `claude-sonnet-4-5-20250929` | Default, detailed reports | 3-10s | Standard |
| **Haiku** | `claude-haiku-4-5-20251001` | Fast summaries, overviews | 1-3s | Low |
| **Opus** | `claude-opus-4-1-20250805` | Complex analysis, reasoning | 5-15s | High |

### Configuration

Set these environment variables in `.env`:

```bash
# Default model (high quality)
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Fast model (quick response < 2 seconds)
CLAUDE_FAST_MODEL=claude-haiku-4-5-20251001

# Reasoning model (complex analysis)
CLAUDE_REASONING_MODEL=claude-opus-4-1-20250805
```

### ClaudeClient Methods

```python
from app.utils.claude_client import ClaudeClient

client = ClaudeClient()

# 1. chat_completion() - Uses Sonnet (default)
response, input_tokens, output_tokens = client.chat_completion(messages)

# 2. chat_completion_fast() - Uses Haiku (fast responses)
response, input_tokens, output_tokens = client.chat_completion_fast(messages)

# 3. chat_completion_reasoning() - Uses Opus (complex analysis)
response, input_tokens, output_tokens = client.chat_completion_reasoning(messages)
```

### Endpoint-to-Model Mapping

| Endpoint | Method | Model | Reason |
|----------|--------|-------|--------|
| POST `/api/topics/generate` | `chat_completion()` | Sonnet | Detailed report generation |
| POST `/api/topics/{id}/ask` | `chat_completion()` | Sonnet | Context-aware responses |
| POST `/api/topics/plan` | `chat_completion_fast()` | **Haiku** | **Quick planning (< 2s)** |

### Implementation Details

- **Location:** [app/utils/claude_client.py](app/utils/claude_client.py)
- **Shared Logic:** `_call_claude()` method eliminates code duplication
- **Token Tracking:** All methods update `last_input_tokens`, `last_output_tokens`, `last_total_tokens`
- **Error Handling:** Consistent exception handling across all methods

### Testing

All three methods are tested with:
- ✅ 8+ unit tests covering initialization, method calls, and token tracking
- ✅ 373+ passing tests (no breaking changes)
- ✅ Token usage tracking verified
- ✅ Custom system prompt support

See [backend/tests/test_utils_claude_client.py](tests/test_utils_claude_client.py) for test cases.

---

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Napoleon - Sphinx extension for Google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Unit Spec - Claude Model Selection](doc/specs/20251112_claude_model_selection.md)

---

**Last Updated:** November 13, 2025
**Version:** 2.5.0
**Effective Date:** Immediately

**Recent Session Notes (2025-11-11):**
- ✅ Test Environment Setup documentation added
- ✅ Python interpreter configuration details (backend/.venv/bin/python)
- ✅ Claude Code Testing Checklist with verification steps
- ✅ Common issues & solutions troubleshooting table
- ✅ Package manager (uv) configuration guidelines

**Previous Session Notes (2025-11-10):**
- ✅ Comprehensive backend architecture documentation
- ✅ Added core functions with 9, 12, and 9-step flows
- ✅ Documented all E2E workflows (2 scenarios)
- ✅ Added development checklist (Step 0, 1, 2)
- ✅ All content migrated from root CLAUDE.md to English
