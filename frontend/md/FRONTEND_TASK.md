# Frontend Development Plan

> HWP Report Generator 프론트엔드 개발 진행 상황 및 남은 태스크
>
> 작성일: 2025-11-05
> 기준 문서: FRONTEND_ONBOARDING.md v2.1

---

## 📊 전체 진행률

**전체 완료율: 81%**

| 카테고리    | 완료  | 진행중 | 대기 | 완료율 |
| ----------- | ----- | ------ | ---- | ------ |
| 핵심 기능   | 9/12  | 0/12   | 3/12 | 75%    |
| UI/UX       | 7/11  | 0/11   | 4/11 | 63%    |
| 상태 관리   | 4/4   | 0/4    | 0/4  | 100%   |
| API 통합    | 10/13 | 0/13   | 3/13 | 76%    |
| 관리자 기능 | 3/6   | 1/6    | 2/6  | 50%    |
| 문서화      | 4/4   | 0/4    | 0/4  | 100%   |

---

## ✅ 완료된 기능 (Completed)

### 1. 핵심 기능

- [x] **대화형 시스템 구현** (v2.0)
    - Topic/Message/Artifact 구조
    - 실시간 AI 대화
    - 메시지 히스토리 관리

- [x] **보고서 생성 플로우**
    - 첫 메시지: 토픽 생성 + 보고서 자동 생성
    - 후속 메시지: 기존 보고서 기반 수정
    - MD 파일 생성 및 관리

- [x] **보고서 미리보기**
    - Markdown 렌더링
    - 줄바꿈 처리
    - 우측 사이드바 미리보기

- [x] **HWPX 다운로드**
    - MD → HWPX 변환 API 연동
    - 브라우저 다운로드 트리거
    - 파일명 자동 처리

- [x] **토픽 목록 관리**
    - TopicListPage 구현
    - 서버 사이드 페이지네이션
    - 토픽 검색 및 필터링

- [x] **토픽 수정/삭제**
    - TopicEditModal 구현
    - TopicDeleteModal 구현
    - 양쪽 리스트 동기화 (Sidebar + TopicListPage)

- [x] **인증 시스템**
    - JWT 토큰 기반 인증
    - 로그인/로그아웃
    - 회원가입 (관리자 승인 대기)
    - 비밀번호 변경

- [x] **라우트 보호**
    - PrivateRoute 컴포넌트
    - PublicRoute 컴포넌트
    - 관리자 전용 라우트

### 2. 상태 관리

- [x] **Zustand Store 도입**
    - useTopicStore 구현
    - Sidebar/TopicListPage 독립 상태
    - 토픽 CRUD 액션

- [x] **Artifact Store 구현** ⭐ (NEW)
    - useArtifactStore (토픽별 아티팩트 캐싱)
    - MD 파일 목록 관리
    - 자동 선택/수동 선택 로직
    - 캐시 갱신 메커니즘

- [x] **AuthContext 구현**
    - 사용자 인증 상태
    - 로그인/로그아웃 함수
    - localStorage 연동

- [x] **메시지 상태 관리**
    - useMessages Hook
    - 메시지 로딩 상태
    - Artifact 통합 렌더링

### 3. UI/UX

- [x] **반응형 레이아웃**
    - MainLayout 컴포넌트
    - Sidebar 토글 (모바일/데스크톱)
    - Dim Overlay

- [x] **채팅 UI**
    - ChatInput (Enter 전송, Shift+Enter 줄바꿈)
    - ChatMessage (사용자/AI 구분)
    - ChatWelcome (초기 화면)
    - GeneratingIndicator (로딩 애니메이션)

- [x] **보고서 선택 드롭다운** ⭐ (NEW)
    - ReportsDropdown 컴포넌트
    - MD 파일 목록 표시
    - Radio 버튼 선택
    - 미리보기/다운로드 버튼

- [x] **설정 드롭다운** ⭐ (NEW)
    - SettingsDropdown 컴포넌트
    - 채팅 설정 (모델, Temperature 등)

- [x] **토픽 카드 UI**
    - 토픽 목록 테이블
    - 수정/삭제 모달
    - 페이지네이션 컨트롤

- [x] **관리자 사이드바**
    - AdminSidebar 컴포넌트
    - 메뉴 전환 (사용자, 프롬프트, 보고서, 설정)

