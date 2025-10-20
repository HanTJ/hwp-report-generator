# HWP 보고서 자동 생성 시스템 - 인증 시스템 가이드

## 새로 추가된 기능

### 1. 회원가입 및 로그인
- 사용자는 이메일, 사용자명, 비밀번호로 회원가입 가능
- 회원가입 후 관리자 승인 필요 (is_active=False 상태)
- JWT 기반 인증 시스템
- 비밀번호는 bcrypt로 암호화 저장

### 2. 보고서 생성 권한
- 로그인한 사용자만 보고서 생성 가능
- 본인이 생성한 보고서만 조회 및 다운로드 가능
- 토큰 사용량 자동 기록

### 3. 관리자 기능
- 회원 승인/거부
- 사용자 비밀번호 초기화
- 회원별 토큰 사용량 통계 조회

## 환경 설정

### .env 파일 설정
```env
# Claude API
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# JWT 설정
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 관리자 정보
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123!@#
ADMIN_USERNAME=관리자
```

**중요**: 프로덕션 환경에서는 반드시 `JWT_SECRET_KEY`를 강력한 랜덤 문자열로 변경하세요.

## 설치 및 실행

### 1. 의존성 설치
```bash
# uv 사용 (권장)
uv pip install -r requirements.txt

# 또는 pip 사용
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화 (최초 1회)
```bash
# 데이터베이스 초기화 스크립트 실행
uv run python init_db.py
```

출력 예시:
```
데이터베이스를 초기화합니다...
✅ 데이터베이스 테이블이 생성되었습니다.
✅ 관리자 계정이 생성되었습니다:
   이메일: hantj@kjbank.com
   비밀번호: kjbank123!@#
데이터베이스 초기화가 완료되었습니다!
```

### 3. 서버 실행
```bash
# uv 사용
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 직접 실행
python main.py
```

서버가 시작되면:
- 서버 시작 시 데이터베이스가 자동으로 초기화됩니다 (이미 초기화되어 있으면 스킵)
- `http://localhost:8000` 에서 접속 가능

### 4. 기본 관리자 계정
- 이메일: `.env` 파일의 `ADMIN_EMAIL` (기본값: `hantj@kjbank.com`)
- 비밀번호: `.env` 파일의 `ADMIN_PASSWORD` (기본값: `kjbank123!@#`)

**프로덕션 환경에서는 반드시 .env 파일의 관리자 정보를 변경하세요!**

## API 엔드포인트

### 인증 API (`/api/auth`)
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `GET /api/auth/me` - 현재 사용자 정보

### 보고서 API (`/api/reports`)
- `POST /api/reports/generate` - 보고서 생성 (인증 필요)
- `GET /api/reports/my-reports` - 내 보고서 목록 (인증 필요)
- `GET /api/reports/download/{report_id}` - 보고서 다운로드 (인증 필요)

### 관리자 API (`/api/admin`) - 관리자 전용
- `GET /api/admin/users` - 사용자 목록 조회
- `PATCH /api/admin/users/{user_id}/approve` - 사용자 승인
- `PATCH /api/admin/users/{user_id}/reject` - 사용자 비활성화
- `POST /api/admin/users/{user_id}/reset-password` - 비밀번호 초기화
- `GET /api/admin/token-usage` - 토큰 사용량 통계
- `GET /api/admin/token-usage/{user_id}` - 특정 사용자 토큰 사용량

## 웹 페이지

- `/` - 메인 페이지 (보고서 생성, 로그인 필요)
- `/login` - 로그인 페이지
- `/register` - 회원가입 페이지
- `/admin` - 관리자 페이지 (관리자 전용)
- `/docs` - API 문서 (Swagger UI)

## 데이터베이스 구조

### users 테이블
- id: 사용자 ID (PK)
- email: 이메일 (UNIQUE)
- username: 사용자명
- hashed_password: 암호화된 비밀번호
- is_active: 활성화 상태 (관리자 승인)
- is_admin: 관리자 권한
- created_at: 생성일시
- updated_at: 수정일시

### reports 테이블
- id: 보고서 ID (PK)
- user_id: 사용자 ID (FK)
- topic: 보고서 주제
- title: 보고서 제목
- filename: 파일명
- file_path: 파일 경로
- file_size: 파일 크기
- created_at: 생성일시

### token_usage 테이블
- id: 사용량 ID (PK)
- user_id: 사용자 ID (FK)
- report_id: 보고서 ID (FK, nullable)
- input_tokens: 입력 토큰 수
- output_tokens: 출력 토큰 수
- total_tokens: 총 토큰 수
- created_at: 생성일시

## 사용 흐름

### 일반 사용자
1. `/register`에서 회원가입
2. 관리자 승인 대기
3. 승인 후 `/login`에서 로그인
4. `/`에서 보고서 생성 및 다운로드

### 관리자
1. 기본 관리자 계정으로 로그인
2. `/admin`에서 회원 승인/관리
3. 토큰 사용량 통계 확인
4. 필요시 사용자 비밀번호 초기화

## 보안 고려사항

1. **JWT 시크릿 키**: 프로덕션 환경에서는 반드시 강력한 랜덤 문자열 사용
2. **HTTPS**: 프로덕션에서는 반드시 HTTPS 사용
3. **비밀번호 정책**: 최소 8자 이상 요구
4. **관리자 계정**: 첫 로그인 후 비밀번호 변경
5. **데이터베이스**: SQLite는 개발용, 프로덕션에서는 PostgreSQL/MySQL 권장

## 문제 해결

### 로그인이 안 되는 경우
- 관리자 승인 여부 확인
- 이메일/비밀번호 확인
- 브라우저 콘솔에서 에러 확인

### 관리자 계정을 잊어버린 경우
1. `data/hwp_reports.db` 파일 삭제
2. `uv run python init_db.py` 실행 (데이터베이스 재초기화)

### 토큰 만료 문제
- 기본 만료 시간: 24시간
- `.env`의 `JWT_EXPIRE_MINUTES` 값 조정 가능

## 추가 개선 사항 (권장)

1. 이메일 인증 추가
2. 비밀번호 변경 기능
3. 회원가입 시 이메일 알림
4. 토큰 사용량 제한 설정
5. 사용자 프로필 관리
6. 보고서 검색 및 필터링
7. 보고서 공유 기능
