# Frontend Onboarding Guide

> HWP Report Generator 프론트엔드 온보딩 가이드
>
> 작성일: 2025-10-31
> 버전: v2.1 (Zustand 상태 관리 + 페이지네이션)

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
| **Zustand**              | 5.0.8    | 전역 상태 관리 (토픽)   |
| **Axios**                | 1.12.2   | HTTP 클라이언트         |
| **Context API**          | Built-in | 전역 상태 관리 (인증)   |
| **React Markdown**       | 10.1.0   | 마크다운 렌더링         |

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
│   │   └── react.svg
│   │
│   ├── components/              # 재사용 가능한 컴포넌트
│   │   ├── auth/                       # 인증 관련
│   │   │   ├── PrivateRoute.tsx        # 로그인 필요 라우트
│   │   │   └── PublicRoute.tsx         # 로그인 시 접근 불가 라우트
│   │   │
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
│   │   │   ├── MainLayout.module.css
│   │   │   ├── Header.tsx              # 헤더 컴포넌트
│   │   │   ├── Header.module.css
│   │   │   ├── Footer.tsx              # 푸터 컴포넌트
│   │   │   └── Footer.module.css
│   │   │
│   │   ├── report/
│   │   │   ├── ReportPreview.tsx       # 보고서 미리보기
│   │   │   ├── ReportPreview.module.css
│   │   │   ├── DownloadedFiles.tsx     # 다운로드 파일 목록
│   │   │   └── DownloadedFiles.module.css
│   │   │
│   │   ├── topic/                      # 토픽 관련
│   │   │   ├── TopicEditModal.tsx      # 토픽 수정 모달
│   │   │   ├── TopicEditModal.module.css
│   │   │   ├── TopicDeleteModal.tsx    # 토픽 삭제 모달
│   │   │   └── TopicDeleteModal.module.css
│   │   │
│   │   └── common/                     # 공통 컴포넌트
│   │
│   ├── context/                 # React Context
│   │   └── AuthContext.tsx             # 인증 상태 관리
│   │
│   ├── hooks/                   # Custom Hooks
│   │   ├── useAuth.ts                  # AuthContext 래퍼
│   │   ├── useReports.ts               # 보고서 관련 hook
│   │   └── useUsers.ts                 # 사용자 관련 hook
│   │
│   ├── pages/                   # 페이지 컴포넌트
│   │   ├── LoginPage.tsx               # 로그인 페이지
│   │   ├── RegisterPage.tsx            # 회원가입 페이지
│   │   ├── MainPage.tsx                # 메인 채팅 페이지 ⭐
│   │   ├── TopicListPage.tsx           # 모든 대화 목록 페이지 ⭐
│   │   ├── ChangePasswordPage.tsx      # 비밀번호 변경 페이지
│   │   ├── AdminPage.tsx               # 관리자 페이지
│   │   ├── MainBakPage.tsx             # 백업 페이지
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
│   ├── stores/                  # Zustand Store ⭐
│   │   └── useTopicStore.ts            # 토픽 상태 관리 (Zustand)
│   │
│   ├── styles/                  # 글로벌 스타일 ⭐
│   │   ├── global.css                  # 전역 스타일
│   │   ├── variables.css               # CSS 변수
│   │   └── common.css                  # 공통 스타일
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
│   │   ├── storage.ts                  # 로컬스토리지 래퍼
│   │   └── formatters.ts               # 포맷팅 유틸리티
│   │
│   ├── constants/               # 상수 정의
│   │   └── index.ts                    # API 엔드포인트, UI 설정, 스토리지 키 등
│   │
│   ├── App.tsx                  # 앱 루트 컴포넌트
│   ├── main.tsx                 # 엔트리 포인트
│   └── index.css                # 글로벌 스타일 (Deprecated)
│
├── package.json                 # 의존성 관리
├── tsconfig.json                # TypeScript 설정
├── vite.config.ts               # Vite 설정 (프록시 포함)
├── eslint.config.js             # ESLint 설정
└── CLAUDE.md                    # 프론트엔드 가이드
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

### 5. **라우팅 구조** ⭐

**App.tsx** 라우트 구성:

**공개 라우트** (PublicRoute - 로그인 안 한 사용자만):

- `/login` - 로그인 페이지
- `/register` - 회원가입 페이지

**보호된 라우트** (PrivateRoute - 로그인 필요):

- `/` - 메인 채팅 페이지 (MainPage)
- `/topics` - 모든 대화 목록 (TopicListPage)
- `/change-password` - 비밀번호 변경 페이지
- `/chat` - 레거시 경로 (`/`로 리다이렉트)

