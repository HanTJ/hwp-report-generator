# Prompt 통합 테스트 가이드

이 디렉토리는 **07.PromptIntegrate.md** 계획에 따라 구현된 Prompt 통합 기능을 테스트하기 위한 파일들을 포함합니다.

---

## 📁 테스트 파일 구성

### 1. `test_prompt_integration.py` (단위 테스트)
pytest 기반의 자동화된 단위 테스트 파일입니다.

**실행 방법:**
```bash
cd backend
uv run pytest tests/test_prompt_integration.py -v
```

**포함된 테스트:**
- `TestPrompts`: System prompt 정의 및 구조 검증
- `TestMarkdownParser`: Markdown 파싱 로직 검증
- `TestMessageConstruction`: Message 배열 구성 검증
- `TestIntegration`: End-to-End 통합 테스트

**예상 결과:**
```
tests/test_prompt_integration.py::TestPrompts::test_system_prompt_exists PASSED
tests/test_prompt_integration.py::TestPrompts::test_create_topic_context_message PASSED
tests/test_prompt_integration.py::TestMarkdownParser::test_parse_markdown_basic PASSED
...
======================== 20 passed in 0.5s ========================
```

---

### 2. `manual_test_prompt_integration.py` (수동 테스트)
개발자가 직접 실행하여 각 기능의 동작을 확인할 수 있는 스크립트입니다.

**실행 방법:**
```bash
cd backend
uv run python tests/manual_test_prompt_integration.py
```

**포함된 테스트:**
1. Topic Context Message 생성
2. Messages 배열 구성
3. Markdown 파싱 (한글 섹션)
4. Markdown 파싱 (영문 섹션)
5. System Prompt 순수성 검증
6. 복잡한 Markdown 파싱

**예상 출력:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Prompt 통합 기능 수동 테스트                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
  TEST 1: Topic Context Message 생성
================================================================================

[입력] Topic: 디지털뱅킹 트렌드

[출력] Message:
  Role: user
  Content:
**대화 주제**: 디지털뱅킹 트렌드

이전 메시지들을 문맥으로 활용하여 일관된 문체와 구조로 답변하세요.

✅ 테스트 통과: Topic Context Message가 올바르게 생성되었습니다.

...

╔══════════════════════════════════════════════════════════════════════════════╗
║                              테스트 결과                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  총 테스트: 6개                                                              ║
║  통과: 6개 ✅                                                                ║
║  실패: 0개 ❌                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎉 모든 테스트가 성공적으로 통과했습니다!
```

---

### 3. `verify_prompt_integration.py` (검증 스크립트)
구현이 계획대로 완료되었는지 자동으로 검증하는 스크립트입니다.

**실행 방법:**
```bash
cd backend
uv run python tests/verify_prompt_integration.py
```

**검증 항목:**
1. 하드코딩된 Prompt 제거 확인
2. Import 확인
3. 파일 구조 확인
4. Markdown Parser 함수 확인
5. Prompts 모듈 확인
6. Claude Client 변경사항 확인
7. Topics Router 변경사항 확인

**예상 출력:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Prompt 통합 검증                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
  1. 하드코딩된 Prompt 제거 확인
================================================================================

✅ app/utils/claude_client.py - 하드코딩 없음
✅ app/routers/topics.py - 하드코딩 없음
✅ app/main.py - 하드코딩 없음

✅ 하드코딩된 prompt가 모두 제거되었습니다.

...

================================================================================
  검증 결과 요약
================================================================================

✅ 통과 - 하드코딩 제거
✅ 통과 - Import 확인
✅ 통과 - 파일 구조
✅ 통과 - Markdown Parser
✅ 통과 - Prompts 모듈
✅ 통과 - Claude Client
✅ 통과 - Topics Router

--------------------------------------------------------------------------------

총 7개 항목 중 7개 통과

🎉 모든 검증 항목을 통과했습니다!
Prompt 통합이 성공적으로 완료되었습니다.
```

---

## 🧪 테스트 실행 순서 (권장)

### 1단계: 검증 스크립트 실행
먼저 구현이 올바르게 완료되었는지 확인합니다.

```bash
cd backend
uv run python tests/verify_prompt_integration.py
```

✅ **결과:** 모든 항목이 통과하면 다음 단계로 진행합니다.

---

### 2단계: 단위 테스트 실행
자동화된 단위 테스트를 실행하여 각 함수가 정상 동작하는지 확인합니다.

```bash
cd backend
uv run pytest tests/test_prompt_integration.py -v
```

✅ **결과:** 모든 테스트가 PASSED이면 다음 단계로 진행합니다.

---

