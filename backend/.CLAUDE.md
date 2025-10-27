# Backend Development Guidelines

이 파일은 HWP Report Generator 백엔드 개발 시 Claude Code가 참조해야 할 가이드라인을 제공합니다.

## 코드 스타일 및 문서화

### DocString 규칙

**모든 Python 함수와 클래스에는 반드시 Google Style DocString을 작성해야 합니다.**

#### Google Style DocString 형식

**함수 DocString 예시:**

```python
def generate_report(topic: str, user_id: int, options: dict = None) -> dict:
    """보고서를 생성하고 메타데이터를 반환합니다.

    주어진 주제에 대해 Claude API를 호출하여 보고서 내용을 생성하고,
    HWPX 파일로 변환한 후 데이터베이스에 저장합니다.

    Args:
        topic: 보고서 생성 주제 (예: "2025년 디지털 뱅킹 트렌드")
        user_id: 보고서를 생성하는 사용자의 ID
        options: 보고서 생성 옵션 (선택사항)
            - template_id: 사용할 템플릿 ID
            - format: 출력 형식 (기본값: "hwpx")

    Returns:
        생성된 보고서 정보를 담은 딕셔너리:
            - id: 보고서 ID
            - filename: 생성된 파일명
            - file_path: 파일 저장 경로
            - created_at: 생성 시각

    Raises:
        ValueError: topic이 빈 문자열인 경우
        FileNotFoundError: 템플릿 파일을 찾을 수 없는 경우
        APIError: Claude API 호출 실패 시

    Examples:
        >>> report = generate_report("AI 트렌드", user_id=1)
        >>> print(report['filename'])
        'report_20251027_103954.hwpx'

    Note:
        이 함수는 Claude API를 호출하므로 처리 시간이 5-15초 정도 소요됩니다.
    """
    # 함수 구현
    pass
```

**클래스 DocString 예시:**

```python
class ClaudeClient:
    """Claude API를 사용하여 보고서 내용을 생성하는 클라이언트 클래스.

    이 클래스는 Anthropic의 Claude API와 통신하여 구조화된 보고서 내용을
    생성하고, 토큰 사용량을 추적합니다.

    Attributes:
        api_key: Claude API 인증 키
        model: 사용할 Claude 모델명 (기본값: claude-sonnet-4-5-20250929)
        client: Anthropic API 클라이언트 인스턴스
        last_input_tokens: 마지막 API 호출의 입력 토큰 수
        last_output_tokens: 마지막 API 호출의 출력 토큰 수
        last_total_tokens: 마지막 API 호출의 총 토큰 수

    Examples:
        >>> client = ClaudeClient()
        >>> content = client.generate_report("디지털 금융 트렌드")
        >>> print(content['title'])
        '디지털 금융 혁신 보고서'
        >>> print(client.last_total_tokens)
        4500
    """

    def __init__(self):
        """Claude 클라이언트를 초기화합니다.

        환경 변수에서 API 키와 모델명을 로드하고 Anthropic 클라이언트를
        초기화합니다. 토큰 사용량 추적 변수도 초기화합니다.

        Raises:
            ValueError: CLAUDE_API_KEY 환경 변수가 설정되지 않은 경우
        """
        # 구현
        pass
```

**간단한 함수의 경우 (한 줄 DocString):**

```python
def get_user_by_id(user_id: int) -> User:
    """주어진 ID로 사용자를 조회합니다."""
    # 구현
    pass
```

#### DocString 섹션 설명

| 섹션 | 필수 여부 | 설명 |
|------|----------|------|
| **Summary** | 필수 | 함수/클래스의 간단한 설명 (첫 줄) |
| **Description** | 선택 | 상세 설명 (Summary 다음 빈 줄 후) |
| **Args** | 함수 파라미터가 있으면 필수 | 각 파라미터 설명 |
| **Returns** | 반환값이 있으면 필수 | 반환값 설명 |
| **Raises** | 예외 발생 시 권장 | 발생 가능한 예외들 |
| **Yields** | 제너레이터인 경우 필수 | yield하는 값 설명 |
| **Examples** | 선택 (복잡한 함수는 권장) | 사용 예시 (doctest 형식) |
| **Note** | 선택 | 추가 주의사항이나 참고사항 |
| **Warning** | 선택 | 경고사항 |
| **See Also** | 선택 | 관련 함수/클래스 참조 |

