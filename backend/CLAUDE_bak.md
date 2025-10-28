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

**All Python functions and classes must include a Google-style DocString.**

#### Google Style DocString Format

**Function DocString Example:**

```python
def generate_report(topic: str, user_id: int, options: dict = None) -> dict:
    """Generates a report and returns metadata.

    Calls the Claude API to generate report content for the given topic,
    converts it into an HWPX file, and stores it in the database.

    Args:
        topic: Report generation topic (e.g., "Digital Banking Trends 2025")
        user_id: ID of the user creating the report
        options: Optional report generation settings
            - template_id: ID of the template to use
            - format: Output format (default: "hwpx")

    Returns:
        Dictionary containing information about the generated report:
            - id: Report ID
            - filename: Generated file name
            - file_path: File storage path
            - created_at: Creation timestamp

    Raises:
        ValueError: When the topic is an empty string
        FileNotFoundError: When the template file is not found
        APIError: When the Claude API call fails

    Examples:
        >>> report = generate_report("AI Trends", user_id=1)
        >>> print(report['filename'])
        'report_20251027_103954.hwpx'

    Note:
        This function calls the Claude API, which typically takes 5-15 seconds.
    """
    pass
```

**Class DocString Example:**

```python
class ClaudeClient:
    """Client class for generating report content using the Claude API.

    This class communicates with Anthropic's Claude API to generate structured
    report content and track token usage.

    Attributes:
        api_key: Claude API authentication key
        model: Claude model name (default: claude-sonnet-4-5-20250929)
        client: Anthropic API client instance
        last_input_tokens: Number of input tokens in the last API call
        last_output_tokens: Number of output tokens in the last API call
        last_total_tokens: Total number of tokens used in the last API call

    Examples:
        >>> client = ClaudeClient()
        >>> content = client.generate_report("Digital Finance Trends")
        >>> print(content['title'])
        'Digital Finance Innovation Report'
        >>> print(client.last_total_tokens)
        4500
    """

    def __init__(self):
        """Initializes the Claude client.

        Loads the API key and model name from environment variables,
        initializes the Anthropic client, and resets token usage counters.

        Raises:
            ValueError: If the CLAUDE_API_KEY environment variable is not set
        """
        pass
```

**Simple Function (One-line DocString):**

```python
def get_user_by_id(user_id: int) -> User:
    """Retrieves a user by ID."""
    pass
```

#### DocString Sections

| Section | Required | Description |
|---------|----------|-------------|
| **Summary** | Yes | Short explanation of the function/class (first line) |
| **Description** | Optional | Detailed explanation after one blank line |
| **Args** | Yes (if parameters exist) | Description of parameters |
| **Returns** | Yes (if return value exists) | Description of return value |
| **Raises** | Recommended (if exceptions possible) | Possible exceptions |
| **Yields** | Yes (if generator) | Description of yielded values |
| **Examples** | Optional (recommended for complex functions) | Usage examples (doctest format) |
| **Note / Warning / See Also** | Optional | Additional information or references |

#### DocString Writing Rules

1. **Summary (first line):**
   - Summarize the function/class in one sentence
   - End with a period
   - Start with an imperative verb (e.g., "Generates," "Returns," "Calculates")

2. **Args:**
   - Format: `parameter_name: description`
   - Omit types (already defined via type hints)
   - Indicate optional parameters with "(optional)" or mention default values
   - Use indentation for complex structures

3. **Returns:**
   - Describe the structure and meaning of the return value
   - For dicts/objects, list key fields
   - If returns `None`, state it explicitly

4. **Raises:**
   - List exceptions and when they occur
   - Format: `ExceptionType: Condition`

5. **Examples:**
   - Use doctest format (`>>>` prompt)
   - Provide runnable examples showing both input and output

#### Incorrect Examples (Avoid)

```python
# ❌ Example 1: No DocString
def create_report(topic, user_id):
    return report

# ❌ Example 2: Incomplete
def create_report(topic: str, user_id: int) -> dict:
    """Creates report"""
    pass

# ❌ Example 3: Wrong format (non-Google style)
def create_report(topic: str) -> dict:
    """
    Creates report
    @param topic: Topic
    @return: Report
    """
    pass
```

#### Correct Examples (Recommended)

