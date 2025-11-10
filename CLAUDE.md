# CLAUDE.md - HWP Report Generator 개발 가이드

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고하는 종합 개발 가이드입니다.

---

## ⚠️ CRITICAL: 백엔드 개발 시 Unit Spec 우선 규칙

### 🔴 의무 규칙 (반드시 따라야 함)

**Rule #1: 반드시 Unit Spec부터 작성**
- 모든 신규 기능, 버그 수정, 리팩토링은 **코드 작성 전에 반드시 Unit Spec을 먼저 작성**
- 규모가 작아도, 간단해 보여도 **예외 없음**
- Unit Spec 없이 코드 작성은 거절됨

**Rule #2: 사용자 승인 후에만 구현**
- Unit Spec 작성 후 사용자의 검토 및 승인을 받을 때까지 대기
- 사용자가 수정을 요청하면 스펙을 수정
- 승인이 나면 그제서야 구현 시작

**Rule #3: Spec을 100% 준수하여 구현**
- 승인된 Spec에서 정의한 테스트 케이스를 모두 통과시켜야 함
- Spec의 파일 변경, 엔드포인트, 로직을 정확히 따름
- 사용자 승인 없이 Spec 변경 금지

**Rule #4: 모든 문서와 테스트 함께 제출**
- 코드 + 테스트 + Unit Spec 문서를 함께 커밋
- CLAUDE.md 업데이트 포함

### 🎯 Claude Code가 따를 프롬프트 지시

> **백엔드 코드 작업을 시작하기 전에 반드시 이를 읽으세요.**

**Step 1: 사용자 요청 분석**
- 사용자가 백엔드 기능을 요청하면, **절대로 코드를 먼저 작성하지 마세요**
- 신규 기능, 버그 수정, 리팩토링 모두 동일하게 적용

**Step 2: Unit Spec 작성 (90% 이상의 시간을 여기에)**
```
// 생성할 Spec 파일 경로
backend/doc/specs/YYYYMMDD_feature_name.md

// 사용할 템플릿
backend/doc/Backend_UnitSpec.md

// 포함할 항목 (모두 필수):
1. 요구사항 요약 (Purpose, Type, Core Requirements)
2. 구현 대상 파일 (New/Change/Reference 표)
3. 흐름도 (Mermaid flowchart 또는 sequence diagram)
4. 테스트 계획 (최소 3개 이상의 TC, Layer별 분류)
5. 에러 처리 시나리오
```

**Step 3: 사용자 검토 대기**
- Spec을 사용자에게 제시하고 승인을 받을 때까지 대기
- "이 Spec이 맞나요? 수정할 부분이 있나요?" 물어보기
- 사용자 의견 반영하여 Spec 수정

**Step 4: 승인 후 구현**
- 사용자 승인 이후에만 코드 작성 시작
- Spec에서 정의한 테스트 케이스를 먼저 작성 (TDD)
- 테스트가 모두 통과할 때까지 구현

**Step 5: 최종 검증 및 커밋**
- 모든 테스트 통과 확인
- CLAUDE.md 업데이트
- Unit Spec 문서 + 코드 + 테스트 함께 커밋

---

## 프로젝트 개요

**HWP Report Generator**: Claude AI를 활용하여 한글(HWP) 형식의 금융 보고서를 자동 생성하는 FastAPI 기반 웹 시스템입니다.

- 사용자가 주제를 입력 → Claude AI로 보고서 내용 자동 생성 → HWPX 형식 파일 생성
- **v2.0+**: 대화형 시스템 (토픽 기반 스레드, 메시지 체이닝)
- **v2.2**: Template 기반 동적 System Prompt 지원
- **v2.3**: 통합 문서화 및 아키텍처 정리

---

## 기술 스택

| 영역 | 스택 | 버전 |
|------|------|------|
| **Backend** | FastAPI | 0.104.1 |
| **Runtime** | Python | 3.12 |
| **패키지 관리** | uv / pip | - |
| **AI** | Anthropic Claude API | anthropic==0.71.0 |
| **Model** | Claude Sonnet 4.5 | claude-sonnet-4-5-20250929 |
| **DB** | SQLite | 3.x |
| **HWPX 처리** | olefile, zipfile | olefile==0.47 |
| **인증** | JWT | python-jose==3.3.0 |
| **해싱** | bcrypt | bcrypt==4.1.2 |
| **Frontend** | React + TypeScript | 18.x / 5.x |

---

## 🗂️ 백엔드 아키텍처 (완전 분석)

### 1. 디렉토리 구조

