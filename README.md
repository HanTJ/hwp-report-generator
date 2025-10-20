# HWP 보고서 자동 생성 시스템

Claude AI를 활용하여 금융 업무보고서를 자동으로 생성하는 웹 시스템입니다.

## 주요 기능

- **AI 기반 보고서 생성**: 주제만 입력하면 Claude AI가 전문적인 금융 보고서 내용 자동 생성
- **HWP 형식 지원**: 한글 프로그램(HWPX) 형식으로 보고서 출력
- **웹 기반 인터페이스**: 간단하고 직관적인 웹 UI
- **보고서 관리**: 생성된 보고서 목록 조회 및 다운로드
- **사용자 인증**: 회원가입, 로그인, JWT 기반 인증 시스템
- **권한 관리**: 관리자 승인 기반 사용자 활성화, 본인 보고서만 접근 가능
- **토큰 사용량 추적**: 사용자별 Claude API 토큰 사용량 기록 및 통계
- **관리자 기능**: 사용자 관리, 비밀번호 초기화, 토큰 사용량 모니터링

## 기술 스택

- **Backend**: FastAPI (Python 3.12)
- **Package Manager**: uv (권장) 또는 pip
- **AI**: Claude API (Anthropic) - anthropic==0.71.0
- **HWP 처리**: zipfile, xml.etree.ElementTree, olefile
- **템플릿 엔진**: Jinja2 (웹 UI)
- **Frontend**: HTML, CSS, JavaScript
- **데이터베이스**: SQLite
- **인증**: JWT (python-jose), bcrypt (passlib)

## 설치 방법

### 1. 저장소 클론 (또는 프로젝트 디렉토리 생성)

```bash
cd hwp-report-generator
```

### 2. Python 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 3. 필요한 패키지 설치

**uv 사용 (권장):**
```bash
# uv로 패키지 설치
uv pip install -r requirements.txt
```

**pip 사용:**
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일을 생성하고 Claude API 키를 설정합니다:

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

`.env` 파일을 열고 필수 환경 변수를 설정:

```
# Claude API 설정
CLAUDE_API_KEY=your_actual_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# JWT 인증 설정
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 관리자 계정 정보
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure_admin_password
ADMIN_USERNAME=관리자
```

