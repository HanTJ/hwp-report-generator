# HWP Report Generator - Frontend

React + TypeScript + Ant Design 기반의 프론트엔드 애플리케이션입니다.

## 🚀 기술 스택

- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빌드 도구
- **React Router v6** - 라우팅
- **Ant Design** - UI 컴포넌트 라이브러리
- **Axios** - HTTP 클라이언트
- **TanStack Query (React Query)** - 서버 상태 관리

## 📁 프로젝트 구조

```
src/
├── components/         # 재사용 가능한 컴포넌트
│   ├── auth/           # 인증 관련 컴포넌트
│   ├── chat/           # 채팅 컴포넌트
│   ├── layout/         # 레이아웃 컴포넌트
│   ├── report/         # 보고서 관련 컴포넌트
│   ├── admin/          # 관리자 컴포넌트
│   └── common/         # 공통 컴포넌트
├── pages/              # 페이지 컴포넌트
├── services/           # API 서비스
├── hooks/              # 커스텀 훅
├── context/            # React Context
├── types/              # TypeScript 타입 정의
├── utils/              # 유틸리티 함수
└── constants/          # 상수
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
VITE_API_BASE_URL=
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:5173 으로 접속
현재 http://localhost:5173/chat에서 메인 화면 테스트 중

### 4. 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

## 📄 주요 페이지

- `/login` - 로그인 페이지
- `/register` - 회원가입 페이지
- `/` - 메인 페이지 (보고서 생성 및 목록)
- `/chat` - 메인 테스트 페이지 (보고서 생성 및 목록)
- `/change-password` - 비밀번호 변경 페이지
- `/admin` - 관리자 페이지 (관리자 전용)

## 🔐 인증 흐름

1. 로그인 시 JWT 토큰을 localStorage에 저장
2. Axios interceptor를 통해 모든 요청에 자동으로 토큰 추가
3. 401 에러 발생 시 자동으로 로그인 페이지로 리다이렉트
4. PrivateRoute로 인증 필요 페이지 보호
5. PublicRoute로 로그인 후 접근 불가 페이지 처리

## 🎨 스타일링

- Ant Design의 컴포넌트와 스타일 사용
- 한국어 locale 적용 (koKR)
- 반응형 디자인 지원

## 🧪 개발 가이드

### 새로운 페이지 추가

1. `src/pages/` 폴더에 새 페이지 컴포넌트 생성
2. `src/App.tsx`에 라우트 추가
3. 필요시 PrivateRoute 또는 PublicRoute로 감싸기

### 새로운 API 엔드포인트 추가

1. `src/constants/index.ts`에 엔드포인트 추가
2. `src/services/`에 API 함수 추가
3. 필요시 `src/hooks/`에 커스텀 훅 생성

### 타입 추가

`src/types/` 폴더에 TypeScript 인터페이스 정의

## 📝 코드 컨벤션

- 함수형 컴포넌트 사용
- TypeScript strict mode 준수
- ESLint/Prettier 규칙 준수
- 명확한 변수/함수 네이밍

## 🔧 트러블슈팅

### CORS 에러

백엔드 FastAPI에서 CORS 설정이 올바른지 확인하세요:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 토큰 만료

로그인 후 일정 시간이 지나면 토큰이 만료됩니다. 자동으로 로그인 페이지로 리다이렉트됩니다.
