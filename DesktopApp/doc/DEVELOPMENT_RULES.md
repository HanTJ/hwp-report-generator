# DesktopApp 개발 규칙

## 공통 규칙

- 모든 로그는 `DesktopApp/src/logging/logger.py`의 `app_logger`를 통해 기록한다. (`print` 사용 금지)
- 로그 모드를 변경할 때는 `app_logger.configure()`를 사용하며, 설정 화면에서 선택한 모드가 즉시 반영되도록 한다.
- 세션 정보는 반드시 `SessionManager`로만 다룬다. (수동 파일 접근/수정 금지)
- JWT 토큰은 `TokenManager`를 통해 저장·검증·삭제한다. DPAPI 예외 처리 로직을 임의로 변경하지 않는다.

## 제약 사항

- 프로젝프홈/backend 디렉토리 수정 금지
- 프로젝프홈/frontend 디렉토리 수정 금지

## 환경설정

- Hancom Office 2024 위치 : "C:\Program Files (x86)\Hnc\Office 2024\HOffice130\Bin\Hwp.exe"

## UI/UX 규칙

- PyQt5 위젯 스타일은 **qt-material**을 사용한다. 직접 팔레트를 수정하기보다는 `apply_material_theme()` 헬퍼를 통해 테마를 적용한다.
- 새로운 다이얼로그/윈도우를 추가할 때는 테마 즉시 적용을 위해 `DesktopApp/src/ui/theme.py`를 활용한다.
- 설정 창에서 테마를 변경하면 즉시 미리보기로 적용되어야 하며, 저장 시 `AppSettings.material_theme`에 반영한다.
- 기본 테마는 `dark_teal`이며, qt-material에서 제공하는 테마 이름을 그대로 사용한다. `.xml` 확장자는 저장하지 않는다.
- 새로운 UI를 추가할 때는 키보드 내비게이션(탭 이동)과 화면 리사이즈/고해상도 대응을 고려해 레이아웃을 구성한다.

## API/네트워크

- HTTP 호출은 `DesktopApp/src/api/client.py`에 정의된 `APIClient`를 통해 수행한다.
- 예외 처리 시 사용자 친화적인 메시지와 함께 `app_logger`로 상세 로그를 남긴다.
- 비동기 처리(추후 도입 예정)를 준비하기 위해 네트워크 호출 타임아웃을 명시적으로 설정한다.

## 설정/스토리지

- 설정 데이터는 `AppSettings`를 통해 읽고 쓴다. 신규 필드를 추가할 때는 기본값과 마이그레이션 로직을 `SettingsStore`에 구현한다.
- `%APPDATA%\HWPConverter` 경로 외에 새 디렉터리를 사용할 경우 개발/배포 문서에 반드시 기록한다.

## 테스트/검증

- UI 변경 후에는 `DesktopApp/scripts/verify_environment.py`를 업데이트하여 필요한 모듈 검증을 유지한다.
- 자동화 테스트를 도입하기 전까지는 주요 화면에 대한 스크린샷/동영상 캡처를 QA 문서에 첨부한다.