- [x] **프롬프트 관리 UI**
    - PromptManagement 컴포넌트
    - TextArea 입력 폼
    - 저장/초기화 버튼

- [x] **사용자 설정 모달** ⭐ (NEW)
    - SettingsModal 컴포넌트
    - 일반 설정 탭 (다크모드 UI)
    - 사용자 정보 탭 (이메일, 사용자명, 가입일)
    - Sidebar 드롭다운 메뉴 통합

### 4. API 통합

- [x] **인증 API**
    - authApi: login, register, logout, changePassword, getMyInfo ⭐

- [x] **토픽 API**
    - topicApi: generateTopic, listTopics, getTopic, updateTopic, deleteTopic, askTopic

- [x] **메시지 API**
    - messageApi: listMessages, createMessage

- [x] **아티팩트 API** ⭐ (NEW)
    - artifactApi: getArtifact, getArtifactContent, downloadArtifact
    - artifactApi: listArtifactsByTopic, convertToHwpx, downloadMessageHwpx

- [x] **관리자 API**
    - adminApi: getAllUsers, approveUser, rejectUser, resetPassword

- [x] **표준 API 응답 처리**
    - ApiResponse<T> 타입
    - 성공/실패 처리
    - 에러 메시지 표시

- [x] **Axios 인터셉터**
    - JWT 토큰 자동 추가
    - 401 에러 자동 로그아웃
    - Public 엔드포인트 필터링

- [x] **Vite 프록시 설정**
    - /api → http://localhost:8000
    - CORS 문제 해결

- [x] **파일 다운로드 처리**
    - Blob 생성
    - Content-Disposition 파싱
    - 브라우저 다운로드 트리거

### 5. 문서화

- [x] **FRONTEND_ONBOARDING.md** (v2.1)
    - 프로젝트 구조 설명
    - 핵심 개념 정리
    - API 통신 가이드
    - 개발 가이드라인

- [x] **USER_FLOW.md** ⭐ (NEW)
    - Mermaid Sequence Diagram
    - 단계별 사용 플로우
    - API 요청/응답 예시
    - 상태 관리 설명

- [x] **CLAUDE.md** (프로젝트 가이드)
    - API 응답 표준
    - 에러 코드 규칙
    - 마이그레이션 가이드

- [x] **USER_SETTINGS.md** ⭐ (NEW)
    - 사용자 설정 기능 문서
    - 컴포넌트 구조 및 API 연동
    - 구현 히스토리

---

## 🚧 진행 중 (In Progress)

### 1. 관리자 기능

- [ ] **프롬프트 관리 API 연동** (50%)
    - 현재: 로컬 기본값만 사용
    - 필요: GET /api/prompts, PUT /api/prompts API 연동
    - 파일: `components/admin/PromptManagement.tsx`
    - 우선순위: Medium

### 2. 아티팩트 기능

- [ ] **아티팩트 캐시 최적화** (30%)
    - 현재: 메시지 전송 후 refreshArtifacts 호출
    - 개선: WebSocket 또는 Polling으로 실시간 갱신
    - 파일: `hooks/useChatActions.ts`
    - 우선순위: Low

---

## 📋 남은 태스크 (TODO)

### High Priority (긴급)

#### 1. 메시지 삭제 기능

- **설명**: 사용자가 특정 메시지를 삭제할 수 있는 기능
- **작업 내용**:
    - [ ] DELETE /api/messages/{messageId} API 추가 (`messageApi.ts`)
    - [ ] ChatMessage 컴포넌트에 삭제 버튼 추가
    - [ ] 메시지 삭제 확인 모달
    - [ ] 메시지 삭제 후 목록 새로고침
- **예상 시간**: 2-3시간
- **의존성**: 백엔드 DELETE 메시지 API 구현 필요

### Medium Priority (중요)

#### 2. 토큰 사용량 대시보드

- **설명**: 관리자가 사용자별 토큰 사용량을 확인
- **작업 내용**:
    - [ ] GET /api/admin/token-usage API 연동
    - [ ] 토큰 사용량 차트 컴포넌트 (Recharts 또는 Ant Design Charts)
    - [ ] 사용자별 사용량 테이블
    - [ ] 날짜별 필터링
    - [ ] AdminPage에 "대시보드" 탭 구현
- **예상 시간**: 5-6시간
- **의존성**: 백엔드 토큰 사용량 API 구현 필요
- **라이브러리**: recharts 또는 @ant-design/charts

