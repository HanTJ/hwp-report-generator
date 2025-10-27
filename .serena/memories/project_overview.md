# HWP 보고서 자동 생성 시스템 프로젝트 개요

## 프로젝트 목적
Claude AI를 사용하여 금융 업무보고서를 자동으로 생성하는 웹 애플리케이션

## 핵심 기능
- 사용자 인증 및 관리 (JWT 기반)
- Claude AI를 통한 보고서 내용 자동 생성
- HWPX 형식의 보고서 파일 생성
- 관리자 페이지를 통한 사용자 승인 관리

## 기술 스택
- **백엔드**: FastAPI (Python 웹 프레임워크)
- **서버**: Uvicorn (ASGI 서버)
- **AI**: Anthropic Claude API
- **데이터베이스**: SQLite
- **인증**: JWT (python-jose), bcrypt, passlib
- **문서 생성**: HWPX 파일 처리 (olefile, zipfile)
- **기타**: Pydantic (데이터 검증), Jinja2 (템플릿)

## 프로젝트 구조
```
hwp-report-generator/
├── database/          # 데이터베이스 연결 및 CRUD
│   ├── connection.py  # SQLite 연결
│   ├── user_db.py     # 사용자 데이터베이스
│   ├── report_db.py   # 보고서 데이터베이스
│   └── token_usage_db.py  # 토큰 사용량 추적
├── models/            # Pydantic 데이터 모델
│   ├── user.py        # 사용자 모델
│   ├── report.py      # 보고서 모델
│   └── token_usage.py # 토큰 사용량 모델
├── routers/           # API 라우터
│   ├── auth.py        # 인증 관련 API
│   ├── reports.py     # 보고서 관련 API
│   └── admin.py       # 관리자 API
├── utils/             # 유틸리티 함수
│   ├── claude_client.py  # Claude API 클라이언트
│   ├── hwp_handler.py    # HWPX 파일 처리
│   └── auth.py           # 인증 헬퍼
├── templates/         # HTML 템플릿
├── static/            # 정적 파일 (CSS, JS)
├── output/            # 생성된 보고서 저장
├── temp/              # 임시 파일
├── data/              # 데이터베이스 파일
└── main.py            # FastAPI 메인 애플리케이션
```

## 주요 엔드포인트
- `GET /`: 메인 페이지
- `GET /login`: 로그인 페이지
- `GET /register`: 회원가입 페이지
- `GET /admin`: 관리자 페이지
- `POST /api/auth/register`: 회원가입
- `POST /api/auth/login`: 로그인
- `POST /api/generate`: 보고서 생성
- `GET /api/download/{filename}`: 보고서 다운로드
- `GET /api/admin/users`: 사용자 목록 조회