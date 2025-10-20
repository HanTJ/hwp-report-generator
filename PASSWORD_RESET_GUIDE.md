# 비밀번호 초기화 및 강제 변경 기능 가이드

## 기능 개요

관리자가 사용자의 비밀번호를 초기화하면, 해당 사용자는 다음 로그인 시 반드시 비밀번호를 변경해야 합니다.

## 구현 상세

### 1. 데이터베이스 변경
- `users` 테이블에 `password_reset_required` BOOLEAN 컬럼 추가
- 기본값: `False` (0)
- 비밀번호 초기화 시: `True` (1)
- 비밀번호 변경 완료 시: `False` (0)

### 2. API 엔드포인트

#### 비밀번호 변경 (사용자)
```
POST /api/auth/change-password
Authorization: Bearer {token}

Request Body:
{
  "current_password": "현재 비밀번호",
  "new_password": "새 비밀번호"
}

Response:
{
  "message": "비밀번호가 성공적으로 변경되었습니다."
}
```

#### 비밀번호 초기화 (관리자)
```
POST /api/admin/users/{user_id}/reset-password
Authorization: Bearer {admin_token}

Response:
{
  "message": "사용자의 비밀번호가 초기화되었습니다. 사용자는 다음 로그인 시 비밀번호를 변경해야 합니다.",
  "temporary_password": "랜덤생성된12자리"
}
```

### 3. 사용 흐름

#### 관리자 측
1. 관리자 페이지 (`/admin`) 접속
2. 사용자 목록에서 "비밀번호 초기화" 버튼 클릭
3. 임시 비밀번호 생성 및 표시
4. 임시 비밀번호를 사용자에게 안전하게 전달

#### 사용자 측
1. 임시 비밀번호로 로그인 시도
2. 로그인 성공 시 자동으로 `/change-password` 페이지로 리다이렉트
3. 경고 메시지 표시: "관리자가 귀하의 비밀번호를 초기화했습니다"
4. 현재 비밀번호(임시 비밀번호) 입력
5. 새 비밀번호 입력 및 확인
6. 비밀번호 변경 완료 후 메인 페이지로 이동

### 4. 보안 기능

- **강제 비밀번호 변경**: `password_reset_required=True`인 사용자는 비밀번호를 변경하기 전까지 다른 페이지에 접근할 수 없음
- **자동 리다이렉트**: 메인 페이지, 관리자 페이지 접근 시 자동으로 비밀번호 변경 페이지로 이동
- **비밀번호 검증**: 현재 비밀번호 확인 후에만 변경 가능
- **플래그 자동 해제**: 비밀번호 변경 완료 시 `password_reset_required` 자동으로 `False`로 변경

## 테스트 방법

### 1. 데이터베이스 마이그레이션
```bash
uv run python migrate_db.py
```

### 2. 테스트 시나리오

#### 시나리오 A: 일반 사용자 비밀번호 초기화
1. 일반 사용자로 회원가입
2. 관리자가 승인
3. 관리자가 해당 사용자의 비밀번호 초기화
4. 사용자가 임시 비밀번호로 로그인
5. 자동으로 비밀번호 변경 페이지로 이동 확인
6. 새 비밀번호로 변경 후 정상 접속 확인

#### 시나리오 B: 관리자 비밀번호 초기화
1. 다른 관리자가 관리자의 비밀번호 초기화
2. 임시 비밀번호로 로그인
3. 비밀번호 변경 페이지로 자동 이동
4. 새 비밀번호로 변경 후 관리자 페이지 접근 확인

## 파일 변경 사항

### 백엔드
- `models/user.py` - `password_reset_required` 필드 추가, `PasswordChange` 모델 추가
- `database/connection.py` - 스키마에 컬럼 추가
- `database/user_db.py` - `_row_to_user` 업데이트
- `routers/auth.py` - 비밀번호 변경 API 추가
- `routers/admin.py` - 비밀번호 초기화 시 플래그 설정
- `migrate_db.py` - 데이터베이스 마이그레이션 스크립트

### 프론트엔드
- `templates/change-password.html` - 비밀번호 변경 페이지
- `static/auth.js` - 로그인 후 리다이렉트 로직
- `static/script.js` - 메인 페이지 접근 시 체크
- `static/admin.js` - 관리자 페이지 접근 시 체크
- `static/style.css` - alert 스타일 추가
- `main.py` - `/change-password` 라우트 추가

## 주의사항

1. **임시 비밀번호 전달**: 관리자는 임시 비밀번호를 안전한 방법으로 사용자에게 전달해야 합니다 (예: 이메일, 별도 메신저)
2. **브라우저 새로고침**: 비밀번호 변경이 필요한 사용자는 페이지를 새로고침해도 계속 비밀번호 변경 페이지로 리다이렉트됩니다
3. **로그아웃 필요 없음**: 비밀번호 변경 후 자동으로 플래그가 해제되며 재로그인 불필요

## API 테스트 예시

### 관리자로 비밀번호 초기화
```bash
# 관리자 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"hantj@kjbank.com","password":"kjbank123!@#"}'

# 응답에서 access_token 획득
export TOKEN="받은_토큰"

# 사용자 비밀번호 초기화 (user_id=2)
curl -X POST http://localhost:8000/api/admin/users/2/reset-password \
  -H "Authorization: Bearer $TOKEN"
```

### 사용자로 비밀번호 변경
```bash
# 임시 비밀번호로 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"임시비밀번호"}'

# 응답에서 access_token과 password_reset_required=true 확인
export USER_TOKEN="받은_토큰"

# 비밀번호 변경
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"임시비밀번호","new_password":"새비밀번호123!@#"}'
```

## 문제 해결

### Q: 비밀번호를 변경했는데도 계속 비밀번호 변경 페이지로 이동합니다
A: 브라우저의 localStorage를 확인하세요. `localStorage.setItem('user', JSON.stringify(updatedUser))`가 제대로 실행되었는지 확인합니다.
```javascript
// 브라우저 콘솔에서 확인
JSON.parse(localStorage.getItem('user')).password_reset_required
// false가 나와야 정상
```

### Q: 데이터베이스에 컬럼이 없다는 오류가 발생합니다
A: 마이그레이션 스크립트를 실행하세요:
```bash
uv run python migrate_db.py
```