#### 3. 프롬프트 관리 API 연동

- **설명**: 프롬프트 설정을 서버에 저장/불러오기
- **작업 내용**:
    - [ ] GET /api/prompts API 연동
    - [ ] PUT /api/prompts API 연동
    - [ ] PromptManagement.tsx 수정
    - [ ] 로딩 상태 처리
    - [ ] 에러 핸들링
- **예상 시간**: 2-3시간
- **파일**: `components/admin/PromptManagement.tsx`, `services/promptApi.ts`

#### 4. 보고서 템플릿 관리

- **설명**: 관리자가 HWPX 템플릿 업로드/관리
- **작업 내용**:
    - [ ] GET /api/templates API 연동
    - [ ] POST /api/templates (파일 업로드)
    - [ ] DELETE /api/templates/{id}
    - [ ] 템플릿 목록 UI
    - [ ] 파일 업로드 UI (Ant Design Upload)
    - [ ] AdminPage에 "템플릿" 탭 추가
- **예상 시간**: 4-5시간
- **의존성**: 백엔드 템플릿 관리 API 구현 필요

### Low Priority (개선)

#### 5. 다크 모드 지원

- **설명**: 라이트/다크 테마 토글
- **작업 내용**:
    - [ ] CSS 변수로 테마 정의
    - [ ] 테마 전환 버튼 추가 (Header 또는 Sidebar)
    - [ ] localStorage에 테마 설정 저장
    - [ ] Ant Design ConfigProvider 테마 동기화
- **예상 시간**: 3-4시간
- **파일**: `styles/variables.css`, `App.tsx`, `components/layout/Header.tsx`

#### 6. 웹 검색 기능 (ChatInput)

- **설명**: AI 응답 시 웹 검색 결과 포함
- **작업 내용**:
    - [ ] ChatInput의 웹 검색 토글 활성화
    - [ ] topicApi.askTopic에 web_search 파라미터 추가
    - [ ] 백엔드 API 수정 대응
- **예상 시간**: 2시간
- **의존성**: 백엔드 웹 검색 기능 구현 필요
- **현재 상태**: UI는 있지만 비활성화됨

#### 7. 파일 첨부 기능 (ChatInput)

- **설명**: 메시지에 파일 첨부
- **작업 내용**:
    - [ ] ChatInput의 파일 첨부 버튼 활성화
    - [ ] multipart/form-data 업로드
    - [ ] 백엔드 API 수정 대응
    - [ ] 첨부 파일 미리보기
- **예상 시간**: 4-5시간
- **의존성**: 백엔드 파일 업로드 기능 구현 필요
- **현재 상태**: UI는 있지만 비활성화됨

#### 8. 보고서 검색 기능

- **설명**: TopicListPage에서 토픽 제목/내용 검색
- **작업 내용**:
    - [ ] 검색 입력창 추가
    - [ ] GET /api/topics?search={query} API 연동
    - [ ] 검색 결과 하이라이팅
    - [ ] 검색 히스토리 저장 (localStorage)
- **예상 시간**: 3-4시간

#### 9. 무한 스크롤 (TopicListPage)

- **설명**: 페이지네이션 대신 무한 스크롤
- **작업 내용**:
    - [ ] Intersection Observer 구현
    - [ ] 스크롤 시 자동 로드
    - [ ] react-intersection-observer 라이브러리 사용
- **예상 시간**: 2-3시간
- **현재**: 페이지네이션 사용 중

---

## 🐛 알려진 버그 & 개선 사항

### Bugs

1. **[FIXED] 프롬프트 관리 중복 메시지** ⭐
    - 상태: 해결됨 (2025-11-05)
    - 원인: React Strict Mode + useEffect 이중 실행
    - 해결: 초기 로드 메시지 제거 + message.key 사용

2. **[FIXED] 아티팩트 목록 갱신 안 됨** ⭐
    - 상태: 해결됨 (2025-11-05)
    - 원인: 메시지 전송 후 artifact 캐시 갱신 누락
    - 해결: useChatActions에 refreshArtifacts 추가

### Improvements

1. **성능 최적화**
    - [ ] React.memo로 불필요한 리렌더링 방지
    - [ ] useMemo, useCallback 적용
    - [ ] 코드 스플리팅 (React.lazy)