```python
# ✅ Example 1: Complete DocString
def create_report(topic: str, user_id: int, template_id: int = None) -> dict:
    """Generates a report based on the given topic.

    Uses the Claude API to generate report content and saves it as an HWPX file.

    Args:
        topic: Report topic
        user_id: User ID
        template_id: Template ID (optional, default: None)

    Returns:
        Generated report information:
            - id: Report ID
            - filename: File name
            - file_path: File path

    Raises:
        ValueError: When topic is empty
        APIError: When Claude API call fails
    """
    pass

# ✅ Example 2: Simple function
def validate_email(email: str) -> bool:
    """Validates the email format."""
    pass

# ✅ Example 3: Generator function
def get_reports_batch(user_id: int, batch_size: int = 100):
    """Retrieves user reports in batch units.

    Args:
        user_id: User ID
        batch_size: Number of reports per batch (default: 100)

    Yields:
        List of report objects (up to batch_size)

    Examples:
        >>> for batch in get_reports_batch(user_id=1, batch_size=50):
        ...     process_batch(batch)
    """
    pass
```

### Private Functions/Methods

Private functions/methods (prefixed with `_`) must also include DocStrings, but can be shorter.

```python
def _parse_xml_content(self, xml_path: str) -> dict:
    """Parses an XML file into a dictionary.

    Args:
        xml_path: XML file path

    Returns:
        Parsed XML content as a dictionary
    """
    pass
```

### Type Hints and DocStrings

Use type hints for types and DocStrings for meaning and constraints.

```python
# ✅ Recommended
def calculate_tokens(input_text: str, model: str = "gpt-4") -> int:
    """Calculates the number of tokens in the input text.

    Args:
        input_text: Text to calculate tokens from
        model: Model name (default: "gpt-4")

    Returns:
        Calculated token count
    """
    pass
```

### Scope

These DocString rules apply to:

- `app/routers/*.py` — all API router functions
- `app/models/*.py` — Pydantic model classes
- `app/database/*.py` — database CRUD functions
- `app/utils/*.py` — utility and helper functions
- `*.py` — all Python files under the backend directory

### Exceptions

You may omit DocStrings in the following cases:

1. `__init__.py` files containing only imports
2. Very simple one-line getters/setters
3. Test functions (DocStrings are recommended for complex tests)

---

## Testing Guidelines

### Test Environment

**Test Frameworks:**

- `pytest` – main testing framework
- `pytest-cov` – code coverage measurement
- `pytest-asyncio` – asynchronous test support
- `pytest-mock` – mocking utility
- `httpx==0.27.2` – HTTP client for FastAPI `TestClient`

**Install dependencies:**

```bash
cd backend
uv pip install -r requirements-dev.txt
```

---

### Test Structure

```
backend/
├── tests/
│   ├── conftest.py                  # Common fixtures
│   ├── test_utils_auth.py           # 8 tests - Auth utilities (password hashing, JWT)
│   ├── test_utils_claude_client.py  # 17 tests - Claude API client (generate, parse, mock)
│   ├── test_utils_hwp_handler.py    # 21 tests - HWPX file handling (generate, format, XML)
│   ├── test_routers_auth.py         # 6 tests - Auth API endpoints (register, login, me)
│   └── test_routers_reports.py      # 16 tests - Reports API (generate, list, download)
├── pytest.ini                       # pytest configuration
└── requirements-dev.txt             # dev/test dependencies
```

**Total: 60 tests (57 passed, 3 skipped)**

---

### Running Tests

**Run all tests:**

```bash
cd backend
uv run pytest tests/ -v
```

**Run specific file:**

```bash
uv run pytest tests/test_utils_auth.py -v
```

**Run specific test case:**

```bash
uv run pytest tests/test_utils_auth.py::TestPasswordHashing::test_hash_password -v
```

**Run with coverage report:**

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

**Run with debug output:**

```bash
uv run pytest tests/ -v -s
```

---

### Test Markers

```bash
# Unit tests only
uv run pytest -m unit -v

# API tests only
uv run pytest -m api -v

# Auth-related tests only
uv run pytest -m auth -v

# Integration tests only
uv run pytest -m integration -v
```

---

### Key Fixtures (conftest.py)

**`test_db`:**
- Creates a temporary SQLite database per test
- Automatically cleans up after execution

**`client`:**
- Provides a FastAPI `TestClient` instance
- Depends on `test_db`

**`test_user_data` / `test_admin_data`:**
- Dictionary of mock user and admin test data

