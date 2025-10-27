# 프로젝트 명령어 가이드

## 개발 환경 설정
```bash
# 의존성 설치
uv pip install -r requirements.txt

# 데이터베이스 초기화
uv run python init_db.py

# 데이터베이스 재설정 (모든 데이터 삭제)
rm -f data/hwp_reports.db
uv run python init_db.py
```

## 서버 실행
```bash
# 개발 서버 (자동 재시작 활성화)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 접속 정보
- 메인 페이지: http://localhost:8000
- 로그인 페이지: http://localhost:8000/login
- 회원가입 페이지: http://localhost:8000/register
- 관리자 페이지: http://localhost:8000/admin
- API 문서: http://localhost:8000/docs

## 기본 관리자 계정
- 이메일: hantj@kjbank.com
- 비밀번호: kjbank123!@#

## Windows 시스템 명령어
```bash
# 디렉토리 조회
dir

# 파일 내용 보기
type filename.txt

# 파일 삭제
del filename.txt

# 디렉토리 삭제
rmdir /s /q dirname
```

## 프로젝트 특이사항
- Windows 환경에서 개발 중
- UV 패키지 매니저 사용
- SQLite 데이터베이스 (data/hwp_reports.db)
- HWPX 파일 생성 및 처리