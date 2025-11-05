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

**Overall Coverage: 70%** ✅ (Target: ≥70%)

- **Total Tests:** 60 (57 passed, 3 skipped)
- **Test Files:** 5 files covering auth, claude_client, hwp_handler, and API endpoints
- **Coverage Increase:** +22% (from 48% to 70%)

**Top Modules:**
- `utils/claude_client.py`: 100% ✅
- `routers/reports.py`: 88% ✅
- `utils/auth.py`: 87% ✅
- `utils/hwp_handler.py`: 83% ⚠️

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

## DocString Review Checklist

- [ ] Does every public function/class have a DocString?
- [ ] Is the summary line clear and concise?
- [ ] Are Args and Returns sections complete?
- [ ] Is there a Raises section if exceptions may occur?
- [ ] Do complex functions include Examples?
- [ ] Is it written in English and follows Google style?

---

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Napoleon - Sphinx extension for Google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

**Last Updated:** October 28, 2025
**Version:** 1.2
**Effective Date:** Immediately