```
backend/app/
├── main.py                          # FastAPI 진입점 (라우터 등록, 초기화)
│
├── routers/                         # API 엔드포인트 (6개)
│   ├── auth.py                      # 인증 (회원가입, 로그인, JWT)
│   ├── topics.py                    # 토픽/보고서 생성 (메시지 체이닝)
│   ├── messages.py                  # 메시지 조회
│   ├── artifacts.py                 # 아티팩트 (MD, HWPX) 다운로드/변환
│   ├── templates.py                 # ✨ 템플릿 업로드/관리
│   └── admin.py                     # 관리자 API
│
├── models/                          # Pydantic 데이터 모델 (9개)
│   ├── user.py                      # User, UserCreate, UserUpdate
│   ├── topic.py                     # Topic, TopicCreate (+ template_id)
│   ├── message.py                   # Message, AskRequest (+ template_id)
│   ├── template.py                  # ✨ Template, Placeholder, TemplateCreate
│   ├── artifact.py                  # Artifact, ArtifactCreate, ArtifactKind
│   ├── ai_usage.py                  # AiUsage, AiUsageCreate
│   ├── transformation.py            # Transformation, TransformOperation
│   ├── token_usage.py               # TokenUsage (레거시)
│   └── report.py                    # Report (레거시, Deprecated)
│
├── database/                        # SQLite CRUD 레이어 (11개)
│   ├── connection.py                # DB 초기화, 테이블 생성, 마이그레이션
│   ├── user_db.py                   # User CRUD
│   ├── topic_db.py                  # Topic CRUD
│   ├── message_db.py                # Message CRUD (seq_no 관리)
│   ├── artifact_db.py               # Artifact CRUD (버전 관리)
│   ├── template_db.py               # ✨ Template CRUD + 트랜잭션
│   ├── ai_usage_db.py               # AI 사용량 추적
│   ├── transformation_db.py         # 변환 이력 (MD→HWPX)
│   ├── token_usage_db.py            # 레거시 토큰 추적
│   ├── report_db.py                 # 레거시 보고서
│   └── __init__.py                  # DB 초기화 함수 export
│
└── utils/                           # 비즈니스 로직 및 헬퍼 (13개)
    ├── prompts.py                   # ✨ System Prompt 중앙 관리
    ├── templates_manager.py         # ✨ HWPX 파일/Placeholder 처리
    ├── claude_client.py             # Claude API 호출 (Markdown 응답)
    ├── markdown_parser.py           # Markdown → 구조화 데이터 (동적 섹션)
    ├── markdown_builder.py          # 구조화 데이터 → Markdown
    ├── hwp_handler.py               # HWPX 수정/생성 (XML 조작)
    ├── artifact_manager.py          # 아티팩트 파일 관리 (저장, 해시)
    ├── file_utils.py                # 파일 I/O 유틸 (쓰기, 읽기, 해시)
    ├── md_handler.py                # Markdown 파일 전용 I/O
    ├── response_helper.py           # API 표준 응답 (success, error)
    ├── auth.py                      # JWT, 비밀번호 해싱
    └── meta_info_generator.py       # Placeholder 메타정보 생성 (향후)
```

### 2. 라우터 (Routers) 상세

#### ✨ templates.py - 템플릿 관리 (신규)

```python
# 엔드포인트
POST   /api/templates              # 템플릿 업로드 (HWPX)
GET    /api/templates              # 내 템플릿 목록
GET    /api/templates/{id}         # 템플릿 상세 조회
DELETE /api/templates/{id}         # 템플릿 삭제
GET    /api/admin/templates        # Admin: 전체 템플릿 조회

# 주요 함수
async def upload_template(file: UploadFile, title: str, current_user: User)
    # 1. 파일 유효성 검사 (.hwpx만)
    # 2. HWPX 파일 검증
    # 3. Placeholder 추출
    # 4. 메타정보 생성 (prompt_user, prompt_system)
    # 5. DB 저장 (Template + Placeholder, 트랜잭션)
    # 6. 응답 반환

async def get_my_templates(current_user: User) -> List[Template]
async def get_template(template_id: int, current_user: User) -> Template
async def delete_template(template_id: int, current_user: User) -> bool
```

#### topics.py - 토픽/보고서 생성

```python
# 엔드포인트
POST   /api/topics                         # 토픽 생성
POST   /api/topics/generate                # 한 번에 보고서 생성 (template_id 선택)
GET    /api/topics                         # 내 토픽 목록
GET    /api/topics/{id}                    # 토픽 상세 조회
PUT    /api/topics/{id}                    # 토픽 업데이트
DELETE /api/topics/{id}                    # 토픽 삭제
POST   /api/topics/{id}/ask                # 메시지 체이닝 (대화)

# 핵심 함수
async def generate_topic_report(
    topic_data: TopicCreate,
    current_user: User
) -> ApiResponse[Dict]:
    """
    1. 입력 검증
    2. Template 기반 System Prompt 선택
    3. Claude API 호출
    4. Markdown 파싱
    5. Topic 생성
    6. User/Assistant 메시지 저장
    7. Artifact (MD) 저장
    8. AI Usage 기록
    9. 응답 반환
    """

async def ask(
    topic_id: int,
    body: AskRequest,
    current_user: User
) -> ApiResponse[Dict]:
    """
    1. 권한/검증 확인
    2. 사용자 메시지 저장
    3. 참조 문서 선택 (artifact_id 또는 최신 MD)
    4. 컨텍스트 구성 (메시지 + 문서 내용)
    5. System Prompt 선택 (custom > template_id > default)
    6. Claude API 호출
    7. Assistant 메시지 저장
    8. Artifact (MD) 저장
    9. AI Usage 기록
    10. 응답 반환
    """
```

#### artifacts.py - 아티팩트 관리

```python
GET    /api/artifacts/{id}                 # 메타정보 조회
GET    /api/artifacts/{id}/content         # 내용 조회 (MD만)
GET    /api/artifacts/{id}/download        # 파일 다운로드
POST   /api/artifacts/{id}/convert         # MD → HWPX 변환
GET    /api/artifacts/messages/{msg_id}/hwpx/download  # 자동 변환 후 다운로드
```

