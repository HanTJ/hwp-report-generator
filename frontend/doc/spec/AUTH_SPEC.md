# 프론트엔드 인증 시스템 명세서

**작성일**: 2025-11-07
**버전**: 1.0
**프로젝트**: HWP Report Generator Frontend

---

## 목차

1. [개요](#개요)
2. [아키텍처](#아키텍처)
3. [핵심 컴포넌트](#핵심-컴포넌트)
4. [인증 플로우](#인증-플로우)
5. [API 엔드포인트](#api-엔드포인트)
6. [타입 정의](#타입-정의)
7. [보안 고려사항](#보안-고려사항)
8. [사용 예시](#사용-예시)

---

## 개요

HWP Report Generator 프론트엔드의 인증 시스템은 **JWT(JSON Web Token) 기반 인증**을 사용하여 사용자 인증 및 권한 관리를 수행합니다.

### 주요 기능

- **회원가입**: 이메일, 사용자명, 비밀번호로 계정 생성 (관리자 승인 필요)
- **로그인**: JWT 토큰 발급 및 로컬스토리지 저장
- **로그아웃**: 토큰 및 사용자 정보 삭제
- **비밀번호 변경**: 현재 비밀번호 확인 후 변경
- **자동 로그인**: 페이지 새로고침 시 토큰으로 세션 유지
- **자동 로그아웃**: 토큰 만료 시 401 에러 감지 및 자동 처리

### 기술 스택

- **인증 방식**: JWT (JSON Web Token)
- **상태 관리**: React Context API
- **HTTP 클라이언트**: Axios
- **저장소**: LocalStorage
- **백엔드 API**: FastAPI (`/api/auth/*`)

---

## 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend App                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               AuthProvider (Context)                  │  │
│  │  - user state                                         │  │
│  │  - isAuthenticated                                    │  │
│  │  - login/logout/register/changePassword               │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           useAuth Hook (Custom Hook)                  │  │
│  │  - AuthContext를 편리하게 사용                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             authApi (API Client)                      │  │
│  │  - login(), register(), logout()                      │  │
│  │  - changePassword(), getMyInfo()                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            api (Axios Instance)                       │  │
│  │  - Request Interceptor: 토큰 자동 추가               │  │
│  │  - Response Interceptor: 401 자동 처리               │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         storage (LocalStorage Wrapper)                │  │
│  │  - getToken(), setToken()                             │  │
│  │  - getUser(), setUser()                               │  │
│  │  - clear()                                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
                  LocalStorage (Browser)
                  - access_token
                  - user
```

### 데이터 플로우

```mermaid
sequenceDiagram
    participant User
    participant Component
    participant useAuth
    participant authApi
    participant axios
    participant Storage
    participant Backend

    User->>Component: 로그인 버튼 클릭
    Component->>useAuth: login({ email, password })
    useAuth->>authApi: login(data)
    authApi->>axios: POST /api/auth/login
    axios->>Backend: HTTP Request
    Backend-->>axios: { access_token, user }
    axios-->>authApi: Response
    authApi-->>useAuth: { access_token, user }
    useAuth->>Storage: setToken(token)
    useAuth->>Storage: setUser(user)
    useAuth->>useAuth: setUser(user)
    useAuth-->>Component: 로그인 완료
    Component-->>User: 메인 페이지 이동
```

---

## 핵심 컴포넌트

### 1. authApi.ts

**위치**: `frontend/src/services/authApi.ts`

**역할**: 백엔드 인증 API와 통신하는 클라이언트 함수 모음

**주요 함수**:

| 함수 | 메서드 | 엔드포인트 | 설명 |
|------|--------|-----------|------|
| `login(data)` | POST | `/api/auth/login` | 로그인, JWT 토큰 반환 |
| `register(data)` | POST | `/api/auth/register` | 회원가입 |
| `logout()` | POST | `/api/auth/logout` | 로그아웃 (서버 로깅용) |
| `changePassword(data)` | POST | `/api/auth/change-password` | 비밀번호 변경 |
| `getMyInfo()` | GET | `/api/auth/me` | 현재 사용자 정보 조회 |

**에러 처리**:
- 모든 함수는 `ApiResponse<T>` 타입의 표준 응답 처리
- `success: false` 시 `error.message`를 throw

**예시**:

```typescript
// 로그인
const response = await authApi.login({ email, password });
// response: { access_token, token_type, user }

// 회원가입
await authApi.register({ email, username, password });
// 성공 시 void, 실패 시 throw Error

// 로그아웃
await authApi.logout();
// localStorage에서 토큰 자동 제거 (finally 블록)
```

---

### 2. AuthContext.tsx

**위치**: `frontend/src/context/AuthContext.tsx`

**역할**: 인증 상태를 앱 전체에서 공유하는 Context Provider

**제공하는 상태**:

```typescript
interface AuthContextType {
  user: User | null;                    // 현재 로그인한 사용자
  isAuthenticated: boolean;             // 로그인 여부 (!!user)
  isLoading: boolean;                   // 초기 로딩 상태
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  changePassword: (data: ChangePasswordRequest) => Promise<void>;
}
```

**주요 기능**:

1. **초기화 (useEffect)**:
   - 컴포넌트 마운트 시 localStorage에서 토큰과 사용자 정보 복구
   - 페이지 새로고침 시 로그인 상태 유지

2. **login()**:
   - authApi.login() 호출
   - 성공 시 토큰과 사용자 정보를 localStorage 및 state에 저장

3. **logout()**:
   - authApi.logout() 호출 (API 실패해도 진행)
   - localStorage 전체 삭제 (`storage.clear()`)
   - user 상태를 null로 설정

4. **changePassword()**:
   - authApi.changePassword() 호출
   - 성공 시 `password_reset_required` 플래그를 false로 변경

**사용법**:

```typescript
// App.tsx에서 최상위에 설정
<AuthProvider>
  <App />
</AuthProvider>
```

---

### 3. useAuth.ts

**위치**: `frontend/src/hooks/useAuth.ts`

**역할**: AuthContext를 편리하게 사용하기 위한 Custom Hook

**기능**:
- `useContext(AuthContext)` 래핑
- AuthProvider 없이 사용 시 에러 발생 (안전장치)

**사용법**:

```typescript
import { useAuth } from '../hooks/useAuth';

function LoginPage() {
  const { user, login, logout, isAuthenticated } = useAuth();

  const handleLogin = async () => {
    await login({ email, password });
  };
}
```

---

### 4. api.ts (Axios Instance)

**위치**: `frontend/src/services/api.ts`

**역할**: Axios 인스턴스 생성 및 인터셉터 설정

#### Request Interceptor (요청 인터셉터)

**기능**: 모든 API 요청에 JWT 토큰 자동 추가

**동작**:
1. Public 엔드포인트(`/api/auth/login`, `/api/auth/register`) 제외
2. Protected 엔드포인트에 `Authorization: Bearer {token}` 헤더 자동 추가
3. 토큰은 localStorage에서 자동으로 가져옴

**코드**:

```typescript
api.interceptors.request.use((config) => {
  if (isPublicEndpoint(config.url)) {
    return config;
  }

  const token = storage.getToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### Response Interceptor (응답 인터셉터)

**기능**: 401 Unauthorized 에러 시 자동 로그아웃

**동작**:
1. 정상 응답(200~299): 그대로 통과
2. 401 에러: localStorage 삭제 + 로그인 페이지로 강제 이동
3. 기타 에러: 그대로 에러 반환

**코드**:

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      storage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**주의사항**:
- 401 에러 시 React Router의 `navigate()` 대신 `window.location.href` 사용
- 이유: Interceptor는 React 컴포넌트 외부에서 실행되므로 `useNavigate()` 사용 불가

---

### 5. storage.ts

**위치**: `frontend/src/utils/storage.ts`

**역할**: LocalStorage를 안전하게 관리하는 유틸리티

**주요 함수**:

| 함수 | 설명 |
|------|------|
| `getToken()` | 저장된 토큰 가져오기 |
| `setToken(token)` | 토큰 저장 |
| `removeToken()` | 토큰 삭제 |
| `getUser()` | 사용자 정보 가져오기 (JSON 파싱) |
| `setUser(user)` | 사용자 정보 저장 (JSON 직렬화) |
| `removeUser()` | 사용자 정보 삭제 |
| `clear()` | 모든 인증 데이터 삭제 (로그아웃용) |

**저장 키**:
- `access_token`: JWT 토큰
- `user`: 사용자 정보 (JSON 문자열)

**에러 처리**:
- `getUser()`: JSON 파싱 실패 시 null 반환

---

### 6. types/auth.ts

**위치**: `frontend/src/types/auth.ts`

**역할**: 인증 관련 TypeScript 타입 정의

**주요 타입**:

```typescript
// 로그인 요청
export interface LoginRequest {
  email: string;
  password: string;
}

// 회원가입 요청
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

// 비밀번호 변경 요청
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// 로그인 응답
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 사용자 정보
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;            // 관리자 승인 여부
  is_admin: boolean;             // 관리자 권한
  password_reset_required: boolean; // 비밀번호 변경 필요
  created_at: string;            // 가입일 (ISO 8601)
}
```

---

## 인증 플로우

### 1. 로그인 플로우

```mermaid
flowchart TD
    A[사용자가 로그인 폼 제출] --> B[useAuth.login 호출]
    B --> C[authApi.login 호출]
    C --> D[POST /api/auth/login]
    D --> E{응답 성공?}
    E -->|실패| F[에러 메시지 표시]
    E -->|성공| G[storage.setToken]
    G --> H[storage.setUser]
    H --> I[AuthContext.setUser]
    I --> J[isAuthenticated = true]
    J --> K[메인 페이지로 이동]
```

**코드 예시**:

```typescript
const { login } = useAuth();

const handleLogin = async (values: LoginRequest) => {
  try {
    await login(values);
    navigate('/');
  } catch (error) {
    message.error('로그인에 실패했습니다.');
  }
};
```

---

### 2. 회원가입 플로우

```mermaid
flowchart TD
    A[사용자가 회원가입 폼 제출] --> B[useAuth.register 호출]
    B --> C[authApi.register 호출]
    C --> D[POST /api/auth/register]
    D --> E{응답 성공?}
    E -->|실패| F[에러 메시지 표시]
    E -->|성공| G[성공 메시지 표시]
    G --> H[로그인 페이지로 이동]
    H --> I[관리자 승인 대기]
```

**특징**:
- 회원가입 후 자동 로그인하지 않음
- `is_active: false` 상태로 생성됨
- 관리자 승인 후 로그인 가능

---

### 3. 로그아웃 플로우

```mermaid
flowchart TD
    A[사용자가 로그아웃 클릭] --> B[useAuth.logout 호출]
    B --> C[authApi.logout 호출]
    C --> D[POST /api/auth/logout]
    D --> E[finally 블록 실행]
    E --> F[storage.clear]
    F --> G[AuthContext.setUser null]
    G --> H[isAuthenticated = false]
    H --> I[로그인 페이지로 이동]
```

**특징**:
- API 호출 실패해도 로그아웃 진행 (finally 블록)
- localStorage 및 Context 상태 모두 정리

---

### 4. 자동 로그인 (페이지 새로고침)

```mermaid
flowchart TD
    A[페이지 로드/새로고침] --> B[AuthProvider useEffect 실행]
    B --> C[storage.getToken]
    C --> D{토큰 존재?}
    D -->|없음| E[isLoading = false]
    D -->|있음| F[storage.getUser]
    F --> G{사용자 정보 존재?}
    G -->|없음| E
    G -->|있음| H[AuthContext.setUser]
    H --> I[isAuthenticated = true]
    I --> E
```

**구현**:

```typescript
useEffect(() => {
  const token = storage.getToken();
  const savedUser = storage.getUser();

  if (token && savedUser) {
    setUser(savedUser);
  }
  setIsLoading(false);
}, []);
```

---

### 5. 토큰 만료 처리 (401 에러)

```mermaid
flowchart TD
    A[API 요청] --> B[서버가 401 응답]
    B --> C[Response Interceptor]
    C --> D[storage.clear]
    D --> E[window.location.href = /login]
    E --> F[로그인 페이지 표시]
```

**특징**:
- 모든 API 요청에 대해 자동으로 동작
- React Router가 아닌 `window.location.href` 사용 (Interceptor는 React 외부)

---

### 6. 비밀번호 변경 플로우

```mermaid
flowchart TD
    A[사용자가 비밀번호 변경 폼 제출] --> B[useAuth.changePassword 호출]
    B --> C[authApi.changePassword 호출]
    C --> D[POST /api/auth/change-password]
    D --> E{응답 성공?}
    E -->|실패| F[에러 메시지 표시]
    E -->|성공| G[user.password_reset_required = false]
    G --> H[storage.setUser 업데이트]
    H --> I[AuthContext.setUser 업데이트]
    I --> J[성공 메시지 표시]
```

---

## API 엔드포인트

### 백엔드 API 명세

**Base URL**: `http://localhost:8000`

| 엔드포인트 | 메서드 | 인증 | 설명 |
|-----------|--------|------|------|
| `/api/auth/register` | POST | 불필요 | 회원가입 |
| `/api/auth/login` | POST | 불필요 | 로그인 |
| `/api/auth/logout` | POST | 필요 | 로그아웃 |
| `/api/auth/me` | GET | 필요 | 내 정보 조회 |
| `/api/auth/change-password` | POST | 필요 | 비밀번호 변경 |

---

### 1. 회원가입

**요청**:

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "홍길동",
  "password": "password123"
}
```

**응답 (성공)**:

```json
{
  "success": true,
  "data": {
    "message": "회원가입이 완료되었습니다. 관리자의 승인을 기다려주세요.",
    "user_id": 123,
    "email": "user@example.com"
  },
  "error": null
}
```

**응답 (실패 - 이메일 중복)**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.DUPLICATE_EMAIL",
    "httpStatus": 400,
    "message": "이미 등록된 이메일입니다.",
    "hint": "다른 이메일 주소를 사용해주세요."
  }
}
```

---

### 2. 로그인

**요청**:

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답 (성공)**:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 123,
      "email": "user@example.com",
      "username": "홍길동",
      "is_active": true,
      "is_admin": false,
      "password_reset_required": false,
      "created_at": "2025-11-07T10:30:00"
    }
  },
  "error": null
}
```

**응답 (실패 - 잘못된 자격증명)**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_CREDENTIALS",
    "httpStatus": 401,
    "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
    "hint": "입력 정보를 다시 확인해주세요."
  }
}
```

**응답 (실패 - 비활성 계정)**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.ACCOUNT_INACTIVE",
    "httpStatus": 403,
    "message": "계정이 활성화되지 않았습니다.",
    "hint": "관리자의 승인을 기다려주세요."
  }
}
```

---

### 3. 로그아웃

**요청**:

```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**응답**:

```json
{
  "success": true,
  "data": {
    "message": "로그아웃되었습니다."
  },
  "error": null
}
```

---

### 4. 내 정보 조회

**요청**:

```http
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**응답**:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "email": "user@example.com",
    "username": "홍길동",
    "is_active": true,
    "is_admin": false,
    "password_reset_required": false,
    "created_at": "2025-11-07T10:30:00"
  },
  "error": null
}
```

---

### 5. 비밀번호 변경

**요청**:

```http
POST /api/auth/change-password
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "current_password": "old_password",
  "new_password": "new_password123"
}
```

**응답 (성공)**:

```json
{
  "success": true,
  "data": {
    "message": "비밀번호가 성공적으로 변경되었습니다."
  },
  "error": null
}
```

**응답 (실패 - 잘못된 현재 비밀번호)**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH.INVALID_PASSWORD",
    "httpStatus": 400,
    "message": "현재 비밀번호가 올바르지 않습니다.",
    "hint": "현재 사용 중인 비밀번호를 확인해주세요."
  }
}
```

---

## 타입 정의

### TypeScript 인터페이스

```typescript
// 로그인 요청
export interface LoginRequest {
  email: string;
  password: string;
}

// 회원가입 요청
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

// 비밀번호 변경 요청
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// 로그인 응답
export interface LoginResponse {
  access_token: string;   // JWT 토큰
  token_type: string;     // "bearer"
  user: User;             // 사용자 정보
}

// 사용자 정보
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;                // 활성화 여부 (관리자 승인)
  is_admin: boolean;                 // 관리자 권한
  password_reset_required: boolean;  // 비밀번호 변경 필요 여부
  created_at: string;                // 가입일 (ISO 8601)
}
```

---

## 보안 고려사항

### 1. JWT 토큰 저장

**현재**: LocalStorage에 토큰 저장

**장점**:
- 페이지 새로고침 시 세션 유지
- 구현이 간단함

**단점**:
- XSS(Cross-Site Scripting) 공격에 취약
- JavaScript로 접근 가능

**권장 사항**:
- ⚠️ **프로덕션 환경에서는 HttpOnly Cookie 사용 권장**
- Cookie는 JavaScript로 접근 불가능하여 XSS 방어

---

### 2. 토큰 만료

**현재 동작**:
- 백엔드에서 JWT 만료 시간 설정 (`.env`의 `JWT_EXPIRE_MINUTES`)
- 만료된 토큰으로 요청 시 401 에러
- Response Interceptor가 자동으로 로그아웃 처리

**개선 가능**:
- Refresh Token 구현 (Access Token + Refresh Token)
- 자동 토큰 갱신

---

### 3. HTTPS 사용

**중요**: 프로덕션 환경에서는 반드시 HTTPS 사용

**이유**:
- HTTP는 평문 전송으로 토큰 탈취 가능
- HTTPS는 SSL/TLS 암호화로 안전한 통신

---

### 4. CORS (Cross-Origin Resource Sharing)

**설정**: 백엔드에서 CORS 허용 origin 설정

**백엔드 설정 예시** (`backend/app/main.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 5. 비밀번호 정책

**현재**: 백엔드에서 비밀번호 해싱 (bcrypt)

**권장 추가 사항**:
- 프론트엔드 비밀번호 검증 (최소 8자, 대소문자/숫자/특수문자 포함)
- 비밀번호 강도 표시기

---

## 사용 예시

### 1. 로그인 페이지

```typescript
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, message } from 'antd';
import type { LoginRequest } from '../types/auth';

function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // 이미 로그인한 경우 메인 페이지로 리다이렉트
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (values: LoginRequest) => {
    try {
      await login(values);
      message.success('로그인 성공!');
      navigate('/');
    } catch (error) {
      message.error(error.message || '로그인에 실패했습니다.');
    }
  };

  return (
    <Form onFinish={handleSubmit}>
      <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
        <Input placeholder="이메일" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true }]}>
        <Input.Password placeholder="비밀번호" />
      </Form.Item>
      <Button type="primary" htmlType="submit">
        로그인
      </Button>
    </Form>
  );
}
```

---

### 2. 보호된 라우트 (Protected Route)

```typescript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  // 로딩 중
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // 로그인하지 않은 경우 로그인 페이지로 리다이렉트
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 로그인한 경우 페이지 렌더링
  return <>{children}</>;
}

// 사용 예시 (App.tsx)
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/" element={
    <ProtectedRoute>
      <HomePage />
    </ProtectedRoute>
  } />
</Routes>
```

---

### 3. 사용자 정보 표시

```typescript
import { useAuth } from '../hooks/useAuth';

function UserProfile() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div>
      <h2>{user.username}님 환영합니다!</h2>
      <p>이메일: {user.email}</p>
      <p>가입일: {new Date(user.created_at).toLocaleDateString()}</p>
      {user.is_admin && <span>관리자</span>}
      <button onClick={logout}>로그아웃</button>
    </div>
  );
}
```

---

### 4. 비밀번호 변경

```typescript
import { useAuth } from '../hooks/useAuth';
import { Form, Input, Button, message } from 'antd';
import type { ChangePasswordRequest } from '../types/auth';

function ChangePasswordPage() {
  const { changePassword } = useAuth();
  const [form] = Form.useForm();

  const handleSubmit = async (values: ChangePasswordRequest) => {
    try {
      await changePassword(values);
      message.success('비밀번호가 성공적으로 변경되었습니다.');
      form.resetFields();
    } catch (error) {
      message.error(error.message || '비밀번호 변경에 실패했습니다.');
    }
  };

  return (
    <Form form={form} onFinish={handleSubmit}>
      <Form.Item
        name="current_password"
        rules={[{ required: true, message: '현재 비밀번호를 입력하세요.' }]}
      >
        <Input.Password placeholder="현재 비밀번호" />
      </Form.Item>
      <Form.Item
        name="new_password"
        rules={[
          { required: true, message: '새 비밀번호를 입력하세요.' },
          { min: 8, message: '비밀번호는 최소 8자 이상이어야 합니다.' }
        ]}
      >
        <Input.Password placeholder="새 비밀번호" />
      </Form.Item>
      <Button type="primary" htmlType="submit">
        비밀번호 변경
      </Button>
    </Form>
  );
}
```

---

### 5. API 호출 예시 (토큰 자동 포함)

```typescript
import api from '../services/api';

// Protected 엔드포인트 - 토큰 자동 추가
async function fetchTopics() {
  const response = await api.get('/api/topics');
  return response.data;
}

// Public 엔드포인트 - 토큰 추가 안 됨
async function login(email: string, password: string) {
  const response = await api.post('/api/auth/login', { email, password });
  return response.data;
}
```

---

## 파일 구조

```
frontend/src/
├── context/
│   └── AuthContext.tsx          # 인증 Context Provider
├── hooks/
│   └── useAuth.ts               # 인증 Custom Hook
├── services/
│   ├── api.ts                   # Axios 인스턴스 + 인터셉터
│   └── authApi.ts               # 인증 API 클라이언트
├── types/
│   └── auth.ts                  # 인증 타입 정의
├── utils/
│   └── storage.ts               # LocalStorage 래퍼
└── constants/
    └── index.ts                 # API 엔드포인트 상수
```

---

## 참고 자료

### 관련 문서

- **백엔드 인증 API**: `backend/app/routers/auth.py`
- **백엔드 인증 유틸**: `backend/app/utils/auth.py`
- **프로젝트 가이드**: `CLAUDE.md`
- **백엔드 온보딩**: `BACKEND_ONBOARDING.md`

### 외부 문서

- [JWT.io - JSON Web Token Introduction](https://jwt.io/introduction)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [React Context API](https://react.dev/learn/passing-data-deeply-with-context)

---

**마지막 업데이트**: 2025-11-07
**작성자**: Claude Code
**버전**: 1.0
