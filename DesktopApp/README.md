# HWPX Desktop Converter

Windows 환경에서 Markdown 문서를 고품질 HWPX 파일로 변환하기 위한 데스크톱 애플리케이션입니다.

## 구조

- `src/` 애플리케이션 소스 코드
- `requirements.txt` 필수 의존성 목록
- `build.spec`, `build.ps1` PyInstaller 배포 스크립트(Phase 4에서 사용 예정)
- `doc/` 개발 참고 문서 (개발 규칙 등)
- `scripts/` 개발 환경 구축 및 점검 스크립트

## 선행 준비

- **운영체제:** Windows 11 (64bit)
- **한컴오피스 2024:** 기본 설치 경로 `C:\Program Files\Hnc\Hwp2024\Hwp.exe`. 다른 경로에 설치했다면 설정 창에서 직접 지정해야 합니다.
- **Microsoft Visual C++ 재배포 패키지:** pywin32, pyhwpx, qt-material에서 사용하는 COM/Win32 API를 위해 최신 버전을 설치합니다.
- **Python 3.10 이상 권장:** `python --version`으로 버전을 확인합니다. 사내 표준 파이썬 버전이 다르다면 `setup_env.ps1` 실행 시 `-Python` 인자로 명시하세요.
- **네트워크:** 방화벽/프록시 정책상 FastAPI 백엔드에 접근 가능한지 확인합니다.

## 개발 준비 절차

> `setup_env.ps1`은 가상환경 생성 → 필수 패키지 설치 → 환경 검증(`verify_environment.py`)을 순차적으로 실행합니다. 오류 메시지가 출력되면 해당 원인을 해결한 뒤 다시 실행하세요.

### 1. 가상환경 생성

자동 스크립트를 사용할 수 없을 때만 아래 과정을 따릅니다.

```powershell
# uv로 가상환경 생성 (.venv)
uv venv

# 가상환경 활성화 (Linux/Mac)
source .venv/bin/activate

# 가상환경 활성화 (Windows)
.venv\Scripts\activate
```

### 2. 수동 의존성 설치 (옵션)

```powershell
uv pip install -r DesktopApp/requirements.txt
```

### 3. 환경 검증

```powershell
python DesktopApp\scripts\verify_environment.py
```

`[O]` 로 시작하는 항목이 모두 출력되면 환경 구성이 완료된 것입니다. 한컴오피스 실행 파일을 찾지 못하면 `DesktopApp/src/config.py`의 기본 경로를 수정하거나 애플리케이션 설정 창에서 직접 경로를 입력하세요.

### 4. 애플리케이션 실행

```powershell
uv run python -m DesktopApp.src.main
```

`uv run`을 사용하면 가상환경과 의존성을 자동으로 활성화한 뒤 애플리케이션을 실행합니다. PyInstaller 패키징은 Phase 4에서 전용 빌드 스크립트를 통해 진행할 예정입니다.

## 변환 흐름

1. Topic을 선택하고 변환할 Markdown Artifact를 체크합니다.
2. 창 하단의 **출력 폴더**가 올바르게 설정되어 있는지 확인합니다.
3. `선택 항목 변환 (HWPX)` 버튼을 클릭하면 변환이 시작되며, 진행 다이얼로그에서 각 항목의 다운로드·변환 상태를 확인하거나 취소할 수 있습니다.
4. 변환이 완료되면 성공/실패 요약과 함께 HWPX 파일이 지정한 출력 폴더에 생성됩니다.

> pyhwpx 모듈과 한컴오피스 2024가 설치되어 있어야 변환 버튼이 활성화됩니다. 모듈이 누락된 경우 오류 메시지로 안내됩니다.

## 일괄 변환 스크립트

여러 Markdown 파일을 한 번에 변환하거나 파싱 오류를 점검하려면 `scripts/convert_batch.py`를 사용할 수 있습니다.

```powershell
# 변환 (하위 폴더를 포함해 검색)
python DesktopApp\scripts\convert_batch.py docs\markdown --recursive --output build\hwpx

# pyhwpx 없이 파싱만 검증 (Dry Run)
python DesktopApp\scripts\convert_batch.py docs\markdown --dry-run
```

실패 항목은 표준 출력에 이유가 함께 표시되며, 종료 코드는 성공/실패 여부에 따라 0, 1, 2(pyhwpx 누락)로 반환됩니다.

## Material 테마

- Qt Material 테마가 기본 적용됩니다. 기본 테마는 `dark_teal`이며, 설정 창에서 즉시 변경할 수 있습니다.
- 테마 변경 시 `.xml` 확장자는 입력하지 않아도 되며, 변경 즉시 미리보기로 적용됩니다.
- 모든 테마 목록은 `Settings → Material 테마` 콤보박스에서 qt-material에서 제공하는 순서로 확인할 수 있습니다.

## 로그 및 세션

- 로그 파일 위치: `%APPDATA%\HWPConverter\logs\application.log`
- 설정 창의 **로그 기록 구분**에서 `운영`(오류 중심) 또는 `디버그`(상세 로그)를 선택할 수 있습니다.
- 세션 정보는 `%APPDATA%\HWPConverter\session.json`에 저장되며, 자동 로그인을 지원하기 위해 refresh token을 보관합니다. 토큰 만료 시 자동으로 재로그인을 시도합니다.
