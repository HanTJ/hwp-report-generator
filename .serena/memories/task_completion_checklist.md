# 작업 완료 체크리스트

## 코드 변경 후 수행할 작업

### 1. 테스트
```bash
# 서버 실행 테스트
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API 테스트 (브라우저에서)
http://localhost:8000/docs

# 주요 기능 수동 테스트
- 로그인/로그아웃
- 보고서 생성
- 파일 다운로드
```

### 2. 데이터베이스 마이그레이션
```bash
# 모델 변경 시 데이터베이스 재생성 필요
rm -f data/hwp_reports.db
uv run python init_db.py
```

### 3. 환경 변수 확인
`.env` 파일에 필요한 환경 변수가 설정되어 있는지 확인:
- `ANTHROPIC_API_KEY`: Claude API 키
- `JWT_SECRET_KEY`: JWT 시크릿 키
- `ADMIN_EMAIL`: 관리자 이메일
- `ADMIN_PASSWORD`: 관리자 비밀번호

### 4. 디렉토리 구조 확인
필요한 디렉토리가 생성되어 있는지 확인:
- `templates/`
- `static/`
- `output/`
- `temp/`
- `data/`

### 5. 의존성 업데이트
새로운 패키지 추가 시:
```bash
# requirements.txt에 추가 후
uv pip install -r requirements.txt
```

## 주요 확인 사항
- [ ] 코드에 한국어 주석 추가
- [ ] 타입 힌트 추가
- [ ] 예외 처리 및 로깅 추가
- [ ] API 엔드포인트 테스트
- [ ] 보안 검증 (인증, 권한 확인)
- [ ] 파일 경로 보안 검증
- [ ] 데이터베이스 변경 사항 확인

## 배포 전 체크리스트
- [ ] 환경 변수 설정 확인
- [ ] 관리자 계정 정보 변경
- [ ] 로그 레벨 조정
- [ ] CORS 설정 확인
- [ ] 보안 설정 강화