# Jira & Confluence MCP 연동 가이드

Atlassian MCP 서버 연결을 통한 Jira 및 Confluence 작업 가이드

---

## 🎯 Jira 기능

### 1. **이슈 조회 및 검색**

#### 특정 이슈 상세 정보 조회
```
getJiraIssue
- 이슈 ID 또는 키(예: ISSUE-123)로 이슈 상세 정보 조회
- 반환 정보: 제목, 설명, 상태, 담당자, 우선순위 등
```

#### JQL로 이슈 검색
```
searchJiraIssuesUsingJql
- JQL(Jira Query Language)을 사용한 고급 검색
- 예시 쿼리:
  - "assignee = currentUser() AND status = 'In Progress'"
  - "project = MYPROJECT AND priority = High"
  - "created >= -7d AND type = Bug"
```

#### Rovo Search (통합 검색)
```
search
- Jira와 Confluence를 동시에 검색
- 자연어 검색 지원
```

---

### 2. **이슈 생성 및 수정**

#### 새 이슈 생성
```
createJiraIssue
- 파라미터:
  - cloudId: Atlassian 클라우드 인스턴스 ID
  - projectKey: 프로젝트 키 (예: "HWPRPT")
  - issueTypeName: 이슈 타입 (Story, Task, Bug, Epic 등)
  - summary: 이슈 제목
  - description: 이슈 설명 (Markdown 지원)
  - assignee_account_id: 담당자 계정 ID (선택)
  - additional_fields: 커스텀 필드 (선택)
```

**사용 예시:**
```
새 이슈 생성:
- 프로젝트: HWP Report Generator
- 타입: Task
- 제목: "API 공통 규격 구현"
- 설명: "Frontend-Backend 간 표준 JSON 응답 구조 구현"
```

#### 기존 이슈 수정
```
editJiraIssue
- 이슈의 제목, 설명, 담당자, 우선순위 등 수정
- 파라미터:
  - issueIdOrKey: 이슈 ID 또는 키
  - fields: 수정할 필드 객체
```

#### 이슈 상태 변경
```
transitionJiraIssue
- 이슈 워크플로우 상태 변경
- 예시:
  - To Do → In Progress
  - In Progress → Done
  - Open → Resolved
```

**워크플로우 확인:**
```
getTransitionsForJiraIssue
- 특정 이슈에서 가능한 상태 전환 목록 조회
```

---

### 3. **코멘트 관리**

#### 이슈에 코멘트 추가
```
addCommentToJiraIssue
- 파라미터:
  - issueIdOrKey: 이슈 ID 또는 키
  - commentBody: 코멘트 내용 (Markdown 지원)
  - commentVisibility: 접근 권한 설정 (선택)
```

**사용 예시:**
```
"보고서 생성 API 구현 완료. 테스트 진행 중입니다."
```

---

### 4. **프로젝트 관리**

#### 접근 가능한 프로젝트 조회
```
getVisibleJiraProjects
- 현재 사용자가 접근 가능한 프로젝트 목록
- 필터:
  - action: view, browse, edit, create
  - searchString: 프로젝트 이름 검색
```

#### 프로젝트 이슈 타입 메타데이터
```
getJiraProjectIssueTypesMetadata
- 프로젝트에서 사용 가능한 이슈 타입 정보
- 반환: Story, Task, Bug, Epic 등
```

#### 이슈 생성 필드 정보
```
getJiraIssueTypeMetaWithFields
- 특정 이슈 타입 생성 시 필요한 필드 정보
- 필수 필드, 선택 필드, 커스텀 필드 등
```

---

### 5. **링크 및 관계**

#### 외부 링크 조회
```
getJiraIssueRemoteIssueLinks
- Confluence 페이지, 외부 URL 등 연결된 링크 조회
- globalId로 특정 링크 필터링 가능
```

---

### 6. **사용자 관리**

#### 현재 사용자 정보
```
atlassianUserInfo
- 로그인한 사용자의 정보 조회
- 반환: accountId, displayName, email 등
```

#### 사용자 검색
```
lookupJiraAccountId
- 이름 또는 이메일로 사용자 검색
- 담당자 할당 시 accountId 확인용
```

---

## 📝 Confluence 기능