**관리자 전용 라우트** (PrivateRoute + requireAdmin):

- `/admin` - 관리자 페이지

**특수 처리**:

- `*` (404) - 존재하지 않는 경로는 `/`로 리다이렉트
- 로그인한 사용자가 `/login` 또는 `/register` 접근 시 `/`로 리다이렉트
- 미인증 사용자가 보호된 라우트 접근 시 `/login`으로 리다이렉트

**구현 예시**:

```typescript
<Routes>
  {/* 공개 라우트 */}
  <Route
    path="/login"
    element={
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    }
  />
  <Route
    path="/register"
    element={
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    }
  />

  {/* 보호된 라우트 */}
  <Route
    path="/"
    element={
      <PrivateRoute>
        <MainPage />
      </PrivateRoute>
    }
  />
  <Route
    path="/topics"
    element={
      <PrivateRoute>
        <TopicListPage />
      </PrivateRoute>
    }
  />
  <Route
    path="/change-password"
    element={
      <PrivateRoute>
        <ChangePasswordPage />
      </PrivateRoute>
    }
  />

  {/* 관리자 전용 */}
  <Route
    path="/admin"
    element={
      <PrivateRoute requireAdmin={true}>
        <AdminPage />
      </PrivateRoute>
    }
  />

  {/* 404 리다이렉트 */}
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>
```

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
6. navigate('/') → MainPage
```

### 2. 보고서 생성 플로우 (첫 번째 메시지)

```
1. MainPage: 사용자가 "디지털뱅킹 트렌드 보고서" 입력
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
5. Zustand: addTopic(newTopic)
   - Sidebar와 TopicListPage 모두에 새 토픽 추가
   ↓
6. messageApi.listMessages(topic_id)
   - 모든 메시지 불러오기
   ↓
7. artifactApi.listArtifactsByTopic(topic_id)
   - 아티팩트 목록 불러오기
   ↓
8. artifactApi.getArtifactContent(artifact_id)
   - MD 파일 내용 불러오기
   ↓
9. UI 업데이트
   - messages 상태 업데이트
   - 보고서 버튼 표시
   - setIsGenerating(false)
   - Sidebar에 새 토픽 표시
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

### 4. 토픽 목록 조회 플로우 ⭐

**Sidebar 로드:**

```
1. Sidebar 컴포넌트 마운트
   ↓
2. useEffect() → loadSidebarTopics()
   ↓
3. topicApi.listTopics("active", 1, SIDEBAR_TOPICS_PER_PAGE)
   ↓
4. Backend: GET /api/topics?status=active&page=1&limit=20
   ↓
5. Zustand: setSidebarTopics(topics)
   ↓
6. UI 업데이트 - Sidebar에 최근 토픽 표시
```

**TopicListPage 로드:**

```
1. TopicListPage 컴포넌트 마운트
   ↓
2. useEffect() → loadPageTopics(1, TOPICS_PER_PAGE)
   ↓
3. topicApi.listTopics("active", 1, TOPICS_PER_PAGE)
   ↓
4. Backend: GET /api/topics?status=active&page=1&limit=20
   ↓
5. Zustand: setPageTopics(topics), setPageTotalTopics(total), setPageCurrentPage(1)
   ↓
6. UI 업데이트 - 테이블에 토픽 목록 표시 + 페이지네이션
```

### 5. 로그아웃 플로우

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
const PUBLIC_ENDPOINTS = ["/api/auth/login", "/api/auth/register"];

