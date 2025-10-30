# Frontend Onboarding Guide

> HWP Report Generator 프론트엔드 온보딩 가이드
>
> 작성일: 2025-10-30
> 버전: v2.0 (대화형 시스템)

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [프로젝트 구조](#프로젝트-구조)
4. [환경 설정 및 실행](#환경-설정-및-실행)
5. [핵심 개념](#핵심-개념)
6. [주요 기능 흐름](#주요-기능-흐름)
7. [API 통신](#api-통신)
8. [상태 관리](#상태-관리)
9. [스타일링](#스타일링)
10. [주요 컴포넌트](#주요-컴포넌트)
11. [트러블슈팅](#트러블슈팅)
12. [개발 가이드라인](#개발-가이드라인)

---

## 프로젝트 개요

### HWP Report Generator Frontend

**주요 기능**:

- 🤖 Claude AI와의 실시간 대화
- 📝 Markdown 형식 보고서 미리보기
- 📥 HWPX 파일 다운로드
- 💬 대화 기록 관리 (Topics/Messages)
- 👤 사용자 인증 및 권한 관리
- 👨‍💼 관리자 페이지

**v2.0 특징**:

- 단일 요청 → **대화형 시스템** 전환
- 실시간 스트리밍 응답 (예정)
- 대화 이력 저장 및 관리
- 아티팩트(산출물) 관리 시스템

---

## 기술 스택

### Core

| 기술           | 버전   | 역할          |
| -------------- | ------ | ------------- |
| **React**      | 19.1.1 | UI 라이브러리 |
| **TypeScript** | 5.9.3  | 타입 안정성   |
| **Vite**       | 7.1.7  | 빌드 도구     |

### UI & Routing

| 기술                 | 버전   | 역할                   |
| -------------------- | ------ | ---------------------- |
| **Ant Design**       | 5.27.6 | UI 컴포넌트 라이브러리 |
| **Ant Design Icons** | 6.1.0  | 아이콘                 |
| **React Router DOM** | 7.9.4  | 클라이언트 라우팅      |

### State Management & Data Fetching

| 기술                     | 버전     | 역할                    |
| ------------------------ | -------- | ----------------------- |
| **TanStack React Query** | 5.90.5   | 서버 상태 관리 (미사용) |
| **Axios**                | 1.12.2   | HTTP 클라이언트         |
| **Context API**          | Built-in | 전역 상태 관리 (인증)   |

### Dev Tools

| 기술                  | 버전   | 역할       |
| --------------------- | ------ | ---------- |
| **ESLint**            | 9.36.0 | 코드 린팅  |
| **TypeScript ESLint** | 8.45.0 | TS 린팅    |
| **Vite Plugin React** | 5.0.4  | React 지원 |

---

## 프로젝트 구조

```
frontend/
├── public/                      # 정적 파일
│   └── vite.svg
│
├── src/
│   ├── assets/                  # 이미지, 폰트 등
│   │   └── logo.png
│   │
│   ├── components/              # 재사용 가능한 컴포넌트
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx           # 메시지 입력 UI
│   │   │   ├── ChatInput.module.css
│   │   │   ├── ChatMessage.tsx         # 메시지 버블 UI
│   │   │   └── ChatMessage.module.css
│   │   │
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx             # 좌측 사이드바 (토픽 목록)
│   │   │   ├── Sidebar.module.css
│   │   │   ├── MainLayout.tsx          # 페이지 레이아웃
│   │   │   └── MainLayout.module.css
│   │   │
│   │   └── report/
│   │       ├── ReportPreview.tsx       # 보고서 미리보기
│   │       ├── ReportPreview.module.css
│   │       ├── DownloadedFiles.tsx     # 다운로드 파일 목록
│   │       └── DownloadedFiles.module.css
│   │
│   ├── context/                 # React Context
│   │   └── AuthContext.tsx             # 인증 상태 관리
│   │
│   ├── hooks/                   # Custom Hooks
│   │   └── useAuth.ts                  # AuthContext 래퍼
│   │
│   ├── pages/                   # 페이지 컴포넌트
│   │   ├── LoginPage.tsx               # 로그인
│   │   ├── RegisterPage.tsx            # 회원가입
│   │   ├── MainChatPage.tsx            # 메인 채팅 페이지 (개발 중) ⭐
│   │   ├── MainPage.tsx                # 메인 페이지 ⭐
│   │   ├── AdminPage.tsx               # 관리자 페이지
│   │   └── *.module.css
│   │
│   ├── services/                # API 클라이언트
│   │   ├── api.ts                      # Axios 인스턴스
│   │   ├── authApi.ts                  # 인증 API
│   │   ├── topicApi.ts                 # 토픽 API
│   │   ├── messageApi.ts               # 메시지 API
│   │   ├── artifactApi.ts              # 아티팩트 API
│   │   ├── adminApi.ts                 # 관리자 API
│   │   └── reportApi.ts                # 보고서 API (Deprecated)
│   │
│   ├── types/                   # TypeScript 타입 정의
│   │   ├── api.ts                      # 공통 API 응답 타입
│   │   ├── auth.ts                     # 인증 관련 타입
│   │   ├── user.ts                     # 사용자 타입
│   │   ├── topic.ts                    # 토픽 타입
│   │   ├── message.ts                  # 메시지 타입
│   │   ├── artifact.ts                 # 아티팩트 타입
│   │   └── report.ts                   # 보고서 타입 (Deprecated)
│   │
│   ├── utils/                   # 유틸리티 함수
│   │   └── storage.ts                  # 로컬스토리지 래퍼
│   │
│   ├── constants/               # 상수 정의
│   │   └── index.ts                    # API 엔드포인트, 키 등
│   │
│   ├── App.tsx                  # 앱 루트 컴포넌트
│   ├── main.tsx                 # 엔트리 포인트
│   └── index.css                # 글로벌 스타일
│
├── package.json                 # 의존성 관리
├── tsconfig.json                # TypeScript 설정
├── vite.config.ts               # Vite 설정 (프록시 포함)
├── eslint.config.js             # ESLint 설정
├── CLAUDE.md                    # 프론트엔드 가이드
└── FRONTEND_API_STATUS.md       # API 구현 현황
```

---

## 환경 설정 및 실행

### 1. 사전 요구사항

- **Node.js**: v18 이상
- **npm**: v9 이상
- **백엔드 서버**: `http://localhost:8000` 실행 중이어야 함

### 2. 설치

```bash
cd frontend
npm install
```

### 3. 개발 서버 실행

```bash
npm run dev
```

**접속 URL**: `http://localhost:5173`

### 4. 빌드

```bash
npm run build
```

빌드 결과물: `frontend/dist/`

### 5. 프리뷰 (빌드 결과 확인)

```bash
npm run preview
```

---

## 핵심 개념

### 1. **대화형 시스템 구조** (v2.0)

```
Topic (대화 스레드)
  ├── Messages (대화 메시지들)
  │   ├── Message 1 (user): "디지털뱅킹 트렌드 보고서 작성해줘"
  │   ├── Message 2 (assistant): "# 디지털뱅킹 트렌드..."
  │   │   └── Artifact 1 (MD): report_v1.md
  │   ├── Message 3 (user): "요약 부분을 더 자세히 작성해줘"
  │   └── Message 4 (assistant): "# 디지털뱅킹 트렌드 (수정)..."
  │       └── Artifact 2 (MD): report_v2.md
  └── Metadata
      ├── input_prompt: "디지털뱅킹 트렌드 보고서 작성해줘"
      ├── generated_title: "디지털뱅킹 트렌드 분석"
      ├── language: "ko"
      └── status: "active"
```

### 2. **아티팩트 (Artifacts)**

생성된 보고서 파일을 관리하는 시스템입니다.

**종류**:

- `md`: Markdown 파일 (AI가 생성)
- `hwpx`: HWPX 파일 (MD에서 변환)
- `pdf`: PDF 파일 (미래 지원 예정)

**버전 관리**:

- 같은 토픽에서 보고서를 수정하면 v2, v3... 증가
- 각 버전은 별도 파일로 저장

### 3. **표준 API 응답 형식**

모든 백엔드 API는 표준화된 응답을 반환합니다.

**성공 응답**:

```typescript
{
  success: true,
  data: { /* 실제 데이터 */ },
  error: null,
  meta: { requestId: "req_abc123" },
  feedback: []
}
```

**실패 응답**:

```typescript
{
  success: false,
  data: null,
  error: {
    code: "AUTH.INVALID_TOKEN",
    httpStatus: 401,
    message: "유효하지 않은 토큰입니다.",
    details: { reason: "expired" },
    traceId: "trace_xyz789",
    hint: "다시 로그인해 주세요."
  },
  meta: { requestId: "req_abc123" },
  feedback: []
}
```

### 4. **JWT 인증 방식**

**Stateless 토큰**:

- 서버에 세션 저장 안 함
- 토큰에 사용자 정보 포함 (`user_id`, `email`)
- 만료 시간: 24시간

**인증 플로우**:

1. 로그인 → JWT 토큰 받음
2. `localStorage`에 토큰 저장
3. Protected API 요청에 `Authorization: Bearer {token}` 헤더 자동 포함
4. 백엔드에서 토큰 검증

**Public vs Protected 엔드포인트**:

- **Public** (토큰 불필요):
  - `POST /api/auth/login` - 로그인
  - `POST /api/auth/register` - 회원가입

- **Protected** (토큰 필요):
  - 나머지 모든 API (토픽, 메시지, 아티팩트, 로그아웃 등)

---

## 주요 기능 흐름

### 1. 로그인 플로우

```
1. LoginPage
   ↓
2. authApi.login(email, password)
   ↓
3. Backend: POST /api/auth/login
   ↓
4. 성공 → { access_token, user }
   ↓
5. AuthContext.login()
   - localStorage에 토큰 저장
   - user 상태 업데이트
   ↓
6. navigate('/') → MainChatPage
```

### 2. 보고서 생성 플로우 (첫 번째 메시지)

```
1. MainChatPage: 사용자가 "디지털뱅킹 트렌드 보고서" 입력
   ↓
2. handleSendMessage()
   - tempUserMessage를 UI에 추가
   - setIsGenerating(true)
   ↓
3. topicApi.generateTopic({ input_prompt, language: "ko" })
   ↓
4. Backend: POST /api/topics/generate
   - Claude API 호출 → 보고서 생성
   - Topic, Message, Artifact(MD) 저장
   - 응답: { topic_id, md_path }
   ↓
5. messageApi.listMessages(topic_id)
   - 모든 메시지 불러오기
   ↓
6. artifactApi.listArtifactsByTopic(topic_id)
   - 아티팩트 목록 불러오기
   ↓
7. artifactApi.getArtifactContent(artifact_id)
   - MD 파일 내용 불러오기
   ↓
8. UI 업데이트
   - messages 상태 업데이트
   - 보고서 버튼 표시
   - setIsGenerating(false)
```

### 3. 보고서 다운로드 플로우

```
1. 사용자가 "다운로드" 버튼 클릭
   ↓
2. handleDownload(reportData)
   - antdMessage.loading("HWPX 파일로 변환 중...")
   ↓
3. artifactApi.convertToHwpx(artifact_id)
   ↓
4. Backend: POST /api/artifacts/{artifact_id}/convert
   ⚠️ 현재 501 에러 (미구현)
   ↓
5. 변환 성공 → { hwpx_artifact_id, filename }
   ↓
6. artifactApi.downloadArtifact(hwpx_artifact_id, filename)
   ↓
7. Backend: GET /api/artifacts/{artifact_id}/download
   - FileResponse로 HWPX 파일 반환
   ↓
8. 브라우저 다운로드 트리거
   - Blob 생성 → <a> 태그 클릭
   ↓
9. downloadedFiles 상태에 추가
   - antdMessage.success("HWPX 파일이 다운로드되었습니다.")
```

### 4. 로그아웃 플로우

```
1. Sidebar: 사용자가 "로그아웃" 버튼 클릭
   ↓
2. handleLogout()
   ↓
3. AuthContext.logout()
   ↓
4. authApi.logout()
   - Backend: POST /api/auth/logout
   - localStorage.removeItem('access_token')
   ↓
5. storage.clear()
   - 모든 로컬스토리지 데이터 삭제
   ↓
6. setUser(null)
   - 앱 전체 로그인 상태 해제
   ↓
7. navigate('/login')
```

---

## API 통신

### API 클라이언트 구조

**Base Client** (`services/api.ts`):

```typescript
import axios from "axios";

// Public 엔드포인트 목록 (JWT 불필요)
const PUBLIC_ENDPOINTS = [
  '/api/auth/login',
  '/api/auth/register',
];

const isPublicEndpoint = (url?: string): boolean => {
  if (!url) return false;
  return PUBLIC_ENDPOINTS.some(endpoint => url.includes(endpoint));
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 인터셉터: JWT 토큰 자동 추가 (Public 엔드포인트 제외)
api.interceptors.request.use((config) => {
  // Public 엔드포인트는 토큰 추가 안 함
  if (isPublicEndpoint(config.url)) {
    return config;
  }

  // Protected 엔드포인트는 토큰 추가
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터: 401 에러 시 로그인 페이지로
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

**주요 특징**:

- **Public 엔드포인트 필터링**: 로그인/회원가입 요청에는 토큰을 추가하지 않음
- **자동 토큰 추가**: Protected 엔드포인트에는 자동으로 JWT 토큰 포함
- **자동 로그아웃**: 401 에러 시 토큰 삭제 후 로그인 페이지로 리다이렉트

**API Service 예시** (`services/topicApi.ts`):

```typescript
export const topicApi = {
  generateTopic: async (data: TopicCreate): Promise<GenerateTopicResponse> => {
    const response = await api.post<ApiResponse<GenerateTopicResponse>>(
      API_ENDPOINTS.GENERATE_TOPIC,
      data
    );

    if (!response.data.success || !response.data.data) {
      throw new Error(
        response.data.error?.message || "보고서 생성에 실패했습니다."
      );
    }

    return response.data.data;
  },
};
```

### Vite 프록시 설정

개발 환경에서 CORS 문제를 피하기 위해 Vite 프록시를 사용합니다.

**`vite.config.ts`**:

```typescript
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

**효과**:

- 프론트엔드: `http://localhost:5173/api/auth/login`
- 실제 요청: `http://localhost:8000/api/auth/login`

---

## 상태 관리

### 1. AuthContext (전역)

**위치**: `src/context/AuthContext.tsx`

**관리 상태**:

- `user`: 현재 로그인한 사용자 정보
- `isAuthenticated`: 로그인 여부
- `isLoading`: 초기 로딩 상태

**제공 함수**:

- `login(data)`: 로그인
- `register(data)`: 회원가입
- `logout()`: 로그아웃
- `changePassword(data)`: 비밀번호 변경

**사용 방법**:

```typescript
import { useAuth } from "../hooks/useAuth";

const MyComponent = () => {
  const { user, isAuthenticated, login, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please login</div>;
  }

  return <div>Hello, {user.username}!</div>;
};
```

### 2. 컴포넌트 로컬 상태 (useState)

**MainChatPage 예시**:

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [selectedReport, setSelectedReport] = useState<ReportData | null>(null);
const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([]);
const [isGenerating, setIsGenerating] = useState(false);
const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
```

### 3. 로컬스토리지 (영속성)

**위치**: `src/utils/storage.ts`

```typescript
export const storage = {
  getToken: () => localStorage.getItem("access_token"),
  setToken: (token: string) => localStorage.setItem("access_token", token),
  getUser: () => JSON.parse(localStorage.getItem("user") || "null"),
  setUser: (user: User) => localStorage.setItem("user", JSON.stringify(user)),
  clear: () => localStorage.clear(),
};
```

---

## 스타일링

### CSS Modules 사용

모든 컴포넌트는 **CSS Modules**을 사용합니다.

**장점**:

- 클래스명 충돌 방지 (자동 해싱)
- 컴포넌트 단위 스코프
- TypeScript 자동 완성

**예시**:

```tsx
// ChatMessage.tsx
import styles from "./ChatMessage.module.css";

const ChatMessage = () => {
  return (
    <div className={styles.chatMessage}>
      <div className={styles.messageContent}>Hello</div>
    </div>
  );
};
```

```css
/* ChatMessage.module.css */
.chatMessage {
  padding: 1rem;
  border-radius: 0.5rem;
}

.messageContent {
  font-size: 0.875rem;
}
```

### CSS 변수 사용

**글로벌 변수** (`src/index.css`):

```css
:root {
  /* Colors */
  --color-primary: #1976d2;
  --color-bg: #f5f7fa;
  --color-text: #2c3e50;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Font sizes */
  --font-xs: 0.75rem;
  --font-sm: 0.875rem;
  --font-md: 1rem;
  --font-lg: 1.125rem;
  --font-xl: 1.25rem;
}
```

**사용**:

```css
.button {
  padding: var(--spacing-md);
  font-size: var(--font-md);
  background-color: var(--color-primary);
}
```

### Ant Design 커스터마이징

**ConfigProvider 사용** (`App.tsx`):

```typescript
import { ConfigProvider } from "antd";

<ConfigProvider
  theme={{
    token: {
      colorPrimary: "#1976D2",
      borderRadius: 8,
    },
  }}
>
  <App />
</ConfigProvider>;
```

---

## 주요 컴포넌트

### 1. MainChatPage

**역할**: 대화형 보고서 생성의 핵심 페이지

**주요 기능**:

- 채팅 인터페이스
- 메시지 입력/전송
- AI 응답 표시
- 보고서 미리보기
- 파일 다운로드

**상태**:

- `messages`: 대화 메시지 목록
- `selectedReport`: 선택된 보고서 (미리보기용)
- `selectedTopicId`: 현재 토픽 ID
- `isGenerating`: AI 응답 생성 중 여부

### 2. ChatMessage

**역할**: 메시지 버블 UI

**Props**:

```typescript
interface ChatMessageProps {
  message: Message;
  onReportClick: (reportData) => void;
  onDownload: (reportData) => void;
}
```

**특징**:

- `reportData`가 있으면: "보고서가 성공적으로 생성되었습니다!" 표시 + 보고서 카드
- `reportData`가 없으면: 일반 메시지 내용 표시

### 3. ChatInput

**역할**: 메시지 입력 UI

**Props**:

```typescript
interface ChatInputProps {
  onSend: (message: string, files: File[], webSearchEnabled: boolean) => void;
  disabled: boolean;
}
```

**기능**:

- 텍스트 입력
- 파일 첨부 (미사용)
- 웹 검색 토글 (미사용)
- Enter 전송 (Shift+Enter는 줄바꿈)

### 4. Sidebar

**역할**: 대화 목록 및 사용자 메뉴

**기능**:

- 토픽 목록 표시
- 새 대화 시작
- 사용자 프로필
- 로그아웃
- 관리자 페이지 링크

**상태**:

- `isOpen`: 사이드바 열림/닫힘
- `topics`: 토픽 목록

### 5. ReportPreview

**역할**: 보고서 미리보기 (우측 사이드바)

**Props**:

```typescript
interface ReportPreviewProps {
  report: {
    filename: string;
    content: string;
    reportId: number;
  };
  onClose: () => void;
  onDownload: () => void;
}
```

**표시 내용**:

- 파일명
- Markdown 내용 (줄바꿈 포함)
- 다운로드 버튼

### 6. AuthContext Provider

**역할**: 인증 상태 전역 관리

**제공 값**:

```typescript
{
  user: User | null,
  isAuthenticated: boolean,
  isLoading: boolean,
  login: (data) => Promise<void>,
  logout: () => Promise<void>,
  register: (data) => Promise<void>,
  changePassword: (data) => Promise<void>,
}
```

---

## 트러블슈팅

### 1. "Sidebar does not provide an export named 'default'"

**원인**: Vite HMR 캐시 문제

**해결**:

```bash
# 개발 서버 재시작
Ctrl+C
npm run dev

# 또는 캐시 삭제
rm -rf node_modules/.vite
npm run dev
```

### 2. 401 Unauthorized 에러

**원인**: JWT 토큰 만료 또는 없음

**해결**:

- 자동 로그인 페이지 리다이렉트 (`api.ts` 인터셉터)
- 수동: `localStorage.clear()` → 재로그인

### 3. CORS 에러

**원인**: 백엔드 서버와 통신 시 CORS 정책

**해결**:

- Vite 프록시 설정 확인 (`vite.config.ts`)
- 백엔드 CORS 설정 확인

### 4. 다운로드 버튼 클릭 시 501 에러

**원인**: `/api/artifacts/{artifact_id}/convert` 백엔드 미구현

**현재 상태**: Phase 6에서 구현 예정

**임시 해결**: MD 파일 직접 다운로드 기능 추가 고려

### 5. CSS가 적용되지 않음

**원인**: CSS Modules import 누락

**해결**:

```typescript
// ❌ 잘못된 방법
import "./ChatMessage.css";

// ✅ 올바른 방법
import styles from "./ChatMessage.module.css";
```

### 6. 타입 에러

**원인**: TypeScript 타입 불일치

**해결**:

```bash
# 타입 체크
npm run type-check

# 또는
tsc --noEmit
```

---

## 개발 가이드라인

### 1. 컴포넌트 작성 규칙

✅ **DO**:

- Functional Components 사용
- TypeScript 타입 명시
- CSS Modules 사용
- Props 인터페이스 정의
- 명확한 컴포넌트 이름

❌ **DON'T**:

- Class Components 사용
- Inline Styles 사용 (특수한 경우 제외)
- Any 타입 남발
- 200줄 이상의 거대한 컴포넌트

**예시**:

```typescript
// ✅ Good
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  disabled = false,
}) => {
  return (
    <button className={styles.button} onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
};

export default Button;
```

### 2. API 호출 규칙

✅ **DO**:

- 표준 API 응답 형식 사용
- 에러 처리 (try-catch)
- 로딩 상태 관리
- 사용자 피드백 (antd message)

❌ **DON'T**:

- 에러 무시
- 사용자에게 피드백 없음
- 네트워크 에러 미처리

**예시**:

```typescript
const handleSubmit = async () => {
  setLoading(true);
  try {
    const result = await topicApi.generateTopic({
      input_prompt,
      language: "ko",
    });
    message.success("보고서가 생성되었습니다.");
    setData(result);
  } catch (error: any) {
    console.error("Error:", error);
    message.error(error.message || "오류가 발생했습니다.");
  } finally {
    setLoading(false);
  }
};
```

### 3. 상태 관리 규칙

✅ **DO**:

- 최소한의 상태만 유지
- 상태 끌어올리기 (Lift State Up)
- 파생 상태는 계산으로 (useMemo)

❌ **DON'T**:

- 중복 상태
- Props를 State에 복사
- 불필요한 전역 상태

### 4. 스타일링 규칙

✅ **DO**:

- CSS Modules 사용
- CSS 변수 사용 (rem 단위)
- 의미 있는 클래스명
- 모바일 반응형 고려

❌ **DON'T**:

- px 단위 남발 (rem 권장)
- Magic Numbers
- Inline Styles

### 5. 타입 정의 규칙

✅ **DO**:

- 백엔드 API 응답과 일치
- 명확한 타입명
- types/ 폴더에 정의

❌ **DON'T**:

- any 타입 남발
- 타입 정의 누락

**예시**:

```typescript
// types/topic.ts
export interface Topic {
  id: number;
  user_id: number;
  input_prompt: string;
  generated_title: string | null;
  language: string;
  status: TopicStatus;
  created_at: string;
  updated_at: string;
}

export type TopicStatus = "active" | "archived" | "deleted";
```

### 6. Git Commit 규칙

**형식**:

```
<type>: <subject>

<body>
```

**Types**:

- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `style`: 스타일 변경
- `docs`: 문서 수정
- `test`: 테스트 추가

**예시**:

```
feat: implement logout API integration

- Add logout() to authApi.ts
- Update AuthContext.logout() to call API
- Make Sidebar.handleLogout() async
- Add error handling for API failures
```

---

## 참고 문서

- **프로젝트 가이드**: `CLAUDE.md`
- **프론트엔드 가이드**: `frontend/CLAUDE.md`
- **API 구현 현황**: `frontend/FRONTEND_API_STATUS.md`
- **백엔드 온보딩**: `BACKEND_ONBOARDING.md`

---

## 자주 묻는 질문 (FAQ)

### Q1. TanStack React Query는 왜 설치되어 있지만 사용하지 않나요?

**A**: 초기 설치했으나 현재는 Axios + useState 조합을 사용합니다. 향후 실시간 데이터 동기화가 필요하면 React Query 활용 예정입니다.

### Q2. 왜 Context API만 사용하고 Redux/Zustand를 안 쓰나요?

**A**: 현재는 전역 상태가 인증(Auth)만 필요하여 Context API로 충분합니다. 복잡해지면 Zustand 도입 고려 예정입니다.

### Q3. reportData가 있을 때만 간결한 메시지를 표시하는 이유는?

**A**: AI가 생성한 Markdown 전체 내용이 메시지에 포함되어 있어, 화면이 너무 길어지는 문제를 방지하기 위함입니다. 대신 보고서 카드를 클릭하면 미리보기로 볼 수 있습니다.

### Q4. 다운로드 버튼이 작동하지 않는 이유는?

**A**: 백엔드의 `/api/artifacts/{artifact_id}/convert` API가 아직 구현되지 않았습니다 (501 에러). Phase 6에서 구현 예정입니다.

### Q5. 개발 서버 포트를 변경하려면?

**A**: `vite.config.ts`에서 설정:

```typescript
export default defineConfig({
  server: {
    port: 3000, // 원하는 포트
  },
});
```

---

## 다음 단계

1. **`GET /api/auth/me` 구현**: 페이지 새로고침 시 사용자 정보 복구
2. **Artifact Convert 백엔드 구현**: HWPX 다운로드 기능 완성
3. **실시간 스트리밍 응답**: AI 응답을 실시간으로 표시
4. **메시지 삭제 기능**: DELETE 메시지 API 활용
5. **토큰 사용량 대시보드**: 관리자 페이지에 추가

---

**작성자**: Claude Code
**최종 업데이트**: 2025-10-30
**버전**: 2.0