#### messages.py, auth.py, admin.py

```python
# messages.py
GET    /api/topics/{topic_id}/messages     # 메시지 목록

# auth.py
POST   /api/auth/register                  # 회원가입
POST   /api/auth/login                     # 로그인
GET    /api/auth/me                        # 내 정보
POST   /api/auth/logout                    # 로그아웃

# admin.py
GET    /api/admin/users                    # 사용자 목록
POST   /api/admin/users/{id}/approve       # 사용자 승인
GET    /api/admin/token-usage              # 토큰 사용량
```

### 3. 모델 (Models) 상세

#### ✨ template.py - 템플릿 모델

```python
class Placeholder(BaseModel):
    """Placeholder ({{KEY}})"""
    id: int
    template_id: int
    placeholder_key: str        # "{{TITLE}}", "{{SUMMARY}}" 등
    created_at: datetime

class TemplateBase(BaseModel):
    title: str                  # 템플릿 제목
    description: Optional[str]  # 설명

class TemplateCreate(TemplateBase):
    filename: str               # 원본 파일명
    file_path: str              # 저장 경로
    file_size: int              # 파일 크기
    sha256: str                 # 무결성 체크
    prompt_user: Optional[str]  # ✨ Placeholder 목록 (쉼표 구분)
    prompt_system: Optional[str]  # ✨ 동적 System Prompt

class Template(TemplateCreate):
    id: int
    user_id: int                # 템플릿 소유자
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**특징:**
- `prompt_user`: Placeholder 키 목록 (예: "TITLE, SUMMARY, BACKGROUND")
- `prompt_system`: 동적 생성된 System Prompt (예: "당신은 금융... {{TITLE}}... {{SUMMARY}}...")
- 트랜잭션 기반 저장 (Template + Placeholder 원자성)

#### topic.py, message.py 확장

```python
class TopicCreate(BaseModel):
    input_prompt: str                   # 사용자 입력 주제
    language: str = "ko"
    template_id: Optional[int] = None   # ✨ 선택: 템플릿 ID

class AskRequest(BaseModel):
    content: str                        # 사용자 질문
    artifact_id: Optional[int] = None   # 참조 아티팩트
    include_artifact_content: bool = False  # 문서 내용 포함 여부
    max_messages: Optional[int] = None  # 컨텍스트 메시지 제한
    system_prompt: Optional[str] = None # 커스텀 System Prompt
    template_id: Optional[int] = None   # ✨ 선택: 템플릿 ID
```

**우선순위:**
1. `system_prompt` (명시적 지정) → 사용
2. `template_id` (선택) → Template 기반 동적 Prompt 생성
3. 기본값 → `FINANCIAL_REPORT_SYSTEM_PROMPT`

### 4. 데이터베이스 (Database) 상세

#### 핵심 테이블 스키마

```sql
-- 사용자 테이블
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 토픽 테이블 (대화 스레드)
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    input_prompt TEXT NOT NULL,
    generated_title TEXT,
    language TEXT NOT NULL DEFAULT 'ko',
    status TEXT NOT NULL DEFAULT 'active',  -- active, archived, deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 메시지 테이블
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    role TEXT NOT NULL,                 -- user, assistant, system
    content TEXT NOT NULL,
    seq_no INTEGER NOT NULL,            -- 순서 번호 (대화 순서)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    UNIQUE(topic_id, seq_no)
);

-- 아티팩트 테이블
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    message_id INTEGER,                 -- 생성한 메시지
    kind TEXT NOT NULL,                 -- MD, HWPX, PDF
    locale TEXT NOT NULL,               -- 언어 (ko, en)
    version INTEGER NOT NULL,           -- 버전 번호
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- ✨ 템플릿 테이블 (신규)
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    prompt_user TEXT DEFAULT NULL,        -- ✨ Placeholder 목록
    prompt_system TEXT DEFAULT NULL,      -- ✨ 동적 System Prompt
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Placeholder 테이블
CREATE TABLE placeholders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    placeholder_key TEXT NOT NULL,      -- {{TITLE}}, {{SUMMARY}} 등
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
);

-- AI 사용량 테이블
CREATE TABLE ai_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    message_id INTEGER,
    model TEXT NOT NULL,                -- claude-sonnet-4-5-20250929
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);
```

#### ✨ template_db.py - Template CRUD (트랜잭션)

```python
class TemplateDB:
    @staticmethod
    def create_template_with_transaction(
        user_id: int,
        template_data: TemplateCreate,
        placeholder_keys: List[str]
    ) -> Template:
        """
        Template과 Placeholder를 트랜잭션으로 저장

        실패 시 자동 롤백 (원자성 보장)
        """

    @staticmethod
    def get_template_by_id(template_id: int, user_id: Optional[int] = None) -> Optional[Template]:
        """
        user_id 지정: 해당 사용자의 template만 조회 (권한 확인)
        user_id 미지정: Admin용 (모든 template 조회)
        """

    @staticmethod
    def list_templates_by_user(user_id: int) -> List[Template]:
        """사용자의 모든 template 조회"""

    @staticmethod
    def delete_template(template_id: int) -> bool:
        """template 삭제 (Placeholder도 함께 삭제)"""