2. **에러 핸들링 개선**
    - [ ] 전역 에러 바운더리
    - [ ] 네트워크 에러 재시도 로직
    - [ ] 상세한 에러 메시지

3. **UX 개선**
    - [ ] 로딩 스켈레톤 UI
    - [ ] 애니메이션 추가 (Framer Motion)
    - [ ] Toast 알림 개선

4. **접근성 (a11y)**
    - [ ] ARIA 속성 추가
    - [ ] 키보드 네비게이션
    - [ ] 스크린 리더 대응

---

## 📦 필요한 라이브러리

### 추가 설치 필요

```bash
# 차트 (토큰 사용량 대시보드)
npm install recharts
# 또는
npm install @ant-design/charts

# 무한 스크롤
npm install react-intersection-observer

# 애니메이션 (선택)
npm install framer-motion
```

---

## 🔄 의존성 (Backend API 필요)

다음 기능은 백엔드 API 구현이 선행되어야 합니다:

| 프론트엔드 기능      | 필요한 백엔드 API                               | 우선순위 |
| -------------------- | ----------------------------------------------- | -------- |
| 메시지 삭제          | DELETE /api/messages/{id}                       | High     |
| 토큰 사용량 대시보드 | GET /api/admin/token-usage                      | Medium   |
| 프롬프트 관리        | GET/PUT /api/prompts                            | Medium   |
| 보고서 템플릿 관리   | GET/POST/DELETE /api/templates                  | Medium   |
| 웹 검색              | POST /api/topics/{id}/ask (web_search 파라미터) | Low      |
| 파일 첨부            | POST /api/messages (multipart/form-data)        | Low      |

---

## 🎯 다음 스프린트 목표 (권장)

### Sprint 1 (1주일)

1. **메시지 삭제 기능** (High)
2. **프롬프트 관리 API 연동** (Medium)
3. **다크모드 실제 기능 구현** (Low)

**예상 완료 후 진행률**: 81% → 87%

### Sprint 2 (1주일)

1. **토큰 사용량 대시보드** (Medium)
2. **보고서 템플릿 관리** (Medium)
3. **성능 최적화** (React.memo, useMemo)

**예상 완료 후 진행률**: 87% → 94%

### Sprint 3 (1주일)

1. **키보드 단축키** (Low)
2. **UX 개선** (로딩 스켈레톤, 애니메이션)
3. **성능 최적화** (React.memo, useMemo)

**예상 완료 후 진행률**: 94% → 98%

---

## 📈 진행 상황 상세

### 핵심 기능 (9/12 완료 - 75%)

| 기능                       | 상태 | 완료일     |
| -------------------------- | ---- | ---------- |
| 대화형 시스템              | ✅   | 2025-10-30 |
| 보고서 생성                | ✅   | 2025-10-30 |
| 보고서 미리보기            | ✅   | 2025-10-30 |
| HWPX 다운로드              | ✅   | 2025-10-31 |
| 토픽 목록 관리             | ✅   | 2025-10-31 |
| 토픽 수정/삭제             | ✅   | 2025-10-31 |
| 인증 시스템                | ✅   | 2025-10-30 |
| 라우트 보호                | ✅   | 2025-10-31 |
| 내 정보 조회               | ✅   | 2025-11-05 |
| 대화형 시스템(스트림) 개선 | ⏳   | -          |
| 비밀번호 암호화            | ⏳   | -          |
| 메시지 삭제                | ⏳   | -          |

### UI/UX (7/11 완료 - 63%)

| 기능                  | 상태 | 완료일     |
| --------------------- | ---- | ---------- |
| 반응형 레이아웃       | ✅   | 2025-10-30 |
| 채팅 UI               | ✅   | 2025-10-30 |
| 보고서 드롭다운       | ✅   | 2025-11-04 |
| 설정 드롭다운         | ✅   | 2025-11-04 |
| 토픽 카드 UI          | ✅   | 2025-10-31 |
| 프롬프트 관리 UI      | ✅   | 2025-11-01 |
| 사용자 설정 모달      | ✅   | 2025-01-05 |
| 채팅 UI(스트림)       | ⏳   | -          |
| 관리자 사이드바       | ⏳   | -          |
| 토큰 사용량 조회 UI   | ⏳   | -          |
| 메시지 삭제 확인 모달 | ⏳   | -          |

