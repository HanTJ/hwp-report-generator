# Serena MCP 연동 가이드

이 문서는 현재 리포지토리에 포함된 `.serena/project.yml`을 기반으로 Serena MCP 서버를 연결하는 방법을 정리합니다. 사용 중인 MCP 클라이언트(예: Codex CLI, Claude Desktop 등)에 서버를 등록하면, 프로젝트 컨텍스트를 활용한 코드 탐색/편집 도구를 사용할 수 있습니다.

## 1) 사전 확인

- 프로젝트 루트에 `.serena/project.yml` 존재: 확인됨
- Python 3.12+ 설치(리포지토리 개발용)
- Serena CLI 설치(또는 npx로 실행)

> Serena CLI 설치/명령은 사용하는 배포에 따라 다를 수 있습니다. 조직 문서 또는 Serena 공식 안내에 따라 설치하세요. 일반적으로는 `serena` 바이너리를 설치하거나, Node 기반이면 `npx serena ...`와 같이 사용할 수 있습니다.

## 2) 서버 실행 커맨드 예시

표준 MCP는 stdio 기반 서버로 실행합니다. 아래 중 하나를 사용하세요.

```
# 설치형 (예: 전역 설치된 serena 바이너리)
serena mcp --project "D:\\WorkSpace\\hwp-report\\hwp-report-generator"

# npx (Node 기반 배포일 경우 예시)
npx -y serena mcp --project "D:\\WorkSpace\\hwp-report\\hwp-report-generator"
```

프로젝트 경로는 실제 리포지토리 루트로 바꿔주세요.

## 3) MCP 클라이언트 설정 예시

### 3-1) Claude Desktop (Windows/macOS/Linux)

`%UserProfile%/.config/claude/mcp.json`(Windows) 또는 `~/.config/claude/mcp.json`(macOS/Linux)에 아래를 추가합니다.

```json
{
  "mcpServers": {
    "serena": {
      "command": "serena",
      "args": ["mcp", "--project", "D:\\WorkSpace\\hwp-report\\hwp-report-generator"],
      "env": {
        "SERENA_PROJECT_DIR": "D:\\WorkSpace\\hwp-report\\hwp-report-generator"
      }
    }
  }
}
```

설정 후 Claude를 재시작하고, 도구 목록에서 `serena`가 보이는지 확인합니다.

### 3-2) Codex CLI

Codex CLI가 MCP 구성을 지원한다면(최신 버전 기준), 동일한 포맷의 설정 파일을 참조하거나 CLI 설정에 MCP 서버를 등록할 수 있습니다. 예시 파일 `.mcp/serena.mcp.json.example`를 제공하니, 사용하는 Codex CLI의 MCP 설정 경로에 맞춰 복사/수정하세요.

## 4) 동작 확인

클라이언트에서 Serena MCP가 연결되면 다음과 같은 도구가 노출됩니다(프로젝트에 포함된 `.serena/project.yml` 기준):

- `list_dir`, `read_file`, `insert_at_line`, `replace_lines`, `find_symbol`, `search_for_pattern` 등

간단한 점검 시나리오:

1. `list_dir`로 `backend/app/routers` 목록 조회
2. `read_file`로 `backend/app/routers/topics.py` 일부 읽기
3. (선택) 별도의 브랜치에서 테스트용 변경(`insert_at_line`) 후 되돌리기

## 5) 문제 해결

- serena 명령을 찾을 수 없음: Serena CLI 설치 또는 `npx serena ...` 사용
- 권한 문제(Windows PowerShell): `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 후 재시도
- 프로젝트 경로 인식 문제: `--project`에 리포지토리 루트를 정확히 지정했는지 확인
- 클라이언트에 서버가 안 보임: 설정 파일 경로/포맷 확인 후 클라이언트 재시작

---

추가로, 필요하시면 현재 환경(Claude Desktop, Codex CLI 등)에 맞춘 정확한 MCP 설정 파일을 만들어 드릴 수 있습니다. 사용 중인 클라이언트를 알려주세요.

