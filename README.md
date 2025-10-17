# HWP 보고서 자동 생성 시스템

Claude AI를 활용하여 금융 업무보고서를 자동으로 생성하는 웹 시스템입니다.

## 주요 기능

- **AI 기반 보고서 생성**: 주제만 입력하면 Claude AI가 전문적인 금융 보고서 내용 자동 생성
- **HWP 형식 지원**: 한글 프로그램(HWPX) 형식으로 보고서 출력
- **웹 기반 인터페이스**: 간단하고 직관적인 웹 UI
- **보고서 관리**: 생성된 보고서 목록 조회 및 다운로드

## 기술 스택

- **Backend**: FastAPI (Python 3.12)
- **Package Manager**: uv (권장) 또는 pip
- **AI**: Claude API (Anthropic) - anthropic==0.71.0
- **HWP 처리**: zipfile, xml.etree.ElementTree, olefile
- **템플릿 엔진**: Jinja2 (웹 UI)
- **Frontend**: HTML, CSS, JavaScript

## 설치 방법

### 1. 저장소 클론 (또는 프로젝트 디렉토리 생성)

```bash
cd hwp-report-generator
```

### 2. Python 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 3. 필요한 패키지 설치

**uv 사용 (권장):**
```bash
# uv로 패키지 설치
uv pip install -r requirements.txt
```

**pip 사용:**
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일을 생성하고 Claude API 키를 설정합니다:

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

`.env` 파일을 열고 API 키를 입력:

```
CLAUDE_API_KEY=your_actual_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

> **중요**: Claude API 키는 [Anthropic Console](https://console.anthropic.com/)에서 발급받을 수 있습니다.

## 실행 방법

### 개발 서버 실행

**uv 사용 (권장):**
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**표준 Python 사용:**
```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 브라우저에서 다음 주소로 접속:

```
http://localhost:8000       # 메인 UI
http://localhost:8000/docs  # API 문서 (Swagger UI)
```

## 사용 방법

### 1. 보고서 생성

1. 웹 브라우저에서 `http://localhost:8000` 접속
2. "보고서 주제" 입력란에 원하는 주제 입력
   - 예: "2024년 디지털 뱅킹 서비스 현황 분석"
   - 예: "핀테크 산업 동향 및 은행권 대응 방안"
3. "보고서 생성" 버튼 클릭
4. 생성 완료 후 자동으로 다운로드 링크 표시

### 2. 생성된 보고서 확인

- 하단의 "생성된 보고서 목록"에서 이전에 생성한 보고서 확인 가능
- 각 보고서의 다운로드 버튼을 클릭하여 다운로드

### 3. HWP 파일 열기

- 생성된 `.hwpx` 파일은 한글 프로그램 또는 호환 프로그램에서 열 수 있습니다
- LibreOffice 등 일부 오픈소스 프로그램에서도 열람 가능

## 프로젝트 구조

```
hwp-report-generator/
├── main.py                    # FastAPI 메인 애플리케이션
├── requirements.txt           # Python 패키지 의존성
├── .env                       # 환경 변수 (API 키)
├── .env.example              # 환경 변수 템플릿
├── .gitignore                # Git 제외 파일 목록
├── README.md                 # 프로젝트 문서
├── CLAUDE.md                 # Claude Code 가이드
├── utils/
│   ├── __init__.py
│   ├── claude_client.py      # Claude API 클라이언트
│   └── hwp_handler.py        # HWPX 파일 처리
├── templates/
│   ├── index.html            # 웹 UI
│   └── report_template.hwpx  # HWP 템플릿 (자동 생성)
├── static/
│   ├── style.css             # 스타일시트
│   └── script.js             # 프론트엔드 로직
├── output/                   # 생성된 보고서 저장
│   └── .gitkeep
└── temp/                     # 임시 파일 처리
    └── .gitkeep
```

## API 엔드포인트

### `GET /`
메인 페이지 (웹 UI)

### `POST /api/generate`
보고서 생성

**Request Body:**
```json
{
  "topic": "보고서 주제"
}
```

**Response:**
```json
{
  "success": true,
  "message": "보고서가 성공적으로 생성되었습니다.",
  "file_path": "output/report_20240117_123456.hwpx",
  "filename": "report_20240117_123456.hwpx"
}
```

### `GET /api/download/{filename}`
생성된 보고서 다운로드

### `GET /api/reports`
생성된 보고서 목록 조회

### `GET /health`
서버 상태 확인

## HWP 템플릿 커스터마이징

기본 템플릿이 자동으로 생성되지만, 커스텀 템플릿을 사용하려면:

1. 한글 프로그램에서 보고서 양식 작성
2. 다음 플레이스홀더를 원하는 위치에 삽입:
   - `{{TITLE}}` - 제목
   - `{{SUMMARY}}` - 요약
   - `{{BACKGROUND}}` - 배경 및 목적
   - `{{MAIN_CONTENT}}` - 주요 내용
   - `{{CONCLUSION}}` - 결론 및 제언
   - `{{DATE}}` - 작성일자

3. "다른 이름으로 저장" → "HWPX 파일" 선택
4. `templates/report_template.hwpx`로 저장

## 문제 해결

### API 키 오류
```
ValueError: CLAUDE_API_KEY 환경 변수가 설정되지 않았습니다.
```
**해결**: `.env` 파일에 올바른 API 키가 설정되어 있는지 확인

### 템플릿 파일 오류
```
FileNotFoundError: 템플릿 파일을 찾을 수 없습니다
```
**해결**: 프로그램이 자동으로 기본 템플릿을 생성합니다. 문제가 지속되면 `templates/` 디렉토리가 존재하는지 확인

### 포트 충돌
```
OSError: [Errno 98] Address already in use
```
**해결**: 8000 포트가 이미 사용 중입니다. 다른 포트를 사용하려면:
```bash
uvicorn main:app --reload --port 8080
```

## 보안 주의사항

- `.env` 파일을 절대 Git에 커밋하지 마세요
- API 키는 안전하게 보관하세요
- 프로덕션 환경에서는 적절한 인증/권한 관리를 추가하세요

## 향후 개선 계획

- [ ] 여러 보고서 템플릿 선택 기능
- [ ] 보고서 히스토리 및 버전 관리
- [ ] 사용자 인증 및 권한 관리
- [ ] 보고서 스타일 커스터마이징
- [ ] PDF 변환 기능
- [ ] 단위 테스트 추가

## 라이선스

MIT License

## 문의 및 기여

이슈나 개선 제안이 있으시면 언제든지 연락주세요.