### 상태 관리 (4/4 완료 - 100%)

| 기능             | 상태 | 완료일     |
| ---------------- | ---- | ---------- |
| Topic Store      | ✅   | 2025-10-31 |
| Artifact Store   | ✅   | 2025-11-04 |
| AuthContext      | ✅   | 2025-10-30 |
| 메시지 상태 관리 | ✅   | 2025-11-04 |

### API 통합 (10/13 완료 - 76%)

| 기능                  | 상태 | 완료일     |
| --------------------- | ---- | ---------- |
| 인증 API              | ✅   | 2025-10-30 |
| 인증 API (내 정보)    | ✅   | 2025-01-05 |
| 토픽 API              | ✅   | 2025-10-30 |
| 메시지 API            | ✅   | 2025-10-30 |
| 아티팩트 API          | ✅   | 2025-11-04 |
| 관리자 API (사용자)   | ✅   | 2025-11-01 |
| 표준 응답 처리        | ✅   | 2025-10-30 |
| Axios 인터셉터        | ✅   | 2025-10-30 |
| Vite 프록시           | ✅   | 2025-10-30 |
| 파일 다운로드         | ✅   | 2025-10-31 |
| 대화형 시스템(스트림) | ⏳   | -          |
| 프롬프트 API          | ⏳   | -          |
| 토큰 사용량 API       | ⏳   | -          |

### 관리자 기능 (3/6 완료 - 50%)

| 기능                 | 상태 | 완료일     |
| -------------------- | ---- | ---------- |
| 사용자 관리 UI       | ✅   | 2025-11-01 |
| 사용자 승인/거부     | ✅   | 2025-11-01 |
| 비밀번호 초기화      | ✅   | 2025-11-01 |
| 프롬프트 관리 UI     | 🚧   | -          |
| 토큰 사용량 대시보드 | ⏳   | -          |
| 템플릿 관리          | ⏳   | -          |

### 문서화 (4/4 완료 - 100%)

| 문서                   | 상태 | 완료일     |
| ---------------------- | ---- | ---------- |
| FRONTEND_ONBOARDING.md | ✅   | 2025-10-31 |
| USER_FLOW.md           | ✅   | 2025-11-05 |
| USER_SETTINGS.md       | ✅   | 2025-01-05 |
| CLAUDE.md              | ✅   | 2025-10-30 |

---

## 📝 변경 이력

### 2025-11-05

- ✅ **사용자 설정 모달 구현** (SettingsModal)
    - 일반 설정 탭 (다크모드 UI)
    - 사용자 정보 탭 (이메일, 사용자명, 가입일)
- ✅ **내 정보 조회 API 연동** (authApi.getMyInfo)
- ✅ **Sidebar 드롭다운 메뉴 개선**
    - 사용자 버튼 → 드롭다운 (이메일, 관리자 페이지, 설정, 로그아웃)
- ✅ **USER_SETTINGS.md 문서 작성**
- 📊 **전체 완료율**: 78% → 81%

### 2025-11-04

- ✅ Artifact Store 구현 (useArtifactStore)
- ✅ ReportsDropdown 컴포넌트 추가
- ✅ SettingsDropdown 컴포넌트 추가
- ✅ 메시지 전송 후 artifact 캐시 갱신 로직 추가
- ✅ USER_FLOW.md 문서 작성
- 🐛 프롬프트 관리 중복 메시지 버그 수정
- 🐛 아티팩트 목록 갱신 안 되는 버그 수정

### 2025-10-31

- ✅ Zustand Store 도입
- ✅ TopicListPage 구현
- ✅ 서버 사이드 페이지네이션
- ✅ 토픽 수정/삭제 모달
- ✅ FRONTEND_ONBOARDING.md v2.1 작성

### 2025-10-30

- ✅ 대화형 시스템 기본 구현
- ✅ 인증 시스템 구현
- ✅ 기본 UI 컴포넌트 구현

---

## 🎓 학습 리소스

### 프로젝트 문서

- `FRONTEND_ONBOARDING.md` - 프론트엔드 온보딩 가이드
- `USER_FLOW.md` - 사용자 플로우 및 API 문서
- `CLAUDE.md` - 프로젝트 전체 가이드

---

**작성자**: Claude Code
**최종 업데이트**: 2025-11-05
**다음 리뷰 일정**: 2025-11-12