#### DocString 작성 규칙

1. **Summary (첫 줄)**:
   - 함수/클래스를 한 문장으로 요약
   - 마침표로 끝남
   - 명령형 동사로 시작 (예: "생성합니다", "반환합니다", "계산합니다")

2. **Args**:
   - 형식: `파라미터명: 설명`
   - 타입은 type hint에 이미 명시되어 있으므로 생략 가능
   - 선택적 파라미터는 "(선택사항)" 또는 기본값 명시
   - 딕셔너리나 복잡한 구조는 들여쓰기로 상세 설명

3. **Returns**:
   - 반환값의 의미와 구조 설명
   - 딕셔너리/객체의 경우 주요 필드 나열
   - None 반환 시에도 명시 ("None을 반환합니다")

4. **Raises**:
   - 발생 가능한 예외와 발생 조건 명시
   - 형식: `예외클래스: 발생 조건`

5. **Examples**:
   - doctest 형식 사용 (`>>>` 프롬프트)
   - 실제 실행 가능한 예제 제공
   - 입력과 출력을 모두 보여줌

#### 잘못된 예시 (지양)

```python
# ❌ 나쁜 예시 1: DocString 없음
def create_report(topic, user_id):
    return report

# ❌ 나쁜 예시 2: 영어로 작성
def create_report(topic: str) -> dict:
    """Creates a report from given topic."""
    pass

# ❌ 나쁜 예시 3: 불완전한 정보
def create_report(topic: str, user_id: int) -> dict:
    """보고서 생성"""
    # Args, Returns 정보 누락
    pass

# ❌ 나쁜 예시 4: 잘못된 형식
def create_report(topic: str) -> dict:
    """
    이 함수는 보고서를 생성합니다
    @param topic: 주제
    @return: 보고서
    """
    # Google Style이 아닌 다른 스타일 사용
    pass
```

#### 올바른 예시 (권장)

```python
# ✅ 좋은 예시 1: 완전한 DocString
def create_report(topic: str, user_id: int, template_id: int = None) -> dict:
    """주어진 주제로 보고서를 생성합니다.

    Claude API를 사용하여 보고서 내용을 생성하고 HWPX 파일로 저장합니다.

    Args:
        topic: 보고서 주제
        user_id: 사용자 ID
        template_id: 템플릿 ID (선택, 기본값: None은 기본 템플릿 사용)

    Returns:
        생성된 보고서 정보:
            - id: 보고서 ID
            - filename: 파일명
            - file_path: 파일 경로

    Raises:
        ValueError: topic이 빈 문자열인 경우
        APIError: Claude API 호출 실패 시
    """
    pass

# ✅ 좋은 예시 2: 간단한 함수
def validate_email(email: str) -> bool:
    """이메일 주소의 형식이 올바른지 검증합니다."""
    pass

# ✅ 좋은 예시 3: 제너레이터 함수
def get_reports_batch(user_id: int, batch_size: int = 100):
    """사용자의 보고서를 배치 단위로 조회합니다.

    Args:
        user_id: 사용자 ID
        batch_size: 한 번에 조회할 보고서 수 (기본값: 100)

    Yields:
        보고서 객체 리스트 (최대 batch_size개)

    Examples:
        >>> for batch in get_reports_batch(user_id=1, batch_size=50):
        ...     process_batch(batch)
    """
    pass
```

### Private 함수/메서드

Private 함수/메서드 (언더스코어로 시작)도 DocString을 작성해야 하지만,
Public 함수보다 간략하게 작성할 수 있습니다.

```python
def _parse_xml_content(self, xml_path: str) -> dict:
    """XML 파일을 파싱하여 딕셔너리로 변환합니다.

    Args:
        xml_path: XML 파일 경로

    Returns:
        파싱된 XML 내용 딕셔너리
    """
    pass
```

### 타입 힌트와 DocString의 조화

타입 힌트를 사용하므로 DocString의 Args 섹션에서는 타입을 생략하고
의미와 제약사항을 설명하는 데 집중합니다.

