# Unit Spec: Topic Plan API

## 1. 요구사항 요약

- **목적:** 사용자가 토픽에 첫 메시지를 보낼 때, Claude AI로부터 보고서 작성 계획을 받아오는 API
- **유형:** ☑ 신규 ☐ 변경 ☐ 삭제
- **핵심 요구사항:**
  - 입력: topic_id, template_id (optional), custom_prompt (optional, 사용자 메시지)
  - 출력: plan (Markdown 형태의 계획), sections (섹션별 제목과 설명)
  - 예외/제약: 토픽 미존재 시 404, 권한 없을 시 403, AI 호출 실패 시 500
  - 처리흐름 요약: 토픽 존재 확인 → Template 기반 프롬프트 구성 → Claude API 호출 → 계획 파싱 → 응답

---

## 2. 구현 대상 파일

| 구분 | 경로                                    | 설명                  |
| ---- | --------------------------------------- | --------------------- |
| 변경 | backend/app/routers/topics.py           | 새 엔드포인트 추가     |
| 변경 | frontend/src/services/topicApi.ts       | plan API 함수 추가    |
| 변경 | frontend/src/types/topic.ts             | PlanRequest/Response 타입 추가 |
| 참조 | backend/app/utils/claude_client.py      | Claude API 호출 참조  |
| 참조 | backend/app/utils/prompts.py            | 프롬프트 구성 참조    |

---

## 3. 동작 플로우 (Mermaid)

```mermaid
flowchart TD
    A[User: 첫 메시지 입력] -->|POST /api/topics/{topic_id}/plan| B[API Router]
    B --> C{토픽 존재?}
    C -- No --> D[404 Error]
    C -- Yes --> E{접근 권한?}
    E -- No --> F[403 Error]
    E -- Yes --> G[Template 조회 by template_id]
    G --> H[프롬프트 구성: System + Custom]
    H --> I[ClaudeClient.generate_plan_markdown]
    I --> J[Claude API 호출]
    J --> K{성공?}
    K -- No --> L[500 Error]
    K -- Yes --> M[Markdown 파싱: 섹션 추출]
    M --> N[PlanResponse 구성]
    N --> O[202 OK + plan/sections 반환]
```

---

## 4. 테스트 계획

### 4.1 원칙

- **테스트 우선(TDD)**: 본 섹션의 항목을 우선 구현하고 코드 작성.
- **계층별 커버리지**: Unit → Integration → API(E2E-lite) 순서로 최소 P0 커버.
- **독립성/재현성**: 외부 연동(Claude API)은 모킹.
- **판정 기준**: 기대 상태코드/스키마/부작용(저장/로그)을 명시적으로 검증.

### 4.2 구현 예상 테스트 항목(각 항목의 목적 포함)

| TC ID      | 계층 | 시나리오              | 목적(무엇을 검증?)                 | 입력/사전조건                        | 기대결과                                           |
| ---------- | ---- | --------------------- | ---------------------------------- | ------------------------------------ | -------------------------------------------------- |
| TC-API-001 | API  | 계획 생성 성공         | API 계약/상태코드/응답 스키마 검증 | `POST /api/topics/1/plan` `{template_id:1, custom_prompt:"보고서 계획"}` | `202`, `plan` 필드 존재, `sections` 배열 존재      |
| TC-API-002 | API  | 토픽 미존재           | 404 에러 핸들링                    | 존재하지 않는 topic_id               | `404`, 에러코드 `TOPIC.NOT_FOUND`                  |
| TC-API-003 | API  | 권한 없음             | 403 에러 핸들링                    | 다른 사용자의 토픽                   | `403`, 에러코드 `TOPIC.UNAUTHORIZED`               |
| TC-API-004 | API  | Claude API 실패       | AI 호출 실패 시 에러 핸들링         | Claude API 모킹 실패 응답           | `500`, 에러코드 `SERVER.AI_ERROR`                  |
| TC-UNIT-005 | Unit | 프롬프트 구성         | Template 기반 프롬프트 생성 검증   | template_id=1, custom_prompt="계획" | 시스템 프롬프트 + 사용자 프롬프트 결합             |
| TC-UNIT-006 | Unit | 계획 파싱            | Markdown → sections 변환 검증      | Markdown 계획 텍스트                | sections 배열 정상 추출 (제목, 설명)               |

### 4.3 샘플 테스트 코드

테스트 작성가이드 `backend/BACKEND_TEST.md` 참조

---

## 5. 사용자 요청 프롬프트

### 5.1 단계별 기록 방식

