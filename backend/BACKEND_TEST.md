# Backend Testing Guide

Comprehensive testing guide for the HWP Report Generator backend.

---

## Table of Contents

1. [Test Environment](#test-environment)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Markers](#test-markers)
5. [Key Fixtures](#key-fixtures)
6. [Current Coverage Status](#current-coverage-status)
7. [Mocking Guidelines](#mocking-guidelines)
8. [Test Writing Patterns](#test-writing-patterns)
9. [Code Coverage Goals](#code-coverage-goals)
10. [Best Practices](#best-practices)
11. [CI/CD Integration](#cicd-integration)
12. [Writing Tests for New Features](#writing-tests-for-new-features)
13. [Troubleshooting](#troubleshooting)
14. [Test Data](#test-data)

---

## Test Environment

### Test Frameworks

- **pytest** – main testing framework
- **pytest-cov** – code coverage measurement
- **pytest-asyncio** – asynchronous test support
- **pytest-mock** – mocking utility
- **httpx==0.27.2** – HTTP client for FastAPI `TestClient`

### Installation

Install all test dependencies:

```bash
cd backend
uv pip install -r requirements-dev.txt
```

Or with standard pip:

```bash
pip install -r requirements-dev.txt
```

---

## Test Structure

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

**Total: 60 tests**
- Passed: 57 (95%)
- Skipped: 3 (DELETE endpoint not yet implemented)
- Failed: 0

---

## Running Tests

### Basic Commands

**Run all tests:**

```bash
cd backend
uv run pytest tests/ -v
```

**Run specific file:**

```bash
uv run pytest tests/test_utils_auth.py -v
```

**Run specific test class:**

```bash
uv run pytest tests/test_utils_auth.py::TestPasswordHashing -v
```

**Run specific test case:**

```bash
uv run pytest tests/test_utils_auth.py::TestPasswordHashing::test_hash_password -v
```

### Coverage Reports

**Terminal report with missing lines:**

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

**HTML report (opens in browser):**

```bash
uv run pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

**XML report (for CI/CD):**

```bash
uv run pytest tests/ --cov=app --cov-report=xml
```

### Debug Mode

**Run with print statements visible:**

```bash
uv run pytest tests/ -v -s
```

**Stop on first failure:**

```bash
uv run pytest tests/ -v -x
```

**Show local variables on failure:**

```bash
uv run pytest tests/ -v -l
```

---

## Test Markers

Markers allow selective test execution.

### Available Markers

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

### Combining Markers

```bash
# Unit AND auth tests
uv run pytest -m "unit and auth" -v

# API OR integration tests
uv run pytest -m "api or integration" -v

# Exclude integration tests
uv run pytest -m "not integration" -v
```

---

## Key Fixtures

Fixtures are defined in `tests/conftest.py` and automatically available to all tests.

### Database Fixtures

**`test_db`**

Creates a temporary SQLite database for each test session.

```python
def test_create_user(test_db):
    """Test DB is automatically created and cleaned up"""
    user = UserDB.create_user(...)
    assert user.id is not None
```

**`client`**

Provides a FastAPI `TestClient` instance with the test database.

```python
def test_api_endpoint(client):
    """Use client to test API endpoints"""
    response = client.get("/api/auth/me")
    assert response.status_code == 200
```

### User Fixtures

**`test_user_data`**

Dictionary containing test user information:

```python
{
    "email": "test@example.com",
    "username": "TestUser",
    "password": "Test1234!@#"
}
```

**`test_admin_data`**

Dictionary containing test admin information:

```python
{
    "email": "admin@example.com",
    "username": "Admin",
    "password": "Admin1234!@#",
    "is_admin": True
}
```

**`create_test_user`**

Creates a test user in the database.

```python
def test_user_operations(create_test_user):
    """User is automatically created"""
    user = create_test_user
    assert user.email == "test@example.com"
```

**`create_test_admin`**

Creates a test admin user in the database.

### Authentication Fixtures

**`auth_headers`**

Generates JWT authentication headers for the test user.

```python
def test_protected_endpoint(client, auth_headers):
    """Use auth_headers for authenticated requests"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

Returns: `{"Authorization": "Bearer <jwt_token>"}`

**`admin_auth_headers`**

Generates JWT authentication headers for the admin user.

### File System Fixtures

**`temp_dir`**

Creates a temporary directory that's automatically cleaned up after the test.

```python
def test_file_operations(temp_dir):
    """temp_dir is created and cleaned up automatically"""
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, 'w') as f:
        f.write("test content")
    assert os.path.exists(file_path)
    # temp_dir is automatically deleted after test
```

**`simple_hwpx_template`**

Creates a simple HWPX template file for testing.

```python
def test_hwp_operations(simple_hwpx_template, temp_dir):
    """Use pre-created HWPX template"""
    handler = HWPHandler(
        template_path=simple_hwpx_template,
        temp_dir=temp_dir,
        output_dir=temp_dir
    )
    result = handler.generate_report({...})
    assert os.path.exists(result)
```

---

## Current Coverage Status

**Last Updated:** October 28, 2025

### Overall Metrics

**Overall Coverage: 70%** ✅ (Goal: ≥70%)

**Test Statistics:**
- Total Tests: 60
- Passed: 57 (95%)
- Skipped: 3 (DELETE endpoint not implemented)
- Failed: 0

### Module Coverage

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

### Coverage Improvement

- **Initial:** 48%
- **Current:** 70%
- **Increase:** +22%

### Priority Improvements

Modules needing attention to reach 70% target:
1. `database/user_db.py` - 69% (need +1%)
2. `routers/auth.py` - 68% (need +2%)
3. `database/token_usage_db.py` - 67% (need +3%)

---

## Mocking Guidelines

### Why Mock?

- Avoid calling real external APIs (cost, rate limits, flaky tests)
- Fast test execution
- Deterministic results
- Test error scenarios easily

### Mocking Claude API

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
    assert client.last_output_tokens == 3200
```

**Important:** Use `@patch('app.utils.claude_client.Anthropic')` not `@patch('anthropic.Anthropic')`. Always patch at the point of use.

### Mocking HWP Handler

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
    mock_handler.generate_report.assert_called_once()
```

### Mocking Best Practices

**DO ✅**

- Always mock external API calls (Claude API, payment gateways, etc.)
- Use `@patch('app.utils.module.Class')` for proper module patching
- Mock at the point of use, not at the import location
- Provide complete mock responses with all required attributes
- Test both success and failure scenarios
- Verify mock was called with expected arguments
- Use `side_effect` for testing exceptions

**DON'T ❌**

- Don't call actual APIs in tests
- Don't use incorrect patch paths (e.g., `@patch('anthropic.Anthropic')` instead of `@patch('app.utils.claude_client.Anthropic')`)
- Don't forget to set up mock return values
- Don't skip testing error handling
- Don't make mocks too complex (refactor if needed)

### Common Mock Patterns

**Mocking exceptions:**

```python
@patch('app.utils.claude_client.Anthropic')
def test_api_error(mock_anthropic_class):
    """Test Claude API error handling"""
    mock_client = Mock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API Error")

    client = ClaudeClient()
    with pytest.raises(Exception) as exc_info:
        client.generate_report("Test")

    assert "Claude API 호출 중 오류 발생" in str(exc_info.value)
```

**Mocking with multiple return values:**

```python
mock_function.side_effect = [
    {"result": "first call"},
    {"result": "second call"},
    {"result": "third call"}
]
```

---

## Test Writing Patterns

### 1. Unit Tests

Test individual functions/methods in isolation.

```python
import pytest
from app.utils.auth import hash_password, verify_password

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

    def test_verify_password_success(self):
        """Tests password verification with correct password"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Tests password verification with wrong password"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False
```

### 2. API Tests

Test API endpoints using the `client` fixture.

```python
import pytest

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
        assert data["username"] == "NewUser"

    def test_register_duplicate_email(self, client, create_test_user):
        """Registration fails with duplicate email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",  # Already exists
                "username": "NewUser",
                "password": "NewUser123!@#"
            }
        )
        assert response.status_code == 400
```

### 3. Exception Tests

Test error handling and exceptions.

```python
import pytest
from fastapi import HTTPException
from app.utils.auth import decode_access_token

def test_invalid_token(self):
    """Tests invalid token handling"""
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("invalid.token")

    assert exc_info.value.status_code == 401
    assert "인증 토큰이 유효하지 않습니다" in str(exc_info.value.detail)
```

### 4. Authenticated Endpoint Tests

Test endpoints requiring authentication.

```python
@pytest.mark.api
def test_authenticated_endpoint(client, auth_headers):
    """Tests endpoint requiring authentication"""
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@example.com"
    assert "password" not in data  # Password should never be in response

def test_authenticated_endpoint_without_auth(client):
    """Tests protected endpoint without authentication"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403
```

### 5. Integration Tests

Test complete workflows across multiple components.

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.integration
class TestReportLifecycle:
    """Full report generation lifecycle test"""

    @patch('app.routers.reports.ClaudeClient')
    @patch('app.routers.reports.HWPHandler')
    def test_full_lifecycle(self, mock_hwp, mock_claude, client, auth_headers, temp_dir):
        """Test: generate → list → download"""
        # Setup mocks
        mock_claude_response = {
            "title": "Test Report",
            "summary": "Summary",
            "background": "Background",
            "main_content": "Content",
            "conclusion": "Conclusion"
        }
        mock_claude.return_value.generate_report.return_value = mock_claude_response

        test_file = os.path.join(temp_dir, "test.hwpx")
        with open(test_file, 'wb') as f:
            f.write(b'test content')
        mock_hwp.return_value.generate_report.return_value = test_file

        # 1. Generate report
        response = client.post(
            "/api/reports/generate",
            headers=auth_headers,
            json={"topic": "Test Topic"}
        )
        assert response.status_code == 200
        report_id = response.json()["id"]

        # 2. List reports
        response = client.get("/api/reports/my-reports", headers=auth_headers)
        assert response.status_code == 200
        reports = response.json()["reports"]
        assert any(r["id"] == report_id for r in reports)

        # 3. Download report
        response = client.get(
            f"/api/reports/download/{report_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
```

---

## Code Coverage Goals

### Targets by Category

| Category | Target | Current | Status |
|----------|--------|---------|--------|
| **Overall** | ≥ 70% | 70% | ✅ Met |
| **Core business logic** | ≥ 90% | - | - |
| **Utility functions** | ≥ 85% | 87% | ✅ Exceeded |
| **API routers** | ≥ 80% | 78% | ⚠️ Near |
| **Database operations** | ≥ 70% | 70% | ✅ Met |

### Coverage Reports

**Terminal report with missing lines:**

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

**HTML report (interactive):**

```bash
uv run pytest tests/ --cov=app --cov-report=html
```

**XML report (for CI/CD tools):**

```bash
uv run pytest tests/ --cov=app --cov-report=xml
```

**Combined report:**

```bash
uv run pytest tests/ --cov=app --cov-report=term --cov-report=html --cov-report=xml
```

### Measuring Coverage for Specific Module

```bash
# Coverage for specific module
uv run pytest tests/test_utils_auth.py --cov=app.utils.auth --cov-report=term-missing

# Coverage for specific package
uv run pytest tests/ --cov=app.utils --cov-report=term-missing
```

---

## Best Practices

### DO ✅

**Test Design:**
- Keep each test self-contained and independent
- Use descriptive, readable names for tests (test should read like a sentence)
- Test one thing per test (single responsibility)
- Use AAA pattern: Arrange, Act, Assert

**Fixtures & Setup:**
- Use fixtures to avoid redundancy
- Use a fresh DB per test
- Clean up resources in fixtures (use `yield` for teardown)

**Assertions:**
- Use `pytest.raises()` for exception checks
- Validate full API responses (structure and values)
- Assert on specific values, not just existence

**Coverage:**
- Maintain coverage ≥ 70%
- Focus on critical paths first
- Test both happy path and error scenarios

**Mocking:**
- Mock all external API calls
- Use proper patch paths (`app.utils.module.Class`)
- Verify mocks were called as expected

**Organization:**
- Group related tests in classes
- Use markers for categorization
- Keep test files parallel to source files

### DON'T ❌

**Dangerous Practices:**
- Never use the production database
- Never call external APIs directly (use mocks)
- Never commit sensitive data in test fixtures

**Bad Test Design:**
- Don't make tests depend on each other
- Don't rely on execution order
- Don't overstuff a single test with too many checks
- Avoid hardcoded dates/times (use freezegun if needed)

**Mocking Issues:**
- Don't use incorrect mock paths
- Don't skip testing error handling
- Don't make mocks too complex (refactor if needed)

**Maintenance:**
- Don't leave skipped tests without a reason
- Don't commit commented-out tests
- Don't ignore flaky tests

### Code Example: Good vs Bad

**❌ Bad Test:**

```python
def test_user_stuff(client):
    """Test user"""  # Vague name and docstring
    # Create user
    r = client.post("/api/auth/register", json={"email": "test@example.com", "username": "Test", "password": "Test123!@#"})
    # Login user
    r2 = client.post("/api/auth/login", json={"email": "test@example.com", "password": "Test123!@#"})
    # Get user
    r3 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {r2.json()['access_token']}"})
    assert r.status_code == 200 and r2.status_code == 200 and r3.status_code == 200
    # Too many things in one test, hard to read
```

**✅ Good Test:**

```python
def test_get_current_user_returns_user_info(client, auth_headers):
    """Getting current user returns correct user information"""
    # Act
    response = client.get("/api/auth/me", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "TestUser"
    assert "password" not in data
    # Clear name, single responsibility, readable assertions
```

---

## CI/CD Integration

### GitHub Actions Workflow

The workflow file `.github/workflows/backend-tests.yml` automatically runs all tests.

**Triggers:**

- Push to `main` or `dev` branch
- Pull request targeting `main` or `dev`
- File changes under `backend/**` or `shared/**`

**Execution steps:**

1. Set up Python 3.12 environment
2. Install `uv` package manager
3. Install dependencies from `requirements.txt` and `requirements-dev.txt`
4. Load environment variables (test mode)
5. Run pytest with coverage
6. Upload coverage results to Codecov

### Environment Variables for CI

```yaml
env:
  PATH_PROJECT_HOME: ${{ github.workspace }}
  CLAUDE_API_KEY: test_api_key
  JWT_SECRET_KEY: test_secret_key
  JWT_ALGORITHM: HS256
  JWT_EXPIRE_MINUTES: 1440
```

### Viewing CI Results

- **GitHub Actions tab:** See test run logs
- **PR checks:** Tests must pass before merging
- **Codecov:** View coverage trends and changes

---

## Writing Tests for New Features

Follow this workflow when adding new features:

### 1. Create a new test file

```bash
cd backend
touch tests/test_new_feature.py
```

### 2. Write test cases (TDD recommended)

Write tests BEFORE implementing the feature:

- **Success scenarios:** Happy path with valid inputs
- **Failure scenarios:** Invalid inputs, missing data
- **Edge cases:** Boundary conditions, empty values
- **Exception handling:** Expected errors and messages

```python
import pytest

@pytest.mark.unit
class TestNewFeature:
    """Tests for new feature"""

    def test_new_feature_success(self):
        """New feature works with valid input"""
        # Write test first
        result = new_feature("valid input")
        assert result == "expected output"

    def test_new_feature_invalid_input(self):
        """New feature raises error with invalid input"""
        with pytest.raises(ValueError):
            new_feature("invalid")
```

### 3. Implement the feature

Make the tests pass by implementing the feature.

### 4. Run the test

```bash
uv run pytest tests/test_new_feature.py -v
```

### 5. Check coverage

```bash
uv run pytest tests/test_new_feature.py --cov=app.module_name --cov-report=term-missing
```

**Target:** Aim for ≥85% coverage for new code.

### 6. Review and refactor

- Are all edge cases covered?
- Are error messages clear?
- Are tests readable and maintainable?
- Is the code following best practices?

---

## Troubleshooting

### Common Issues and Solutions

#### 1. `ModuleNotFoundError: No module named 'shared'`

**Error:**
```
ModuleNotFoundError: No module named 'shared'
```

**Cause:** `PATH_PROJECT_HOME` environment variable not set correctly.

**Solution:**
```bash
# Check conftest.py sys.path setup
# Ensure .env file exists in backend/
echo "PATH_PROJECT_HOME=$(pwd)/.." > .env
```

#### 2. `TypeError: Client.__init__() unexpected keyword`

**Error:**
```
TypeError: Client.__init__() got unexpected keyword argument 'follow_redirects'
```

**Cause:** Incompatible `httpx` version.

**Solution:**
```bash
uv pip install httpx==0.27.2
```

#### 3. `HTTPException` not raised properly

**Error:**
```
Expected HTTPException not raised
```

**Cause:** Incorrect exception testing syntax.

**Solution:**
```python
# Correct way to test HTTPException
from fastapi import HTTPException

with pytest.raises(HTTPException) as exc_info:
    decode_access_token("invalid.token")

assert exc_info.value.status_code == 401
assert "토큰이 유효하지 않습니다" in str(exc_info.value.detail)
```

#### 4. `database is locked` error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Database not properly closed or concurrent access.

**Solution:**
```python
# Ensure test_db fixture creates new DB per test
# Always close connections:
conn = get_db_connection()
try:
    # Use connection
    pass
finally:
    conn.close()
```

#### 5. Mock not working (actual API called)

**Error:**
```
anthropic.AuthenticationError: invalid x-api-key
```

**Cause:** Incorrect patch path or mock not set up before client creation.

**Solution:**
```python
# ❌ Wrong path
@patch('anthropic.Anthropic')

# ✅ Correct path (at point of use)
@patch('app.utils.claude_client.Anthropic')

# Ensure mock is set up BEFORE creating client
@patch('app.utils.claude_client.Anthropic')
def test_something(mock_anthropic):
    mock_anthropic.return_value = Mock()  # Set up first
    client = ClaudeClient()  # Then create client
```

#### 6. Test passes locally but fails in CI

**Common causes:**
- Environment variables not set in CI
- Different Python version
- File path assumptions (use `os.path.join`)
- Timezone differences (use UTC)

**Solution:**
```python
# Check CI environment setup
# Use relative paths
# Mock time-dependent functions
```

#### 7. Flaky tests (intermittent failures)

**Common causes:**
- Race conditions
- Network timeouts
- Random data generation
- Time-dependent logic

**Solution:**
```python
# Use deterministic test data
# Mock time functions
# Increase timeouts if needed
# Ensure proper cleanup
```

---

## Test Data

### Test User Accounts

**Normal User:**

```python
{
    "email": "test@example.com",
    "username": "TestUser",
    "password": "Test1234!@#"
}
```

**Admin User:**

```python
{
    "email": "admin@example.com",
    "username": "Admin",
    "password": "Admin1234!@#",
    "is_admin": True
}
```

### Test Report Content

**Sample Topic:**
```
"2025년 디지털 뱅킹 트렌드"
```

**Sample Generated Content:**
```python
{
    "title": "디지털 뱅킹 혁신 보고서",
    "title_background": "추진 배경",
    "background": "디지털 금융 환경의 급격한 변화...",
    "title_main_content": "주요 내용",
    "main_content": "AI 기반 개인화 서비스...",
    "title_conclusion": "결론 및 제언",
    "conclusion": "지속적인 디지털 혁신이 필요...",
    "title_summary": "요약",
    "summary": "본 보고서는..."
}
```

### Test File Paths

```python
# Template path
TEMPLATE_PATH = "backend/templates/report_template.hwpx"

# Output path
OUTPUT_PATH = "backend/output/report_20251028_153045.hwpx"

# Temp directory (auto-cleaned)
TEMP_DIR = "backend/temp/work_20251028_153045/"
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated:** October 28, 2025
**Version:** 1.0