```python
# ✅ 권장: 타입은 type hint에, 의미는 DocString에
def calculate_tokens(input_text: str, model: str = "gpt-4") -> int:
    """입력 텍스트의 토큰 수를 계산합니다.

    Args:
        input_text: 토큰을 계산할 텍스트
        model: 사용할 모델명 (기본값: "gpt-4")

    Returns:
        계산된 토큰 수
    """
    pass

# ❌ 지양: DocString에 타입 중복 명시
def calculate_tokens(input_text: str, model: str = "gpt-4") -> int:
    """입력 텍스트의 토큰 수를 계산합니다.

    Args:
        input_text (str): 토큰을 계산할 텍스트  # 타입 중복
        model (str): 사용할 모델명  # 타입 중복

    Returns:
        int: 계산된 토큰 수  # 타입 중복
    """
    pass
```

## 적용 범위

이 DocString 규칙은 다음 파일들에 적용됩니다:

- `app/routers/*.py` - 모든 API 라우터 함수
- `app/models/*.py` - Pydantic 모델 클래스
- `app/database/*.py` - 데이터베이스 CRUD 함수
- `app/utils/*.py` - 유틸리티 함수 및 헬퍼 클래스
- `*.py` - backend 디렉토리의 모든 Python 파일

## 예외 사항

다음 경우는 DocString을 생략할 수 있습니다:

1. `__init__.py` 파일의 import 문만 있는 경우
2. 매우 단순한 getter/setter 메서드 (한 줄로 명확한 경우)
3. 테스트 함수 (하지만 복잡한 테스트는 DocString 권장)

```python
# 예외: 매우 단순한 getter
@property
def user_id(self) -> int:
    return self._user_id

# 권장: 복잡한 로직이 있는 경우는 DocString 작성
@property
def is_expired(self) -> bool:
    """토큰이 만료되었는지 확인합니다.

    현재 시각과 만료 시각을 비교하여 판단합니다.

    Returns:
        토큰이 만료되었으면 True, 아니면 False
    """
    return datetime.now() > self.expires_at
```

## DocString 검증

코드 리뷰 시 다음 사항을 확인합니다:

- [ ] 모든 public 함수/클래스에 DocString이 있는가?
- [ ] Summary (첫 줄)가 명확한가?
- [ ] Args, Returns 섹션이 완전한가?
- [ ] 예외 처리가 있다면 Raises 섹션이 있는가?
- [ ] 복잡한 함수는 Examples가 있는가?
- [ ] 한글로 작성되었는가?

## 참고 자료

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Napoleon - Sphinx extension for Google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)

---

## 테스트 가이드라인

### 테스트 환경

**테스트 프레임워크:**
- pytest (메인 테스트 프레임워크)
- pytest-cov (코드 커버리지 측정)
- pytest-asyncio (비동기 테스트 지원)
- pytest-mock (모킹 기능)
- httpx==0.27.2 (FastAPI TestClient용 HTTP 클라이언트)

**의존성 설치:**
```bash
cd backend
uv pip install -r requirements-dev.txt
```

### 테스트 구조

```
backend/
├── tests/
│   ├── conftest.py              # 공통 fixtures
│   ├── test_utils_auth.py       # 인증 유틸리티 테스트
│   ├── test_routers_auth.py     # 인증 API 테스트
│   └── (추가 테스트 파일들...)
├── pytest.ini                   # pytest 설정
└── requirements-dev.txt         # 개발/테스트 의존성
```

### 테스트 실행

**전체 테스트:**
```bash
cd backend
uv run pytest tests/ -v
```

**특정 파일:**
```bash
uv run pytest tests/test_utils_auth.py -v
```

**특정 테스트:**
```bash
uv run pytest tests/test_utils_auth.py::TestPasswordHashing::test_hash_password -v
```

**커버리지 포함:**
```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

**디버그 출력:**
```bash
uv run pytest tests/ -v -s
```

### 테스트 마커

```bash
# 유닛 테스트만
uv run pytest -m unit -v

# API 테스트만
uv run pytest -m api -v

# 인증 관련 테스트만
uv run pytest -m auth -v
```

### 주요 Fixtures (conftest.py)

**test_db:**
- 각 테스트마다 새로운 임시 SQLite DB 생성
- 자동 정리

**client:**
- FastAPI TestClient 제공
- test_db에 의존

**test_user_data / test_admin_data:**
- 테스트용 사용자 데이터 딕셔너리

**create_test_user / create_test_admin:**
- 테스트용 사용자/관리자 생성
- User 객체 반환

**auth_headers / admin_auth_headers:**
- JWT 인증 헤더 생성
- {"Authorization": "Bearer <token>"} 형식

**temp_dir:**
- 임시 디렉토리 생성 및 자동 정리

### 테스트 작성 패턴

**1. 유닛 테스트:**
```python
import pytest