> **중요**:
> - Claude API 키는 [Anthropic Console](https://console.anthropic.com/)에서 발급받을 수 있습니다.
> - `JWT_SECRET_KEY`는 최소 32자 이상의 임의의 문자열로 설정하세요 (프로덕션 환경에서 필수)
> - `ADMIN_PASSWORD`는 안전한 비밀번호로 변경하세요

### 5. 데이터베이스 초기화

최초 실행 시 데이터베이스 초기화 스크립트를 실행합니다:

```bash
uv run python init_db.py
```

이 스크립트는:
- SQLite 데이터베이스 생성 (users, reports, token_usage 테이블)
- .env에 설정된 관리자 계정 생성
- 데이터는 `data/` 디렉토리에 저장됩니다

## 실행 방법

### 개발 서버 실행

**uv 사용 (권장):**
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**표준 Python 사용:**
```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 브라우저에서 다음 주소로 접속:

```
http://localhost:8000       # 메인 UI
http://localhost:8000/docs  # API 문서 (Swagger UI)
```

## 사용 방법

### 1. 회원가입 및 로그인

1. 웹 브라우저에서 `http://localhost:8000` 접속
2. 우측 상단 "회원가입" 클릭
3. 이메일, 사용자명, 비밀번호 입력하여 계정 생성
4. **관리자 승인 대기** (관리자가 사용자를 승인해야 로그인 가능)
5. 승인 후 로그인하여 서비스 이용

### 2. 관리자 기능

관리자 계정으로 로그인 후:

1. **사용자 관리**: `/admin` 페이지 접속
   - 대기 중인 사용자 승인/거부
   - 사용자 비활성화
   - 사용자 비밀번호 초기화 (임시 비밀번호 발급)
2. **토큰 사용량 모니터링**: 사용자별 Claude API 토큰 사용 통계 확인

### 3. 보고서 생성

1. 로그인 후 메인 페이지에서 "보고서 주제" 입력
   - 예: "2024년 디지털 뱅킹 서비스 현황 분석"
   - 예: "핀테크 산업 동향 및 은행권 대응 방안"
2. "보고서 생성" 버튼 클릭
3. 생성 완료 후 자동으로 다운로드 링크 표시

### 4. 생성된 보고서 확인

- 하단의 "생성된 보고서 목록"에서 **본인이 생성한 보고서만** 확인 가능
- 각 보고서의 다운로드 버튼을 클릭하여 다운로드

### 5. HWP 파일 열기

- 생성된 `.hwpx` 파일은 한글 프로그램 또는 호환 프로그램에서 열 수 있습니다
- LibreOffice 등 일부 오픈소스 프로그램에서도 열람 가능

## 프로젝트 구조

```
hwp-report-generator/
├── main.py                    # FastAPI 메인 애플리케이션
├── init_db.py                 # 데이터베이스 초기화 스크립트
├── migrate_db.py              # 데이터베이스 마이그레이션 스크립트
├── requirements.txt           # Python 패키지 의존성
├── .env                       # 환경 변수 (API 키, 관리자 정보)
├── .env.example              # 환경 변수 템플릿
├── .gitignore                # Git 제외 파일 목록
├── README.md                 # 프로젝트 문서
├── CLAUDE.md                 # Claude Code 가이드
├── models/                   # 데이터 모델
│   ├── user.py               # 사용자 모델
│   ├── report.py             # 보고서 모델
│   └── token_usage.py        # 토큰 사용량 모델
├── database/                 # 데이터베이스 레이어
│   ├── connection.py         # DB 연결 및 스키마
│   ├── user_db.py            # 사용자 CRUD
│   ├── report_db.py          # 보고서 CRUD
│   └── token_usage_db.py     # 토큰 사용량 CRUD
├── routers/                  # API 라우터
│   ├── auth.py               # 인증 API
│   ├── reports.py            # 보고서 API
│   └── admin.py              # 관리자 API
├── utils/
│   ├── auth.py               # JWT 인증 및 비밀번호 해싱
│   ├── claude_client.py      # Claude API 클라이언트
│   └── hwp_handler.py        # HWPX 파일 처리
├── templates/
│   ├── index.html            # 메인 페이지
│   ├── login.html            # 로그인 페이지
│   ├── register.html         # 회원가입 페이지
│   ├── admin.html            # 관리자 페이지
│   ├── change-password.html  # 비밀번호 변경 페이지
│   └── report_template.hwpx  # HWP 템플릿 (자동 생성)
├── static/
│   ├── style.css             # 스타일시트
│   ├── script.js             # 메인 페이지 로직
│   ├── auth.js               # 인증 관련 로직
│   └── admin.js              # 관리자 페이지 로직
├── data/                     # 데이터베이스 파일 (Git 제외)
│   └── hwp_reports.db
├── output/                   # 생성된 보고서 저장 (Git 제외)
└── temp/                     # 임시 파일 처리 (Git 제외)
```

## API 엔드포인트

### 인증 API (`/api/auth`)

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인 (JWT 토큰 발급)
- `GET /api/auth/me` - 현재 사용자 정보 조회
- `POST /api/auth/change-password` - 비밀번호 변경

### 보고서 API (`/api/reports`)

- `POST /api/reports/generate` - 보고서 생성 (인증 필요)
- `GET /api/reports/my-reports` - 본인 보고서 목록 조회 (인증 필요)
- `GET /api/reports/download/{report_id}` - 보고서 다운로드 (인증 필요)

### 관리자 API (`/api/admin`)

- `GET /api/admin/users` - 전체 사용자 목록 조회 (관리자 전용)
- `PATCH /api/admin/users/{user_id}/approve` - 사용자 승인 (관리자 전용)
- `PATCH /api/admin/users/{user_id}/reject` - 사용자 비활성화 (관리자 전용)
- `POST /api/admin/users/{user_id}/reset-password` - 비밀번호 초기화 (관리자 전용)
- `GET /api/admin/token-usage` - 전체 토큰 사용량 통계 (관리자 전용)
- `GET /api/admin/token-usage/{user_id}` - 특정 사용자 토큰 사용량 (관리자 전용)

### 기타

- `GET /` - 메인 페이지
- `GET /health` - 서버 상태 확인
- `GET /docs` - API 문서 (Swagger UI)

## HWP 템플릿 커스터마이징

기본 템플릿이 자동으로 생성되지만, 커스텀 템플릿을 사용하려면:

1. 한글 프로그램에서 보고서 양식 작성
2. 다음 플레이스홀더를 원하는 위치에 삽입:

   **주요 내용 플레이스홀더:**
   - `{{TITLE}}` - 제목
   - `{{DATE}}` - 작성일자
   - `{{BACKGROUND}}` - 배경 및 목적 내용
   - `{{MAIN_CONTENT}}` - 주요 내용
   - `{{CONCLUSION}}` - 결론 및 제언 내용
   - `{{SUMMARY}}` - 요약 내용

   **섹션 제목 플레이스홀더 (선택사항):**
   - `{{TITLE_BACKGROUND}}` - 배경 섹션 제목
   - `{{TITLE_MAIN_CONTENT}}` - 주요 내용 섹션 제목
   - `{{TITLE_CONCLUSION}}` - 결론 섹션 제목
   - `{{TITLE_SUMMARY}}` - 요약 섹션 제목

3. "다른 이름으로 저장" → "HWPX 파일" 선택
4. `templates/report_template.hwpx`로 저장

### 줄바꿈 처리

시스템은 자동으로 줄바꿈을 처리합니다:
- **단락 구분**: `\n\n` (이중 줄바꿈)은 별도의 단락으로 분리됩니다
- **줄바꿈**: `\n` (단일 줄바꿈)은 단락 내에서 줄바꿈으로 표시됩니다
- 한글 워드프로세서가 파일을 열 때 자동으로 레이아웃을 계산하여 올바르게 표시됩니다

## 데이터베이스 마이그레이션

시스템 업데이트로 데이터베이스 스키마가 변경된 경우 마이그레이션이 필요합니다.

### 기존 데이터베이스 마이그레이션

**password_reset_required 컬럼 추가** (기존 시스템에서 업그레이드하는 경우):

```bash
uv run python migrate_db.py
```

이 스크립트는:
- 기존 `users` 테이블에 `password_reset_required` 컬럼 추가
- 기존 데이터는 유지하면서 스키마만 업데이트

### 데이터베이스 초기화 (새로운 설치)

데이터베이스를 완전히 새로 만들려면:

```bash
# 기존 데이터베이스 삭제
rm -rf data/

# 데이터베이스 재초기화
uv run python init_db.py
```

> **경고**: 기존 데이터가 모두 삭제되므로 주의하세요!

## Render.com 배포 가이드

Render.com에서 본 애플리케이션을 무료로 배포할 수 있습니다.

### 1. 사전 준비

1. GitHub 저장소에 코드 푸시
2. [Render.com](https://render.com) 계정 생성

### 2. Web Service 생성

1. Render 대시보드에서 "New +" → "Web Service" 선택
2. GitHub 저장소 연결
3. 다음 설정 입력:

   - **Name**: `hwp-report-generator` (원하는 이름)
   - **Environment**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     python init_db.py && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

### 3. 환경 변수 설정

Render 대시보드의 "Environment" 탭에서 다음 환경 변수 추가:

```
CLAUDE_API_KEY=your_actual_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
JWT_SECRET_KEY=your-super-secret-random-string-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=secure_admin_password_here
ADMIN_USERNAME=관리자
```

> **중요**:
> - `JWT_SECRET_KEY`는 프로덕션에서 반드시 안전한 랜덤 문자열로 설정하세요
> - `ADMIN_PASSWORD`는 강력한 비밀번호로 설정하세요

### 4. 데이터베이스 영구 저장소 설정

Render의 무료 플랜에서는 디스크가 임시 저장소이므로, 재배포 시 데이터가 사라집니다. 영구 저장을 위해:

**옵션 1: Render Disk 사용 (유료)**
1. Render 대시보드에서 "Disks" 추가
2. Mount Path: `/opt/render/project/src/data`
3. Size: 1GB (최소)

**옵션 2: 외부 데이터베이스 사용 (권장)**
- PostgreSQL, MySQL 등 외부 관리형 데이터베이스 사용
- 코드 수정 필요: `database/connection.py`에서 SQLite 대신 PostgreSQL 연결

**옵션 3: 무료 테스트용**
- 임시 저장소 사용 (재배포 시 데이터 초기화됨)
- 관리자 계정은 `init_db.py`가 자동 재생성

### 5. 배포

1. "Create Web Service" 클릭
2. 자동으로 빌드 및 배포 시작
3. 배포 완료 후 제공되는 URL로 접속
   - 예: `https://hwp-report-generator.onrender.com`

### 6. 배포 후 확인사항

1. `/health` 엔드포인트 확인
   ```
   https://your-app.onrender.com/health
   ```
   응답: `{"status":"healthy"}`

2. 관리자 계정으로 로그인 테스트
   - 이메일: `.env`에 설정한 `ADMIN_EMAIL`
   - 비밀번호: `.env`에 설정한 `ADMIN_PASSWORD`

3. 일반 사용자 회원가입 → 관리자 승인 → 로그인 플로우 테스트

### 7. 주의사항

- **무료 플랜 제약사항**:
  - 15분 동안 요청이 없으면 서비스가 sleep 상태로 전환
  - 첫 요청 시 콜드 스타트로 인해 응답 시간이 느릴 수 있음
  - 월 750시간 무료 제공 (1개 서비스 상시 운영 가능)

- **데이터 백업**:
  - 임시 저장소 사용 시 정기적으로 데이터베이스 백업 필요
  - 보고서 파일(`output/`)도 임시 저장되므로 별도 백업 권장

## 문제 해결

### API 키 오류
```
ValueError: CLAUDE_API_KEY 환경 변수가 설정되지 않았습니다.
```
**해결**: `.env` 파일에 올바른 API 키가 설정되어 있는지 확인

### 데이터베이스 테이블 없음
```
no such table: users
```
**해결**: 데이터베이스 초기화 스크립트 실행
```bash
uv run python init_db.py
```

### 데이터베이스 컬럼 없음
```
no such column: password_reset_required
```
**해결**: 마이그레이션 스크립트 실행
```bash
uv run python migrate_db.py
```

### 템플릿 파일 오류
```
FileNotFoundError: 템플릿 파일을 찾을 수 없습니다
```
**해결**: 프로그램이 자동으로 기본 템플릿을 생성합니다. 문제가 지속되면 `templates/` 디렉토리가 존재하는지 확인

### 포트 충돌
```
OSError: [Errno 98] Address already in use
```
**해결**: 8000 포트가 이미 사용 중입니다. 다른 포트를 사용하려면:
```bash
uvicorn main:app --reload --port 8080
```

### 비밀번호 72바이트 초과 오류
```
ValueError: password cannot be longer than 72 bytes
```
**해결**: bcrypt 라이브러리 제약사항입니다. 비밀번호를 72바이트 이하로 입력하세요 (한글 약 24자, 영문 72자)

## 보안 주의사항

- **환경 변수**: `.env` 파일을 절대 Git에 커밋하지 마세요
- **API 키**: Claude API 키는 안전하게 보관하고 정기적으로 로테이션하세요
- **JWT 시크릿**: 프로덕션 환경에서는 반드시 강력한 랜덤 문자열 사용
- **비밀번호**: 관리자 비밀번호는 복잡하게 설정하고 정기적으로 변경하세요
- **HTTPS**: 프로덕션 배포 시 HTTPS 사용 (Render.com은 자동 제공)
- **데이터베이스**: 민감한 데이터 포함 시 암호화 저장 고려

## 관련 문서

- [README_AUTH.md](README_AUTH.md) - 인증 시스템 상세 가이드
- [PASSWORD_RESET_GUIDE.md](PASSWORD_RESET_GUIDE.md) - 비밀번호 초기화 기능 가이드
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드
- [CLAUDE.md](CLAUDE.md) - Claude Code 개발 가이드

## 향후 개선 계획

- [x] 사용자 인증 및 권한 관리
- [x] 토큰 사용량 추적
- [ ] 여러 보고서 템플릿 선택 기능
- [ ] 보고서 히스토리 및 버전 관리
- [ ] 보고서 스타일 커스터마이징
- [ ] PDF 변환 기능
- [ ] PostgreSQL 지원
- [ ] 단위 테스트 추가
- [ ] 이메일 알림 기능 (회원가입 승인, 비밀번호 초기화)

## 라이선스

MIT License

## 문의 및 기여

이슈나 개선 제안이 있으시면 언제든지 연락주세요.