### 3단계: 수동 테스트 실행
실제 동작을 눈으로 확인합니다.

```bash
cd backend
uv run python tests/manual_test_prompt_integration.py
```

✅ **결과:** 각 테스트의 출력을 확인하고, 예상대로 동작하는지 검증합니다.

---

## 🚀 End-to-End 테스트 (선택)

실제 Claude API를 호출하여 전체 흐름을 테스트하려면:

```bash
cd backend
uv run python -c "
from app.utils.claude_client import ClaudeClient
from app.utils.prompts import FINANCIAL_REPORT_SYSTEM_PROMPT, create_topic_context_message
from app.utils.markdown_parser import parse_markdown_to_content

# 1. Claude API 호출
client = ClaudeClient()
topic = '2025 디지털뱅킹 트렌드'
md_content = client.generate_report(topic)

# 2. Markdown 파싱
content = parse_markdown_to_content(md_content)

# 3. 결과 출력
print('=== 생성된 제목 ===')
print(content['title'])
print()
print('=== 섹션 제목들 ===')
print(f\"요약: {content['title_summary']}\")
print(f\"배경: {content['title_background']}\")
print(f\"주요내용: {content['title_main_content']}\")
print(f\"결론: {content['title_conclusion']}\")
print()
print('=== 요약 (앞 100자) ===')
print(content['summary'][:100])
"
```

⚠️ **주의:** 이 테스트는 실제 Claude API를 호출하므로 API 키가 설정되어 있어야 하며, 토큰이 소비됩니다.

---

## 📋 테스트 체크리스트

구현 후 다음 항목들을 확인하세요:

### ✅ 파일 생성/수정
- [ ] `backend/app/utils/prompts.py` 생성됨
- [ ] `backend/app/utils/markdown_parser.py` 전체 교체됨
- [ ] `backend/app/utils/claude_client.py` 수정됨
- [ ] `backend/app/routers/topics.py` 수정됨
- [ ] `backend/app/main.py` 수정됨

### ✅ Import 확인
- [ ] `claude_client.py`에서 `FINANCIAL_REPORT_SYSTEM_PROMPT` import
- [ ] `topics.py`에서 `FINANCIAL_REPORT_SYSTEM_PROMPT, create_topic_context_message` import
- [ ] `topics.py`에서 `parse_markdown_to_content` import
- [ ] `main.py`에서 `parse_markdown_to_content` import

### ✅ 핵심 변경사항
- [ ] `generate_report()` 메서드가 `str` (Markdown) 반환
- [ ] `_parse_report_content()` 메서드 삭제됨
- [ ] System prompt가 순수하게 지침만 포함
- [ ] Topic context가 message로 추가됨
- [ ] Markdown 파싱이 동적 섹션 제목을 추출함

### ✅ 테스트 통과
- [ ] `verify_prompt_integration.py` 모든 항목 통과
- [ ] `test_prompt_integration.py` 모든 테스트 PASSED
- [ ] `manual_test_prompt_integration.py` 모든 테스트 통과

---

## 🐛 트러블슈팅

### 문제 1: Import 에러
```
ImportError: cannot import name 'FINANCIAL_REPORT_SYSTEM_PROMPT'
```

**해결:**
- `backend/app/utils/prompts.py` 파일이 존재하는지 확인
- Import 경로가 `from app.utils.prompts import ...`인지 확인

---

### 문제 2: 테스트 실패 (섹션 분류)
```
AssertionError: classify_section("핵심 요약") != "summary"
```

**해결:**
- `markdown_parser.py`의 `classify_section()` 함수 확인
- 키워드 목록에 해당 단어가 포함되어 있는지 확인

---

### 문제 3: Claude API 에러
```
Exception: Claude API 호출 중 오류 발생
```

**해결:**
- `.env` 파일에 `CLAUDE_API_KEY`가 설정되어 있는지 확인
- API 키가 유효한지 확인
- 인터넷 연결 상태 확인

---

## 📚 참고 문서

- **구현 계획:** `backend/doc/07.PromptIntegrate.md`
- **프로젝트 가이드:** `CLAUDE.md`
- **백엔드 가이드:** `backend/CLAUDE.md`

---

## ✅ 최종 확인

모든 테스트가 통과하면:

1. ✅ `verify_prompt_integration.py` 실행 → 모든 항목 통과
2. ✅ `pytest test_prompt_integration.py` 실행 → 모든 테스트 PASSED
3. ✅ `manual_test_prompt_integration.py` 실행 → 모든 테스트 통과

**🎉 Prompt 통합이 성공적으로 완료되었습니다!**

---

**작성일:** 2025-01-03
**버전:** 1.0