#### 1단계: 초기 사용자 요청
```
topicApi에
POST /api/topics/{topic_id}/plan 이 경로의 api를 만들어줘. 내용은 아래 참조.
// Request
{
  "template_id": 1,  // 선택: Template 사용 시
  "custom_prompt": "보고서 계획을 세워줘"  // 선택: 커스텀 프롬프트
}

// Response (202 OK)
{
  "success": true,
  "data": {
    "plan": "# 보고서 계획\n\n## 섹션 1\n...",
    "sections": [
      {"title": "요약", "description": "핵심 내용 요약"},
      {"title": "배경", "description": "배경 및 맥락"}
    ]
  }
}

1. api 요청은 사용자가 첫 메시지를 보낼 때 요청한다. custom propmpt에는 사용자 메시지가 들어간다. "template_id": 1로 일단해서 만들어봐
```

#### 2단계: 최종 명확화 (통합)
- ✅ POST /api/topics/{topic_id}/plan 엔드포인트 생성
- ✅ Request: template_id (optional), custom_prompt (optional)
- ✅ Response: 202 OK, plan (Markdown), sections (제목/설명 배열)
- ✅ 사용자 첫 메시지 시 호출
- ✅ template_id = 1 고정으로 구현
- ✅ Frontend topicApi에 함수 추가
- ✅ 표준 API 응답 형식 준수

---

**요청 일시:** 2025-11-13

**컨텍스트/배경:**
- 사용자가 토픽에 첫 메시지를 보낼 때, AI로부터 보고서 작성 계획을 먼저 받아 사용자에게 보여주는 UX 개선
- Template 기반 프롬프트 구성으로 일관된 보고서 구조 제공
- 계획 단계와 실제 보고서 생성 단계 분리

---

## 6. Request/Response 스키마

### Request (PlanRequest)
```python
class PlanRequest(BaseModel):
    template_id: Optional[int] = None
    custom_prompt: Optional[str] = None
```

### Response (PlanResponse)
```python
class Section(BaseModel):
    title: str
    description: str

class PlanResponse(BaseModel):
    plan: str  # Markdown
    sections: List[Section]
```

### TypeScript (Frontend)
```typescript
interface PlanRequest {
  template_id?: number;
  custom_prompt?: string;
}

interface Section {
  title: string;
  description: string;
}

interface PlanResponse {
  plan: string;
  sections: Section[];
}
```

---

## 7. 구현 세부사항

### Backend (topics.py)

1. **엔드포인트:**
   ```python
   @router.post("/{topic_id}/plan", summary="Generate topic plan")
   async def generate_topic_plan(
       topic_id: int,
       plan_request: PlanRequest,
       current_user: User = Depends(get_current_active_user)
   )
   ```

2. **처리 로직:**
   - 토픽 존재 및 소유권 확인
   - Template 조회 (template_id가 있으면)
   - 프롬프트 구성: 시스템 프롬프트 + 사용자 프롬프트
   - ClaudeClient 호출 (generate_plan_markdown)
   - Markdown 파싱하여 섹션 추출
   - PlanResponse 구성 및 반환

3. **에러 코드:**
   - `TOPIC.NOT_FOUND`: 토픽 미존재
   - `TOPIC.UNAUTHORIZED`: 접근 권한 없음
   - `SERVER.AI_ERROR`: Claude API 호출 실패

### Frontend (topicApi.ts)

1. **API 함수:**
   ```typescript
   generateTopicPlan: async (topicId: number, data: PlanRequest): Promise<PlanResponse> => {
       const response = await api.post<ApiResponse<PlanResponse>>(
           API_ENDPOINTS.TOPIC_PLAN(topicId),
           data
       )
       // 성공/실패 처리
       return response.data.data
   }
   ```

2. **Endpoint 상수 추가 (constants/index.ts):**
   ```typescript
   TOPIC_PLAN: (topicId: number) => `/api/topics/${topicId}/plan`
   ```

---

## 8. 프롬프트 전략

### 계획 생성 프롬프트 (예시)

```
당신은 금융 기관의 전문 보고서 작성자입니다.

사용자의 주제를 분석하여 보고서 작성 계획을 세워주세요.
다음 형식으로 작성하세요:

# 보고서 계획

## 1. 요약
[요약 섹션에 들어갈 내용 계획]

## 2. 배경
[배경 섹션에 들어갈 내용 계획]

## 3. 주요 내용
[주요 내용 섹션에 들어갈 내용 계획]

## 4. 결론
[결론 섹션에 들어갈 내용 계획]

사용자 주제: {custom_prompt}
```

### 섹션 파싱 전략

- H2 헤더 (##)를 섹션으로 인식
- 섹션 제목 추출
- 섹션 하위 텍스트를 description으로 추출
- sections 배열 구성

---

**작성일:** 2025-11-13
**작성자:** Claude Code
**버전:** 1.0