@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """비밀번호 해싱 테스트"""

    def test_hash_password(self):
        """비밀번호 해싱 테스트"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
```

**2. API 테스트:**
```python
@pytest.mark.api
class TestAuthRouter:
    """인증 API 테스트"""

    def test_register_success(self, client):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "신규사용자",
                "password": "NewUser123!@#"
            }
        )

        assert response.status_code == 200
```

**3. 예외 테스트:**
```python
def test_invalid_token(self):
    """잘못된 토큰 테스트"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("invalid.token")

    assert exc_info.value.status_code == 401
```

**4. 인증 필요 테스트:**
```python
def test_authenticated_endpoint(self, client, auth_headers):
    """인증 필요 엔드포인트 테스트"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

### 코드 커버리지 목표

- 전체: 최소 70% 이상
- 핵심 비즈니스 로직: 90% 이상
- 유틸리티 함수: 85% 이상

**커버리지 리포트:**
```bash
# 터미널 출력
uv run pytest tests/ --cov=app --cov-report=term-missing

# HTML 리포트
uv run pytest tests/ --cov=app --cov-report=html

# XML 리포트 (CI/CD용)
uv run pytest tests/ --cov=app --cov-report=xml
```

### CI/CD 통합

`.github/workflows/backend-tests.yml`이 자동으로 테스트 실행:

**트리거:**
- `main` 또는 `dev` 브랜치 push
- PR 생성 (main/dev 대상)
- `backend/**` 또는 `shared/**` 파일 변경

**실행 내용:**
1. Python 3.12 환경 설정
2. uv 설치
3. 의존성 설치
4. 환경 변수 설정
5. pytest 실행 (커버리지 포함)
6. Codecov 업로드

### 새 기능 개발 시 테스트 작성

1. **테스트 파일 생성**
   ```bash
   touch tests/test_new_feature.py
   ```

2. **테스트 케이스 작성** (TDD 권장)
   - 성공 시나리오
   - 실패 시나리오
   - 경계 조건
   - 예외 처리

3. **기능 구현**

4. **테스트 실행**
   ```bash
   uv run pytest tests/test_new_feature.py -v
   ```

5. **커버리지 확인**
   ```bash
   uv run pytest tests/test_new_feature.py --cov=app.module_name --cov-report=term-missing
   ```

### 모범 사례

**DO ✅:**
- 각 테스트는 독립적으로 실행 가능
- 테스트 이름은 명확하고 서술적으로
- Fixtures 활용하여 중복 제거
- 테스트마다 새 DB 사용
- 예외 발생 시 pytest.raises() 사용
- API 응답 형식 철저히 검증
- 커버리지 70% 이상 유지

**DON'T ❌:**
- 실제 프로덕션 DB 사용 금지
- 외부 API 직접 호출 금지 (모킹 필수)
- 테스트 간 의존성 생성 금지
- 테스트 순서 의존 금지
- 하드코딩된 시간/날짜 피하기
- 한 테스트에서 너무 많이 검증하지 않기

### 문제 해결

**1. ModuleNotFoundError: No module named 'shared'**
- conftest.py에서 PATH_PROJECT_HOME 확인
- .env 파일에 PATH_PROJECT_HOME 정의 확인

**2. TypeError: Client.__init__() unexpected keyword**
```bash
uv pip install httpx==0.27.2
```

**3. HTTPException not raised**
```python
# 올바른 방법
with pytest.raises(HTTPException) as exc_info:
    decode_access_token(invalid_token)
assert exc_info.value.status_code == 401
```

**4. database is locked**
- test_db fixture가 각 테스트마다 새 DB 생성하는지 확인
- 연결 후 반드시 close() 호출

### 테스트 데이터

**일반 사용자:**
- Email: test@example.com
- Username: 테스트사용자
- Password: Test1234!@#

**관리자:**
- Email: admin@example.com
- Username: 관리자
- Password: Admin1234!@#

---

**작성일**: 2025-10-27
**버전**: 1.1
**적용 시작**: 즉시