```

#### PlaceholderDB

```python
class PlaceholderDB:
    @staticmethod
    def create_placeholder(template_id: int, placeholder_key: str) -> Placeholder

    @staticmethod
    def get_placeholders_by_template(template_id: int) -> List[Placeholder]

    @staticmethod
    def delete_placeholders_by_template(template_id: int) -> bool
```

### 5. 유틸리티 (Utils) 상세

#### ✨ prompts.py - System Prompt 중앙 관리

```python
# 기본 System Prompt (상수)
FINANCIAL_REPORT_SYSTEM_PROMPT = """당신은 금융 기관의 전문 보고서 작성자입니다.
다음 구조로 Markdown 보고서를 작성하세요:

# [보고서 제목]
## [요약 섹션 제목]
[요약 내용]
## [배경 섹션 제목]
[배경 내용]
## [주요 내용 섹션 제목]
[주요 내용]
## [결론 섹션 제목]
[결론 내용]
"""

# ✨ 동적 System Prompt 생성
def create_dynamic_system_prompt(placeholders: List[Placeholder]) -> str:
    """
    Template의 Placeholder를 기반으로 동적 System Prompt 생성

    예:
        placeholders = [Placeholder(placeholder_key="{{TITLE}}"), ...]
        prompt = create_dynamic_system_prompt(placeholders)
        # → "당신은 금융... {{TITLE}}... {{SUMMARY}}를 포함하여..."
    """

# Topic Context 메시지 생성
def create_topic_context_message(topic_input_prompt: str) -> dict:
    """대화 주제를 포함하는 context message 생성"""
    return {
        "role": "user",
        "content": f"다음 주제로 보고서를 작성해주세요:\n\n{topic_input_prompt}"
    }
```

#### ✨ templates_manager.py - HWPX 파일/Placeholder 처리

```python
class TemplatesManager:
    def validate_hwpx(self, file_content: bytes) -> bool:
        """HWPX 파일 유효성 검사 (ZIP 매직 바이트 확인)"""

    def extract_hwpx(self, file_path: str) -> str:
        """
        HWPX를 임시 디렉토리에 언팩

        반환: 언팩된 디렉토리 경로
        """

    def extract_placeholders(self, work_dir: str) -> List[str]:
        """
        HWPX 파일에서 Placeholder 추출

        정규식: {{[A-Z_]+}}
        반환: ["{{TITLE}}", "{{SUMMARY}}", ...]
        """

    def has_duplicate_placeholders(self, placeholders: List[str]) -> bool:
        """Placeholder 중복 검사"""

    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        """SHA256 해시 계산"""
```

#### claude_client.py - Claude API 호출

```python
class ClaudeClient:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = 4096
        self.client = Anthropic(api_key=self.api_key)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> Tuple[str, int, int]:
        """
        Claude API 호출

        Args:
            messages: [{"role": "user", "content": "..."}, ...]
            system_prompt: 시스템 프롬프트

        Returns:
            (응답_텍스트, input_tokens, output_tokens)
        """

    def generate_report(self, topic: str) -> str:
        """레거시: 보고서 생성 (Markdown 반환)"""

    def get_token_usage(self) -> Dict:
        """마지막 호출의 토큰 사용량"""
```

#### markdown_parser.py - Markdown → 구조화 데이터

```python
def parse_markdown_to_content(md_text: str) -> Dict[str, str]:
    """
    Markdown을 HWP 플레이스홀더용 content dict로 변환

    반환:
    {
        "title": "보고서 제목",
        "summary": "요약 내용",
        "background": "배경 내용",
        "main_content": "주요 내용",
        "conclusion": "결론 내용",
        "title_summary": "요약 섹션 제목",
        "title_background": "배경 섹션 제목",
        "title_main_content": "주요 내용 섹션 제목",
        "title_conclusion": "결론 섹션 제목"
    }

    특징:
    - H1 추출: 제목
    - H2 섹션: 키워드 기반 자동 분류 (동적 섹션 추출)
    - 동적 제목: 각 섹션의 실제 H2 제목을 title_xxx로 저장
    """

def classify_section(section_title: str) -> str:
    """
    섹션 제목을 'summary', 'background', 'main_content', 'conclusion' 중 하나로 분류

    우선순위:
    1. 결론 키워드 먼저 체크 (높음) → "향후 추진 계획" 올바르게 분류
    2. 배경 키워드
    3. 주요 내용 키워드
    4. 요약 키워드
    """

def extract_all_h2_sections(md_text: str) -> List[Tuple[str, str]]:
    """H2 섹션 모두 추출 → [(제목, 내용), ...]"""
```

#### markdown_builder.py - 구조화 데이터 → Markdown

```python
def build_report_md(content: Dict[str, str]) -> str:
    """
    content dict를 Markdown 포맷으로 빌드

    입력:
    {
        "title": "...",
        "title_summary": "...",
        "summary": "...",
        ...
    }

    반환:
    # 제목
    ## 요약 섹션 제목
    요약 내용
    ...
    """
```

#### hwp_handler.py - HWPX 수정/생성

```python
class HWPHandler:
    def __init__(self, template_path: str, temp_dir: str, output_dir: str):
        self.template_path = template_path
        self.temp_dir = temp_dir
        self.output_dir = output_dir

    def generate_report(self, content: Dict[str, str]) -> str:
        """
        Template HWPX를 언팩 → XML 수정 → 재압축

        1. 템플릿 HWPX 언팩
        2. section0.xml 파싱
        3. 플레이스홀더 {{KEY}} 치환
        4. 줄바꿈 처리 (\\n\\n → 문단, \\n → 줄바꿈)
        5. 재압축 → HWPX 파일 생성

        반환: 생성된 파일 경로
        """