### 1. **스페이스 관리**

#### 스페이스 목록 조회
```
getConfluenceSpaces
- 접근 가능한 Confluence 스페이스 목록
- 필터:
  - type: global, collaboration, knowledge_base, personal
  - status: current, archived
  - keys: 특정 스페이스 키로 필터링
```

---

### 2. **페이지 관리**

#### 페이지 상세 조회
```
getConfluencePage
- 파라미터:
  - cloudId: Atlassian 클라우드 ID
  - pageId: 페이지 ID (URL에서 추출 가능)
- 반환: Markdown 변환된 페이지 본문
```

**페이지 ID 추출 방법:**
```
URL: https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title
→ pageId: "123456789"
```

#### 스페이스 내 페이지 목록
```
getPagesInConfluenceSpace
- 파라미터:
  - spaceId: 스페이스 ID (숫자)
  - title: 제목으로 필터링 (선택)
  - status: current, archived, deleted (선택)
  - subtype: live (Live Docs), page (일반 페이지)
```

#### 새 페이지 생성
```
createConfluencePage
- 파라미터:
  - cloudId: Atlassian 클라우드 ID
  - spaceId: 스페이스 ID
  - title: 페이지 제목
  - body: 페이지 내용 (Markdown 형식 필수)
  - parentId: 부모 페이지 ID (하위 페이지 생성 시)
  - subtype: "live" (Live Doc 생성 시)
  - isPrivate: true/false (비공개 페이지 설정)
```

**사용 예시:**
```
API 문서 페이지 생성:
- 제목: "HWP Report Generator API 명세"
- 본문: Markdown으로 작성된 API 문서
- 스페이스: 개발 문서 스페이스
```

#### 페이지 수정
```
updateConfluencePage
- 파라미터:
  - pageId: 수정할 페이지 ID
  - body: 새 내용 (Markdown)
  - title: 새 제목 (선택)
  - versionMessage: 버전 메시지 (선택)
  - status: current, draft
```

#### 하위 페이지 조회
```
getConfluencePageDescendants
- 특정 페이지의 모든 하위 페이지 조회
- depth 파라미터로 깊이 제한 가능
```

---

### 3. **코멘트 관리**

#### 푸터 코멘트 조회
```
getConfluencePageFooterComments
- 페이지 하단의 일반 코멘트 조회
- 정렬, 상태 필터링 지원
```

#### 인라인 코멘트 조회
```
getConfluencePageInlineComments
- 특정 텍스트에 연결된 인라인 코멘트 조회
- resolutionStatus: resolved, open, dangling
```

#### 푸터 코멘트 생성
```
createConfluenceFooterComment
- 파라미터:
  - pageId: 페이지 ID
  - body: 코멘트 내용 (Markdown)
  - parentCommentId: 답글 작성 시
```

#### 인라인 코멘트 생성
```
createConfluenceInlineComment
- 파라미터:
  - pageId: 페이지 ID
  - body: 코멘트 내용
  - inlineCommentProperties:
    - textSelection: 하이라이트할 텍스트
    - textSelectionMatchIndex: 매칭 인덱스
    - textSelectionMatchCount: 총 매칭 수
```

---

### 4. **검색**

#### CQL로 Confluence 검색
```
searchConfluenceUsingCql
- CQL(Confluence Query Language) 사용
- 예시 쿼리:
  - "title ~ 'API' AND type = page"
  - "space = DEV AND created >= '2025-01-01'"
```

---

## 💡 실제 사용 시나리오

### 시나리오 1: 버그 리포트 워크플로우
1. `createJiraIssue` - Bug 타입 이슈 생성
2. `addCommentToJiraIssue` - 재현 방법 코멘트 추가
3. `transitionJiraIssue` - 상태를 "In Progress"로 변경
4. 수정 완료 후 `transitionJiraIssue` - "Done"으로 변경

### 시나리오 2: 기능 개발 문서화
1. `createJiraIssue` - Story 타입 이슈 생성
2. `createConfluencePage` - 기능 명세 문서 작성
3. 문서 링크를 Jira 이슈에 연결
4. `updateConfluencePage` - 개발 진행 중 문서 업데이트