const isPublicEndpoint = (url?: string): boolean => {
  if (!url) return false;
  return PUBLIC_ENDPOINTS.some((endpoint) => url.includes(endpoint));
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

### 1. AuthContext (전역 - 인증)

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

### 2. Zustand Store (전역 - 토픽) ⭐

**위치**: `src/stores/useTopicStore.ts`

**관리 상태**:

**Sidebar용 상태:**

- `sidebarTopics`: Sidebar에 표시할 토픽 목록 (첫 페이지만)
- `sidebarLoading`: Sidebar 로딩 상태

**TopicListPage용 상태:**

- `pageTopics`: TopicListPage의 토픽 목록 (페이지네이션)
- `pageLoading`: 페이지 로딩 상태
- `pageTotalTopics`: 전체 토픽 개수
- `pageCurrentPage`: 현재 페이지
- `pagePageSize`: 페이지당 토픽 개수

**공통 상태:**

- `selectedTopicId`: 현재 선택된 토픽 ID

**주요 함수**:

- `loadSidebarTopics()`: Sidebar용 토픽 로드 (첫 페이지만)
- `loadPageTopics(page, pageSize)`: TopicListPage용 토픽 로드 (페이지네이션)
- `addTopic(topic)`: 새 토픽 추가 (양쪽 리스트 반영)
- `updateTopicInBothLists(topicId, updates)`: 토픽 업데이트 (양쪽 리스트 반영)
- `removeTopicFromBothLists(topicId)`: 토픽 삭제 (양쪽 리스트 반영)
- `setSelectedTopicId(id)`: 선택된 토픽 변경
- `refreshTopic(topicId)`: 특정 토픽 새로고침
- `updateTopicById(topicId, data)`: 토픽 업데이트 (API 호출)
- `deleteTopicById(topicId)`: 토픽 삭제 (API 호출)

**사용 방법**:

```typescript
import { useTopicStore } from "../stores/useTopicStore";

const MyComponent = () => {
  const {
    sidebarTopics,
    selectedTopicId,
    setSelectedTopicId,
    loadSidebarTopics,
  } = useTopicStore();

  useEffect(() => {
    loadSidebarTopics();
  }, []);

  return (
    <div>
      {sidebarTopics.map((topic) => (
        <div key={topic.id} onClick={() => setSelectedTopicId(topic.id)}>
          {topic.generated_title || topic.input_prompt}
        </div>
      ))}
    </div>
  );
};
```

**특징**:

- Sidebar와 TopicListPage가 **독립적인 상태**를 가짐
- 토픽 생성/수정/삭제 시 **양쪽 리스트 동시 업데이트**
- Sidebar는 항상 첫 페이지만 표시
- TopicListPage는 서버 사이드 페이지네이션 지원

### 3. 컴포넌트 로컬 상태 (useState)

**MainPage 예시**:

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [selectedReport, setSelectedReport] = useState<ReportData | null>(null);
const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([]);
const [isGenerating, setIsGenerating] = useState(false);
const [currentTopicId, setCurrentTopicId] = useState<number | null>(null);
```

### 4. 로컬스토리지 (영속성)

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

### 5. 상수 (Constants) ⭐

**위치**: `src/constants/index.ts`

**주요 상수**:

**API_ENDPOINTS**: API 엔드포인트 URL 모음

```typescript
export const API_ENDPOINTS = {
  // 인증 API
  LOGIN: "/api/auth/login",
  REGISTER: "/api/auth/register",
  LOGOUT: "/api/auth/logout",
  CHANGE_PASSWORD: "/api/auth/change-password",

  // 토픽 API
  CREATE_TOPIC: "/api/topics",
  GENERATE_TOPIC: "/api/topics/generate",
  LIST_TOPICS: "/api/topics",
  GET_TOPIC: (topicId: number) => `/api/topics/${topicId}`,
  UPDATE_TOPIC: (topicId: number) => `/api/topics/${topicId}`,
  DELETE_TOPIC: (topicId: number) => `/api/topics/${topicId}`,
  ASK_TOPIC: (topicId: number) => `/api/topics/${topicId}/ask`,

  // 메시지 API
  LIST_MESSAGES: (topicId: number) => `/api/topics/${topicId}/messages`,
  CREATE_MESSAGE: (topicId: number) => `/api/topics/${topicId}/messages`,

  // 아티팩트 API
  GET_ARTIFACT: (artifactId: number) => `/api/artifacts/${artifactId}`,
  GET_ARTIFACT_CONTENT: (artifactId: number) =>
    `/api/artifacts/${artifactId}/content`,
  DOWNLOAD_ARTIFACT: (artifactId: number) =>
    `/api/artifacts/${artifactId}/download`,
  DOWNLOAD_MESSAGE_HWPX: (messageId: number, locale: string = "ko") =>
    `/api/artifacts/messages/${messageId}/hwpx/download?locale=${locale}`,
  // ... 기타 엔드포인트
} as const;
```

**STORAGE_KEYS**: 로컬스토리지 키 이름

```typescript
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "access_token",
  USER: "user",
} as const;
```

**UI_CONFIG**: UI 설정 상수

```typescript
export const UI_CONFIG = {
  PAGINATION: {
    // TopicListPage에서 한 페이지당 표시할 토픽 개수
    TOPICS_PER_PAGE: 20,
    // Sidebar에 표시할 최대 토픽 개수
    SIDEBAR_TOPICS_PER_PAGE: 20,
  },
} as const;
```

**사용 방법**:

```typescript
import { API_ENDPOINTS, UI_CONFIG } from "../constants";

// API 호출
const response = await api.get(API_ENDPOINTS.LIST_TOPICS);