```

---

## E2E (End-to-End) 플로우

### 시나리오 1: Template 업로드 → Topic 생성 → 보고서 생성

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣ 사용자: 템플릿 파일 업로드                               │
│ POST /api/templates                                          │
│ - file: report_template.hwpx (binary)                        │
│ - title: "재무보고서 템플릿"                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2️⃣ 백엔드: Template 저장                                    │
│ - HWPX 파일 검증                                            │
│ - Placeholder 추출: {{TITLE}}, {{SUMMARY}}, ...             │
│ - 동적 System Prompt 생성                                   │
│ - DB 저장 (Template + Placeholder + 메타정보)               │
│ ✅ 응답: { template_id: 1, placeholders: [...] }           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3️⃣ 사용자: 보고서 생성 (Template 선택)                    │
│ POST /api/topics/generate                                   │
│ {                                                            │
│   "input_prompt": "2025 디지털뱅킹 트렌드 분석",             │
│   "template_id": 1  ← ✨ 선택된 Template                    │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4️⃣ 백엔드: 동적 System Prompt 생성 및 Claude 호출         │
│ a) Template #1 로드                                         │
│ b) Placeholder 조회: [{{TITLE}}, {{SUMMARY}}, ...]          │
│ c) create_dynamic_system_prompt(placeholders)               │
│    → "당신은 금융... {{TITLE}}를 포함하여..."                │
│ d) Claude API 호출:                                        │
│    system_prompt = (동적 System Prompt)                    │
│    user_message = "2025 디지털뱅킹 트렌드 분��으로..."      │
│ e) 응답: Markdown 텍스트                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5️⃣ 백엔드: Markdown 파싱 및 보고서 저장                    │
│ a) parse_markdown_to_content(response)                      │
│    → {title, summary, background, main_content, ...}       │
│ b) build_report_md(content) → Markdown 포맷                 │
│ c) Topic, Message, Artifact (MD) 생성                       │
│ d) AI Usage 기록                                             │
│ ✅ 응답: { topic_id: 42, artifact_id: 100 }               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6️⃣ 사용자: MD → HWPX 변환 및 다운로드                      │
│ POST /api/artifacts/100/convert                             │
│ → HWPX 파일 생성                                            │
│ GET /api/artifacts/{hwpx_artifact_id}/download              │
│ → 보고서 다운로드 (보고서.hwpx)                             │
└─────────────────────────────────────────────────────────────┘
```

