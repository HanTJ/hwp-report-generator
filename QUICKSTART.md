# 빠른 시작 가이드

## 1. 의존성 설치
```bash
uv pip install -r requirements.txt
```

## 2. 데이터베이스 초기화
```bash
uv run python init_db.py
```

예상 출력:
```
데이터베이스를 초기화합니다...
✅ 데이터베이스 테이블이 생성되었습니다.
✅ 관리자 계정이 생성되었습니다:
   이메일: hantj@kjbank.com
   비밀번호: kjbank123!@#
데이터베이스 초기화가 완료되었습니다!
```

## 3. 서버 실행
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 4. 접속하기

### 관리자 로그인
1. http://localhost:8000/login 접속
2. 이메일: `hantj@kjbank.com`
3. 비밀번호: `kjbank123!@#`
4. 로그인 후 http://localhost:8000/admin 에서 관리자 페이지 접속 가능

### 일반 사용자 회원가입
1. http://localhost:8000/register 접속
2. 이메일, 사용자명, 비밀번호 입력
3. 회원가입 완료 (관리자 승인 대기 상태)
4. 관리자가 http://localhost:8000/admin 에서 승인
5. 승인 후 로그인하여 보고서 생성 가능

## 5. 보고서 생성 테스트
1. 로그인 후 http://localhost:8000 접속
2. 보고서 주제 입력 (예: "2025년 디지털 뱅킹 서비스 현황 분석")
3. "보고서 생성" 버튼 클릭
4. 생성 완료 후 다운로드

## API 문서
http://localhost:8000/docs

## 데이터베이스 초기화 (재설정)
```bash
rm -f data/hwp_reports.db
uv run python init_db.py
```