### 시나리오 3: Sprint 계획
1. `searchJiraIssuesUsingJql` - 백로그 이슈 조회
   ```
   "project = HWPRPT AND status = 'To Do' ORDER BY priority DESC"
   ```
2. 우선순위 높은 이슈 선택
3. `editJiraIssue` - Sprint 필드 할당
4. `transitionJiraIssue` - 상태 변경

### 시나리오 4: API 문서 자동 생성
1. 코드에서 API 명세 추출
2. `createConfluencePage` - Markdown으로 API 문서 생성
3. `createJiraIssue` - API 리뷰 Task 생성
4. Jira 이슈에 Confluence 문서 링크 추가

---

## 🔍 유용한 JQL 쿼리 예시

### 내 작업 조회
```
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC
```

### 최근 생성된 버그
```
project = HWPRPT AND type = Bug AND created >= -7d
```

### 특정 Sprint의 완료된 이슈
```
sprint = "Sprint 1" AND status = Done
```

### 고우선순위 미해결 이슈
```
priority in (Highest, High) AND resolution = Unresolved
```

### 특정 라벨이 붙은 이슈
```
labels = "api-development" AND status != Done
```

---

## 🔍 유용한 CQL 쿼리 예시 (Confluence)

### 최근 수정된 페이지
```
type = page AND lastModified >= '2025-01-01'
```

### 특정 스페이스의 페이지
```
space = DEV AND type = page
```

### 제목 검색
```
title ~ 'API' AND type = page
```

---

## 📚 HWP Report Generator 프로젝트 활용 예시

### 1. 백로그 관리
```
JQL: project = HWPRPT AND status = 'To Do' ORDER BY priority DESC
```

### 2. 버그 트래킹
```
이슈 생성:
- Type: Bug
- Summary: "HWP 파일 생성 시 한글 깨짐 현상"
- Priority: High
- Component: hwp-handler
```

### 3. 기술 문서 작성
```
Confluence 페이지:
- 제목: "HWP Report Generator API 명세"
- 내용:
  - API 엔드포인트 목록
  - 요청/응답 예시
  - 에러 코드 정의
  - 인증 방법
```

### 4. 릴리즈 노트 작성
```
JQL로 완료된 이슈 조회:
"project = HWPRPT AND fixVersion = '1.0.0' AND status = Done"

Confluence에 릴리즈 노트 페이지 생성
```

### 5. Sprint 회고
```
Confluence에 회고 페이지 생성:
- 잘된 점 (Keep)
- 개선할 점 (Problem)
- 액션 아이템 (Try)
```

---

## 🛠️ 도움말 및 팁

### Cloud ID 확인 방법
```
1. getAccessibleAtlassianResources 호출
2. 반환된 cloudId 사용
3. 또는 Atlassian URL에서 추출
```

### 페이지 ID 확인 방법
```
Confluence URL에서 숫자 부분:
https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456789/Title
→ pageId = "123456789"
```

### 스페이스 ID vs 스페이스 Key
```
- Space Key: 문자열 (예: "DEV", "HWPRPT")
- Space ID: 숫자 (예: 12345)
- getConfluenceSpaces로 Space ID 조회 가능
```

### Markdown 지원
```
Confluence 페이지 생성/수정 시:
- body 파라미터에 Markdown 형식 사용 필수
- 자동으로 Confluence 형식으로 변환됨
```

---

## ⚠️ 주의사항

1. **권한 확인**: 모든 작업은 현재 사용자의 권한에 따라 제한됨
2. **Cloud ID**: 정확한 Cloud ID 사용 필요
3. **Markdown 필수**: Confluence 페이지 생성 시 Markdown 형식 필수
4. **페이지 ID**: 페이지 수정 시 정확한 페이지 ID 필요
5. **이슈 타입**: 프로젝트마다 사용 가능한 이슈 타입이 다를 수 있음

---

## 📞 문의 및 지원

Atlassian MCP 연동 관련 문의:
- Atlassian 공식 문서 참조
- MCP 서버 설정 확인
- 인증 토큰 유효성 확인

---

**이 문서는 Atlassian MCP 서버 연동을 통해 사용 가능한 모든 기능을 정리한 것입니다.**
**실제 사용 시 프로젝트 상황에 맞게 활용하시기 바랍니다.**