### 시나리오 2: 대화형 메시지 체이닝 (Ask)

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣ 사용자: 질문 입력 (Template 선택, 참조 문서 지정)       │
│ POST /api/topics/42/ask                                     │
│ {                                                            │
│   "content": "이 내용을 더 자세히 설명해주세요",             │
│   "template_id": 1,                ← ✨ Template 선택       │
│   "artifact_id": 100,              ← 참조할 MD 문서         │
│   "include_artifact_content": true,← 문서 내용 포함         │
│   "max_messages": 10               ← 컨텍스트 제한          │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2️⃣ 백엔드: 컨텍스트 구성                                    │
│ a) 권한 확인: 사용자가 Topic 소유                           │
│ b) 사용자 메시지 저장                                        │
│ c) 컨텍스트 메시지 수집:                                    │
│    - artifact_id 명시 → 해당 메시지까지의 이전 메시지만    │
│    - max_messages 적용 → 최근 N개 메시지만                 │
│ d) 참조 문서 내용 주입:                                     │
│    "현재 보고서(MD):\n\n[artifact 내용]"                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3️⃣ 백엔드: System Prompt 선택 (우선순위)                  │
│ 우선순위 1: body.system_prompt (명시적 지정) ✓             │
│ 우선순위 2: body.template_id (선택) ✓                      │
│   → Template 로드                                           │
│   → Placeholder 조회                                        │
│   → create_dynamic_system_prompt()                         │
│ 우선순위 3: FINANCIAL_REPORT_SYSTEM_PROMPT (기본)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4️⃣ 백엔드: Claude API 호출                                 │
│ a) claude_messages = [topic_context] + [previous_msgs]     │
│ b) claude.chat_completion(claude_messages, system_prompt) │
│ c) 응답: Markdown 텍스트                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5️⃣ 백엔드: 응답 저장 및 아티팩트 생성                     │
│ a) Assistant 메시지 저장                                    │
│ b) Markdown 파싱 및 빌드                                    │
│ c) Artifact (MD v2) 생성                                    │
│ d) AI Usage 기록                                             │
│ ✅ 응답: {                                                  │
│      topic_id, user_message, assistant_message,            │
│      artifact, usage (토큰, 지연시간)                       │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6️⃣ 사용자: 응답 확인 및 다음 액션                          │
│ - 대화 계속: POST /api/topics/42/ask (새 메시지)           │
│ - 최신 MD 다운로드: GET /api/artifacts/{artifact_id}/...  │
│ - HWPX 변환: POST /api/artifacts/{artifact_id}/convert    │
└─────────────────────────────────────────────────────────────┘
```

---

## 환경 변수 (Environment Variables)

### 필수 설정 (`backend/.env`)

```env
# ======================================
# 프로젝트 경로 (필수!)
# ======================================
PATH_PROJECT_HOME=/Users/jaeyoonmo/workspace/hwp-report-generator

# ======================================
# Claude API 설정
# ======================================
CLAUDE_API_KEY=sk-ant-...your-api-key...
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# ======================================
# JWT 인증 설정
# ======================================
JWT_SECRET_KEY=your-secret-key-min-32-chars-recommended
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# ======================================
# 관리자 계정 (초기 생성)
# ======================================
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123!@#
ADMIN_USERNAME=관리자

# ======================================
# 데이터베이스 (선택사항)
# ======================================
# 기본: backend/data/hwp_reports.db
# DATABASE_URL=sqlite:///path/to/database.db
```

### 환경 변수 로딩 프로세스

```python
# main.py
from dotenv import load_dotenv, find_dotenv

# 1. .env 파일 자동 검색
env_file_path = find_dotenv()

# 2. .env 로드
load_dotenv(env_file_path)

# 3. 경로 설정
PATH_PROJECT_HOME = os.getenv("PATH_PROJECT_HOME")
if not PATH_PROJECT_HOME:
    # 에러 메시지 출력 후 종료
    sys.exit(1)

# 4. sys.path에 프로젝트 루트 추가 (shared 모듈 import 가능하게)
project_root = Path(PATH_PROJECT_HOME)
sys.path.insert(0, str(project_root))
```

### 폴더 구조 (PATH_PROJECT_HOME 기준)

```
{PATH_PROJECT_HOME}/
├── backend/
│   ├── app/
│   ├── templates/          # HWPX 템플릿
│   ├── artifacts/          # 생성된 아티팩트 (MD, HWPX)
│   ├── data/               # SQLite DB (hwp_reports.db)
│   ├── temp/               # 임시 파일
│   └── .env                # 환경 설정
├── frontend/
└── shared/                 # 공유 타입/상수
```

---

## 주요 함수 및 흐름

### generate_topic_report() - 9단계 플로우

```python
@router.post("/generate", summary="주제 입력 → MD 보고서 생성")
async def generate_topic_report(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] 입력 검증
        - input_prompt 필수, 3자 이상

    [Step 2] Template 기반 System Prompt 선택
        IF topic_data.template_id:
            - Template 로드
            - Placeholder 조회
            - create_dynamic_system_prompt() 호출
        ELSE:
            - FINANCIAL_REPORT_SYSTEM_PROMPT 사용

    [Step 3] Claude API 호출
        - user_message = create_topic_context_message(input_prompt)
        - system_prompt = (Step 2 결과)
        - response = claude.chat_completion([user_message], system_prompt)

    [Step 4] Markdown 파싱
        - content = parse_markdown_to_content(response)
        - 동적 섹션 추출 (title, summary, background, ...)

    [Step 5] Topic 생성
        - topic = TopicDB.create_topic(...)
        - generated_title 업데이트

    [Step 6] 메시지 저장
        - user_msg = MessageDB.create_message(USER)
        - assistant_msg = MessageDB.create_message(ASSISTANT)

    [Step 7] Artifact (MD) 저장
        - md_text = build_report_md(content)
        - artifact = ArtifactDB.create_artifact(kind=MD)

    [Step 8] AI Usage 기록
        - AiUsageDB.create_ai_usage(input_tokens, output_tokens, latency_ms)

    [Step 9] 응답 반환
        - { topic_id, artifact_id, message_ids, usage }
    """
```

### ask() - 12단계 플로우

```python
@router.post("/{topic_id}/ask", summary="메시지 체이닝 (대화)")
async def ask(
    topic_id: int,
    body: AskRequest,
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] 권한 및 검증
        - Topic 존재 확인
        - 소유권 확인 (topic.user_id == current_user.id)
        - content 필수, 1자 이상
        - content 길이 검증 (50,000자 이하)

    [Step 2] 사용자 메시지 저장
        - user_msg = MessageDB.create_message(topic_id, MessageCreate(role=USER))

    [Step 3] 참조 문서 선택
        IF body.artifact_id:
            - artifact = ArtifactDB.get_artifact_by_id(body.artifact_id)
            - 권한 확인 (artifact.topic_id == topic_id)
            - 타입 확인 (kind == MD)
        ELSE:
            - artifact = ArtifactDB.get_latest_artifact_by_kind(topic_id, MD)

    [Step 4] 컨텍스트 구성
        - all_messages = MessageDB.get_messages_by_topic(topic_id)
        - user_messages = [m for m in all_messages if m.role == USER]
        - artifact_id 명시 → 해당 메시지까지만 포함
        - max_messages 적용 → 최근 N개만

    [Step 5] 문서 내용 주입
        IF body.include_artifact_content AND artifact exists:
            - md_content = read(artifact.file_path)
            - artifact_message = "현재 보고서(MD):\n\n{md_content}"
            - context_messages에 추가

    [Step 6] 컨텍스트 크기 검증
        - total_chars = sum(len(m.content) for m in context_messages)
        - MAX_CONTEXT_CHARS = 50,000
        - 초과 시 error_response 반환

    [Step 7] System Prompt 선택 (우선순위)
        IF body.system_prompt:
            - system_prompt = body.system_prompt
        ELIF body.template_id:
            - template = TemplateDB.get_template_by_id(body.template_id)
            - placeholders = PlaceholderDB.get_placeholders_by_template()
            - system_prompt = create_dynamic_system_prompt(placeholders)
        ELSE:
            - system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT

    [Step 8] Claude API 호출
        - claude_messages = [topic_context] + [context_messages] + [user_msg]
        - response = claude.chat_completion(claude_messages, system_prompt)

    [Step 9] Assistant 메시지 저장
        - assistant_msg = MessageDB.create_message(topic_id, MessageCreate(role=ASSISTANT))

    [Step 10] Artifact (MD) 저장
        - result = parse_markdown_to_content(response)
        - md_text = build_report_md(result)
        - artifact = ArtifactDB.create_artifact(kind=MD, version++)

    [Step 11] AI Usage 기록
        - AiUsageDB.create_ai_usage(...)

    [Step 12] 응답 반환
        - {
            topic_id,
            user_message,
            assistant_message,
            artifact,
            usage { model, input_tokens, output_tokens, latency_ms }
          }
    """
```

### upload_template() - 템플릿 업로드

```python
@router.post("", summary="HWPX 템플릿 업로드")
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """
    [Step 1] 파일 유효성 검사
        - 파일 명 확인 (.hwpx만)
        - 파일 크기 확인 (최대 50MB)

    [Step 2] HWPX 파일 검증
        - TemplatesManager.validate_hwpx()
        - ZIP 매직 바이트 확인 (PK\\x03\\x04)

    [Step 3] 파일 저장
        - 경로: templates/user_{user_id}/template_{timestamp}.hwpx
        - SHA256 해시 계산

    [Step 4] Placeholder 추출
        - TemplatesManager.extract_hwpx() → 임시 디렉토리에 언팩
        - TemplatesManager.extract_placeholders() → {{KEY}} 추출
        - 결과: ["{{TITLE}}", "{{SUMMARY}}", ...]

    [Step 5] 중복 검사
        - TemplatesManager.has_duplicate_placeholders()
        - 중복 있으면 경고 (거부하지 않음)

    [Step 6] 메타정보 생성
        - prompt_user = ", ".join(unique_placeholders)
          → "TITLE, SUMMARY, BACKGROUND, ..."
        - placeholder_objs = [Placeholder(placeholder_key=ph) ...]
        - system_prompt = create_dynamic_system_prompt(placeholder_objs)
          → "당신은 금융... {{TITLE}}... {{SUMMARY}}..."

    [Step 7] DB 저장 (트랜잭션)
        - TemplateDB.create_template_with_transaction(
            user_id,
            TemplateCreate(
              ..., prompt_user, prompt_system
            ),
            placeholder_keys
          )
        - 실패 시 자동 롤백

    [Step 8] 임시 파일 정리
        - 임시 언팩 디렉토리 삭제

    [Step 9] 응답 반환
        - {
            id, title, filename, prompt_user, prompt_system,
            placeholders: [{ key, ... }, ...]
          }
    """
```

---

## 주요 개선사항 (v2.0 → v2.3)

### v2.3 (2025-11-10) - 통합 문서화

✅ **백엔드 CLAUDE.md 완전 갱신**
- 주요 함수 E2E 플로우 상세 분석
- 모든 라우터, 모델, DB 구조 문서화
- 환경 변수 설정 가이드
- 12단계 ask() 플로우 도식화

✅ **아키텍처 정리**
- 라우터 6개, 모델 9개, DB 11개, Utils 13개 분류
- 각 컴포넌트의 역할 명확화
- 의존성 관계 정의

### v2.2 (2025-11-10) - 동적 Prompt + 마크다운 파싱 수정

✅ **Template 기반 동적 System Prompt**
- 템플릿 업로드 시 Placeholder 추출 → System Prompt 자동 생성
- POST /api/topics/generate, POST /api/topics/{id}/ask에서 template_id 지원
- 우선순위: custom > template_id > default

✅ **/ask 아티팩트 마크다운 파싱 수정**
- 문제: Claude 응답 전체가 artifact로 저장됨
- 해결: parse_markdown_to_content() + build_report_md() 적용
- /generate와 /ask의 일관성 확보

✅ **테스트 추가**
- /ask 마크다운 파싱 3개 신규 테스트
- 전체 topics 테스트 28/28 통과 (100%)
- topics.py 커버리지 39% → 78%

### v2.1 (2025-11-04) - 프롬프트 통합

✅ **System Prompt 중앙 관리** (utils/prompts.py)
- FINANCIAL_REPORT_SYSTEM_PROMPT 상수화
- create_dynamic_system_prompt() 함수
- create_topic_context_message() 함수

✅ **동적 섹션 추출** (markdown_parser.py)
- H2 섹션 자동 분류 (요약, 배경, 주요내용, 결론)
- 동적 제목 추출 (title_summary, title_background, ...)
- 키워드 우선순위 조정

✅ **ClaudeClient 반환 타입 변경**
- Dict[str, str] → str (Markdown만 반환)
- 파싱 책임을 호출자로 이전 (관심사 분리)

### v2.0 (2025-10-31) - 대화형 시스템

✅ **Topics + Messages 아키텍처**
- 단일 요청 → 대화형 시스템 (토픽 스레드)
- 메시지 seq_no 기반 순서 관리
- 컨텍스트 유지 (이전 메시지 참조)

✅ **Artifacts 버전 관리**
- MD (Markdown), HWPX, PDF 지원
- 버전 번호로 변경사항 추적
- Transformation 이력 (MD→HWPX 변환)

✅ **API 표준화**
- success_response(), error_response() 헬퍼
- ErrorCode 클래스 (DOMAIN.DETAIL 형식)
- 모든 엔드포인트 100% 준수

---

## 개발 체크리스트 (백엔드)

### ✅ Step 0: Unit Spec 작성 (필수, 가장 먼저)

**이 단계를 완료하지 않으면 다음 단계로 진행할 수 없습니다.**

```
사용자 요청
    ↓
Claude: Unit Spec 작성
    ↓
[생성 위치] backend/doc/specs/YYYYMMDD_feature_name.md
[템플릿] backend/doc/Backend_UnitSpec.md
    ↓
사용자: 스펙 검토 및 승인
    ↓
승인 ✅ → Step 1로 진행
또는
수정 요청 → 스펙 수정 후 재제출
```

**Unit Spec에 포함되어야 할 항목:**
- [ ] 요구사항 요약 (Purpose, Type, Core Requirements)
- [ ] 구현 대상 파일 (New/Change/Reference)
- [ ] 흐름도 (Mermaid)
- [ ] 테스트 계획 (최소 3개 이상 TC)
- [ ] 에러 처리 시나리오

---

### ✅ Step 1: 구현 (Unit Spec 승인 후)

**Step 0의 승인을 받았을 때만 진행**

#### 1-1. 데이터 모델 정의
- [ ] Pydantic 모델 정의 (`models/*.py`)
- [ ] 필드 타입 힌트 완벽
- [ ] 선택/필수 필드 명확히

#### 1-2. 데이터베이스 로직
- [ ] DB CRUD 메서드 구현 (`database/*.py`)
- [ ] 트랜잭션 처리 (필요시)
- [ ] SQL 쿼리 파라미터화 (SQL Injection 방지)
- [ ] 인덱스 고려

#### 1-3. 라우터/API 구현
- [ ] 라우터 함수 구현 (`routers/*.py`)
- [ ] API 응답: **반드시** `success_response()` / `error_response()` 사용
- [ ] 에러 코드: **반드시** `ErrorCode` 상수 사용
- [ ] HTTP 상태 코드 정확히

#### 1-4. 로깅 및 문서화
- [ ] 로깅 추가 (`logger.info()`, `logger.warning()`, `logger.error()`)
- [ ] DocString 작성 (Google 스타일, 모든 함수)
- [ ] 파라미터, 반환값, 예외 명시

#### 1-5. 테스트 작성
- [ ] 테스트 작성 (`tests/test_*.py`)
- [ ] Unit Spec의 모든 TC 구현
- [ ] 성공 케이스 + 에러 케이스 모두
- [ ] 모든 테스트 **반드시 통과**

---

### ✅ Step 2: 검증 및 최종 확인 (구현 후)

#### 2-1. 기존 코드 영향 확인
- [ ] 기존 테스트 실행 (새 에러 없는지 확인)
- [ ] 호환성 검증 (breaking change 없는지)
- [ ] 의존성 충돌 확인

#### 2-2. 문서 업데이트
- [ ] CLAUDE.md 업데이트 (새 엔드포인트, 모델, DB 등)
- [ ] 필요시 README.md 업데이트

#### 2-3. 깃 커밋
- [ ] Unit Spec 문서 포함 (`backend/doc/specs/YYYYMMDD_*.md`)
- [ ] 깃 커밋 메시지: feat/fix/refactor 명확히
- [ ] 커밋 메시지에 Unit Spec 파일 명시

---

### 🚫 주의사항

**다음은 절대 하면 안 됨:**
- ❌ Unit Spec 없이 코드 작성 시작
- ❌ Unit Spec 미승인 상태에서 구현
- ❌ 승인된 Spec에서 임의로 변경
- ❌ 테스트 없이 구현 완료했다고 간주
- ❌ HTTPException 직접 사용 (response_helper 사용)
- ❌ 에러 코드 하드코딩 (ErrorCode 상수 사용)

---

### 버그 수정 / 리팩토링 시

**중요: 규모가 작아도 Unit Spec 필수**

- [ ] Unit Spec 작성 (버그/리팩토링 계획)
- [ ] 사용자 승인 (큰 변경사항일 경우)
- [ ] 기존 테스트 확인 (모두 통과해야 함)
- [ ] 새 테스트 추가 (버그 재발 방지)
- [ ] CLAUDE.md 업데이트

---

## 참고 자료

- `backend/CLAUDE.md` - 백엔드 개발 가이드라인 (DocString, 파일 관리)
- `backend/BACKEND_TEST.md` - 테스트 작성 가이드
- `backend/doc/Backend_UnitSpec.md` - Unit Spec 템플릿
- `backend/doc/specs/` - 구현된 스펙 문서들
- `backend/doc/07.PromptIntegrate.md` - 프롬프트 통합 가이드
- `backend/doc/04.messageChaining.md` - 메시지 체이닝 설계

---

**마지막 업데이트:** 2025-11-10
**버전:** 2.3
**상태:** ✅ 완전 분석 및 문서화 완료