// 동적 엔드포인트
const topicUrl = API_ENDPOINTS.GET_TOPIC(123);

// UI 설정 사용
const pageSize = UI_CONFIG.PAGINATION.TOPICS_PER_PAGE;
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

### 1. MainPage (메인 채팅 페이지) ⭐

**위치**: `src/pages/MainPage.tsx`

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
- `currentTopicId`: 현재 토픽 ID (Zustand에서 가져옴)
- `isGenerating`: AI 응답 생성 중 여부

### 2. TopicListPage (모든 대화 페이지) ⭐

**위치**: `src/pages/TopicListPage.tsx`

**역할**: 모든 대화 목록을 테이블 형식으로 표시하는 페이지

**주요 기능**:

- 토픽 목록 테이블 표시 (ID, 주제, 생성일, 액션)
- 서버 사이드 페이지네이션 (기본 20개/페이지)
- 토픽 검색 및 필터링
- 토픽 수정/삭제
- 토픽 클릭 시 MainPage로 이동

**상태** (Zustand에서 관리):

- `pageTopics`: 현재 페이지의 토픽 목록
- `pageLoading`: 로딩 상태
- `pageTotalTopics`: 전체 토픽 개수
- `pageCurrentPage`: 현재 페이지 번호
- `pagePageSize`: 페이지당 토픽 개수

**주요 함수**:

- `handleTopicSelect(topicId)`: 토픽 선택 후 MainPage로 이동
- `handleEdit(topic)`: 토픽 수정 모달 열기
- `handleDelete(topic)`: 토픽 삭제 모달 열기
- `handleGoToPage(page)`: 특정 페이지로 이동
- `handlePrevGroup()`: 이전 10페이지 그룹으로 이동
- `handleNextGroup()`: 다음 10페이지 그룹으로 이동

**페이지네이션 특징**:

- 한 번에 최대 10개의 페이지 번호 표시 (1-10, 11-20, ...)
- "< >" 버튼으로 페이지 그룹 이동
- 서버에서 필터링된 데이터만 가져옴 (성능 최적화)

### 3. Sidebar (좌측 사이드바)

**위치**: `src/components/layout/Sidebar.tsx`

**역할**: 최근 대화 목록 및 사용자 메뉴 표시

**주요 기능**:

- 최근 토픽 목록 표시 (기본 20개)
- 새 대화 시작 버튼
- "모든 대화" 버튼 (TopicListPage로 이동)
- 사용자 프로필 메뉴
- 설정 (비밀번호 변경)
- 로그아웃
- 관리자 페이지 링크 (관리자만)

**상태** (Zustand에서 관리):

- `sidebarTopics`: 최근 토픽 목록 (첫 페이지만)
- `sidebarLoading`: 로딩 상태
- `selectedTopicId`: 선택된 토픽 ID

**특징**:

- Collapsed/Expanded 두 가지 상태
- 모바일에서는 Overlay와 함께 표시
- 토픽 클릭 시 MainPage에서 해당 토픽의 대화 로드

### 4. ChatMessage

**위치**: `src/components/chat/ChatMessage.tsx`

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
- `reportData`가 없으면: 일반 메시지 내용 표시 (Markdown 지원)
- 사용자 메시지와 AI 메시지 구분 표시

### 5. ChatInput

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

### 6. TopicEditModal / TopicDeleteModal ⭐

**위치**: `src/components/topic/`

**역할**: 토픽 수정 및 삭제 모달

**TopicEditModal Props**:

```typescript
interface TopicEditModalProps {
  topic: Topic | null;
  isOpen: boolean;
  onClose: () => void;
}
```

**TopicDeleteModal Props**:

```typescript
interface TopicDeleteModalProps {
  topic: Topic | null;
  isOpen: boolean;
  onClose: () => void;
}
```

**특징**:

- Zustand의 `updateTopicById`, `deleteTopicById` 사용
- 수정/삭제 후 양쪽 리스트 (Sidebar, TopicListPage) 자동 업데이트
- 성공/실패 메시지 표시

### 7. PrivateRoute / PublicRoute ⭐

**위치**: `src/components/auth/`

**역할**: 라우트 보호 컴포넌트

**PrivateRoute**:

- 로그인한 사용자만 접근 가능
- `requireAdmin` prop으로 관리자 전용 라우트 설정 가능
- 미인증 시 `/login`으로 리다이렉트

**PublicRoute**:

- 로그인하지 않은 사용자만 접근 가능
- 인증된 사용자는 `/`로 리다이렉트
- 로그인/회원가입 페이지에 사용

**사용 예시**:

```typescript
// 일반 사용자용 보호 라우트
<Route
  path="/"
  element={
    <PrivateRoute>
      <MainPage />
    </PrivateRoute>
  }
/>

// 관리자 전용 라우트
<Route
  path="/admin"
  element={
    <PrivateRoute requireAdmin={true}>
      <AdminPage />
    </PrivateRoute>
  }
/>

// 공개 라우트 (로그인 안 한 사람만)
<Route
  path="/login"
  element={
    <PublicRoute>
      <LoginPage />
    </PublicRoute>
  }
/>
```

### 8. ReportPreview

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
- 상태 끌어올리기 (Lift State Up) 또는 Zustand 사용
- 파생 상태는 계산으로 (useMemo)
- **토픽 관련 상태는 Zustand 사용** (useTopicStore)
- **인증 관련 상태는 Context API 사용** (AuthContext)
- Zustand 액션을 통해 상태 업데이트 (직접 set 호출 지양)

❌ **DON'T**:

- 중복 상태
- Props를 State에 복사
- 불필요한 전역 상태
- Zustand 상태를 직접 수정 (immutable 유지)
- 여러 store에 같은 데이터 중복 저장

**Zustand 사용 예시**:

```typescript
// ✅ Good - Zustand 액션 사용
const { updateTopicById, deleteTopicById } = useTopicStore();

const handleUpdate = async () => {
  await updateTopicById(topicId, { generated_title: "새 제목" });
};

// ❌ Bad - 직접 상태 수정 시도
const { sidebarTopics } = useTopicStore();
sidebarTopics[0].generated_title = "새 제목"; // 작동하지 않음!
```

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
- **백엔드 온보딩**: `BACKEND_ONBOARDING.md`

---

## 자주 묻는 질문 (FAQ)

### Q1. Context API와 Zustand를 같이 사용하는 이유는?

**A**:

- **Context API**: 인증(Auth) 전용 - 앱 전체에서 사용자 정보 필요
- **Zustand**: 토픽 관리 전용 - 복잡한 상태 업데이트와 여러 컴포넌트 간 공유 필요
- 각 상태의 특성에 맞게 도구를 선택하여 사용합니다.

### Q2. Sidebar와 TopicListPage가 별도의 상태를 가지는 이유는?

**A**:

- **Sidebar**: 최근 토픽만 표시 (첫 페이지, 고정 개수)
- **TopicListPage**: 모든 토픽 표시 (페이지네이션)
- 각각의 목적이 다르므로 독립적인 상태로 관리하되, 토픽 생성/수정/삭제 시에는 **양쪽 모두 업데이트**하여 동기화합니다.

### Q3. reportData가 있을 때만 간결한 메시지를 표시하는 이유는?

**A**: AI가 생성한 Markdown 전체 내용이 메시지에 포함되어 있어, 화면이 너무 길어지는 문제를 방지하기 위함입니다. 대신 보고서 카드를 클릭하면 미리보기로 볼 수 있습니다.

### Q4. 개발 서버 포트를 변경하려면?

**A**: `vite.config.ts`에서 설정:

```typescript
export default defineConfig({
  server: {
    port: 3000, // 원하는 포트
  },
});
```

### Q5. 페이지네이션이 두 곳에서 다르게 작동하는 이유는?

**A**:

- **Sidebar**: 클라이언트 사이드 - 첫 페이지만 로드, "모든 대화" 버튼으로 전체 목록 이동
- **TopicListPage**: 서버 사이드 - 실제 데이터베이스에서 페이지별로 조회 (성능 최적화)

### Q6. MainBakPage는 무엇인가요?

**A**: 백업 또는 이전 버전의 메인 페이지입니다. 현재는 `MainPage`가 실제로 사용되는 메인 채팅 페이지이며, `MainBakPage`는 참고용으로 남겨둔 것입니다.

---

## 다음 단계

1. ✅ **Zustand 상태 관리 도입**: 토픽 관리 완료
2. ✅ **TopicListPage 구현**: 모든 대화 목록 페이지 완료
3. ✅ **토픽 수정/삭제 기능**: 모달 컴포넌트 완료
4. ✅ **라우트 보호**: PrivateRoute/PublicRoute 완료
5. ✅ **서버 사이드 페이지네이션**: TopicListPage 완료
6. **내 정보 조회 기능**: /api/users/me (예정)
7. **메시지 삭제 기능**: DELETE 메시지 API 활용 (예정)
8. **토큰 사용량 대시보드**: 관리자 페이지에 추가 (예정)

---

**작성자**: Claude Code
**최종 업데이트**: 2025-10-31
**버전**: 2.1