**`create_test_user` / `create_test_admin`:**
- Creates a test user/admin
- Returns a `User` object

**`auth_headers` / `admin_auth_headers`:**
- Generates JWT authentication headers
- Format: `{"Authorization": "Bearer <token>"}`

**`temp_dir`:**
- Creates and cleans up a temporary directory automatically

**`simple_hwpx_template`:**
- Creates a simple HWPX template file for testing
- Used by HWP handler tests

---

### Current Coverage Status

**Overall Coverage: 70%** ✅ (Goal: ≥70%)

**Test Statistics:**
- Total Tests: 60
- Passed: 57 (95%)
- Skipped: 3 (DELETE endpoint not implemented)
- Failed: 0

**Module Coverage:**

| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| `utils/claude_client.py` | 100% | 85% | ✅ Exceeded |
| `routers/reports.py` | 88% | 80% | ✅ Exceeded |
| `utils/auth.py` | 87% | 85% | ✅ Exceeded |
| `utils/hwp_handler.py` | 83% | 85% | ✅ Near target |
| `database/report_db.py` | 75% | 70% | ✅ Achieved |
| `database/user_db.py` | 69% | 70% | ⚠️ Near target |
| `routers/auth.py` | 68% | 70% | ⚠️ Near target |
| `database/token_usage_db.py` | 67% | 70% | ⚠️ Near target |
| `database/connection.py` | 100% | 70% | ✅ Exceeded |

**Coverage Improvement:**
- Initial: 48%
- Current: 70%
- Increase: +22%

---

### Mocking Guidelines

#### Mocking Claude API

**Always mock Claude API calls to avoid actual API usage during tests.**

```python
from unittest.mock import Mock, patch

@patch('app.utils.claude_client.Anthropic')
def test_generate_report(mock_anthropic_class):
    """Test report generation with mocked Claude API"""
    # Setup mock client
    mock_client = Mock()
    mock_anthropic_class.return_value = mock_client

    # Setup mock response
    mock_response = Mock()
    mock_response.content = [
        Mock(text="""[제목]
디지털 뱅킹 혁신 보고서
[배경제목]
추진 배경
[배경]
디지털 금융 환경의 변화...""")
    ]
    mock_response.usage = Mock(input_tokens=1500, output_tokens=3200)
    mock_client.messages.create.return_value = mock_response

    # Test
    client = ClaudeClient()
    result = client.generate_report("Test Topic")

    # Assertions
    assert "title" in result
    assert result["title"] == "디지털 뱅킹 혁신 보고서"
    assert client.last_input_tokens == 1500
```

**Important:** Use `@patch('app.utils.claude_client.Anthropic')` not `@patch('anthropic.Anthropic')`. Always patch at the point of use.

#### Mocking HWP Handler

```python
@patch('app.routers.reports.HWPHandler')
def test_with_mocked_hwp(mock_hwp_class, temp_dir):
    """Test with mocked HWPX file generation"""
    # Setup mock handler
    mock_handler = Mock()
    mock_hwp_class.return_value = mock_handler

    # Create test file
    test_file = os.path.join(temp_dir, "test.hwpx")
    with open(test_file, 'wb') as f:
        f.write(b'test content')

    # Mock return value
    mock_handler.generate_report.return_value = test_file

    # Test
    handler = HWPHandler(template_path="dummy", temp_dir=temp_dir, output_dir=temp_dir)
    result = handler.generate_report({"title": "Test"})

    assert result == test_file
```

#### Mocking Best Practices

**DO ✅:**
- Always mock external API calls (Claude API, etc.)
- Use `@patch('app.utils.module.Class')` for proper module patching
- Mock at the point of use, not at the import location
- Provide complete mock responses with all required attributes
- Test both success and failure scenarios

**DON'T ❌:**
- Don't call actual APIs in tests
- Don't use incorrect patch paths
- Don't forget to set up mock return values
- Don't skip testing error handling

---

### Test Writing Patterns

#### 1. Unit Tests

```python
import pytest

@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Password hashing tests"""

    def test_hash_password(self):
        """Tests that password hashing works correctly"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
```

#### 2. API Tests

```python
@pytest.mark.api
class TestAuthRouter:
    """Authentication API tests"""

    def test_register_success(self, client):
        """Successful user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "NewUser",
                "password": "NewUser123!@#"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"
```

#### 3. Exception Tests

```python
def test_invalid_token(self):
    """Tests invalid token handling"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("invalid.token")

    assert exc_info.value.status_code == 401
```

#### 4. Authenticated Endpoint Tests

```python
def test_authenticated_endpoint(self, client, auth_headers):
    """Tests endpoint requiring authentication"""
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@example.com"
```

#### 5. Integration Tests

```python
@pytest.mark.integration
class TestReportLifecycle:
    """Full report generation lifecycle test"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_full_lifecycle(self, mock_hwp, mock_claude, client, auth_headers):
        """Test: generate → list → download"""
        # Setup mocks
        mock_claude.return_value.generate_report.return_value = {...}
        mock_hwp.return_value.generate_report.return_value = "/path/test.hwpx"

        # 1. Generate report
        response = client.post("/api/reports/generate",
                              headers=auth_headers,
                              json={"topic": "Test"})
        assert response.status_code == 200
        report_id = response.json()["id"]

        # 2. List reports
        response = client.get("/api/reports/my-reports", headers=auth_headers)
        assert any(r["id"] == report_id for r in response.json()["reports"])

        # 3. Download report
        response = client.get(f"/api/reports/download/{report_id}",
                             headers=auth_headers)
        assert response.status_code == 200
```

---

### Code Coverage Goals

- **Overall:** ≥ 70% ✅
- **Core business logic:** ≥ 90%
- **Utility functions:** ≥ 85%

**Coverage reports:**

```bash
# Terminal report
uv run pytest tests/ --cov=app --cov-report=term-missing

# HTML report
uv run pytest tests/ --cov=app --cov-report=html

# XML report (for CI/CD)
uv run pytest tests/ --cov=app --cov-report=xml
```

---

### Best Practices

**DO ✅**

- Keep each test self-contained and independent
- Use descriptive, readable names for tests
- Use fixtures to avoid redundancy
- Use a fresh DB per test
- Use `pytest.raises()` for exception checks
- Validate full API responses (structure and values)
- Maintain coverage ≥ 70%
- Mock all external API calls
- Test both success and failure scenarios
- Use proper patch paths (`app.utils.module.Class`)

**DON'T ❌**

- Never use the production database
- Never call external APIs directly (use mocks)
- Don't make tests depend on each other
- Don't rely on execution order
- Avoid hardcoded dates/times (use freezegun if needed)
- Don't overstuff a single test with too many checks
- Don't use incorrect mock paths
- Don't skip error handling tests

---

### CI/CD Integration

The workflow file `.github/workflows/backend-tests.yml` automatically runs all tests.

**Triggers:**

- Push to `main` or `dev` branch
- Pull request targeting `main` or `dev`
- File changes under `backend/**` or `shared/**`

**Execution steps:**

1. Set up Python 3.12 environment
2. Install `uv`
3. Install dependencies
4. Load environment variables
5. Run pytest with coverage
6. Upload results to Codecov

---

### Writing Tests for New Features

**1. Create a new test file**

```bash
touch tests/test_new_feature.py
```

**2. Write test cases** (TDD recommended)

- Success scenarios
- Failure scenarios
- Edge cases
- Exception handling

**3. Implement the feature**

**4. Run the test**

```bash
uv run pytest tests/test_new_feature.py -v
```

**5. Check coverage**

```bash
uv run pytest tests/test_new_feature.py --cov=app.module_name --cov-report=term-missing
```

---

### Troubleshooting

**1. `ModuleNotFoundError: No module named 'shared'`**

- Check `PATH_PROJECT_HOME` in `conftest.py`
- Ensure `.env` defines `PATH_PROJECT_HOME`

**2. `TypeError: Client.__init__() unexpected keyword`**

```bash
uv pip install httpx==0.27.2
```

**3. `HTTPException` not raised properly**

```python
with pytest.raises(HTTPException) as exc_info:
    decode_access_token(invalid_token)
assert exc_info.value.status_code == 401
```

**4. `database is locked` error**

- Ensure `test_db` fixture creates a new DB per test
- Always call `.close()` after DB use

**5. Mock not working (actual API called)**

- Check patch path: use `@patch('app.utils.module.Class')` not `@patch('module.Class')`
- Ensure mock is set up before creating the client instance

---

### Test Data

**Normal User:**

- Email: `test@example.com`
- Username: `TestUser`
- Password: `Test1234!@#`

**Admin User:**

- Email: `admin@example.com`
- Username: `Admin`
- Password: `Admin1234!@#`

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
