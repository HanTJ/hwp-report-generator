# 커스텀 템플릿 실행 계획

이 문서는 기존 백엔드에 “템플릿 기반” 보고서 생성을 추가하기 위한 최소·정확 변경사항을 5가지 요구사항에 맞춰 정리합니다.

## 목표(Goals)
- 사용자 입력으로 템플릿(HWPX + 플레이스홀더)과 주제를 함께 받아 처리
- 템플릿의 플레이스홀더를 기반으로 시스템 프롬프트 동적 생성
- 해당 시스템 프롬프트와 토픽 기반 메시지로 Claude에 질의
- 응답을 Markdown으로 저장하고 사용량/아티팩트 관리
- 선택한 템플릿으로 MD → HWPX 변환 시 플레이스홀더 치환

## 비범위(Non-Goals)
- 프론트엔드 구현
- PDF 생성 또는 추가 웹검색 도구 확장(현 지원 범위 외)

## 현행 기능 요약(Backend)
- 템플릿 업로드/검증/플레이스홀더 추출: `backend/app/routers/templates.py`, `backend/app/utils/templates_manager.py`
- 시스템 프롬프트 주입 가능한 Claude 클라이언트: `backend/app/utils/claude_client.py`
- 토픽/메시지/MD 아티팩트 생성 흐름: `backend/app/routers/topics.py`
- Markdown → content dict 파싱: `backend/app/utils/markdown_parser.py`
- MD → HWPX 변환(HWPX 템플릿 사용 + 플레이스홀더 치환): `backend/app/utils/hwp_handler.py`, 사용처 `backend/app/routers/artifacts.py`

## 상위 흐름(High-Level Flow)
1) 사용자가 `template_id`와 `topic`(및 선택적 질문)을 제공
2) 백엔드가 템플릿 플레이스홀더를 조회하고, 해당 구조에 맞는 시스템 프롬프트를 동적으로 생성
3) 토픽 컨텍스트 + 사용자 메시지로 Claude에 `chat_completion()` 호출(커스텀 시스템 프롬프트 적용)
4) 응답을 MD 아티팩트로 저장(현행 유지)
5) 선택 템플릿 경로를 사용해 MD 아티팩트를 HWPX로 변환(고정 템플릿 사용 탈피)
6) 필요 시 변환 이력(MD→HWPX)을 `TransformationDB`에 기록(권장)

## API 변경사항
1) Ask API가 템플릿을 받도록 확장
- 모델: `backend/app/models/message.py`
  - `AskRequest`에 `template_id: Optional[int]` 필드 추가
- 라우터: `backend/app/routers/topics.py` (`@router.post("/{topic_id}/ask")`)
  - `template_id`가 존재하면:
    - `TemplateDB.get_template_by_id(template_id, current_user.id)`로 템플릿 로드(소유권 검증 포함)
    - `PlaceholderDB.get_placeholders_by_template(template.id)`로 플레이스홀더 로드
    - “시스템 프롬프트 빌더”로 동적 시스템 프롬프트 생성
    - `ClaudeClient.chat_completion()` 호출 시 디폴트 대신 해당 프롬프트 사용
  - 사용자/어시스턴트 메시지 및 MD 아티팩트 저장은 현행 유지

2) 선택: 통합 엔드포인트(질문+저장+변환)
- `POST /api/topics/{topic_id}/generate-from-template`
- Body: `{ content: string, template_id: number, include_artifact_content?: boolean, max_messages?: number }`
- Ask 흐름(템플릿 시스템 프롬프트 적용) 완료 후, MD→HWPX 변환까지 수행해 두 아티팩트 id 반환
  - 변환은 별도 다운로드 엔드포인트를 계속 사용해도 무방

## 시스템 프롬프트 빌더
플레이스홀더 배열로부터 지침형 프롬프트를 생성하는 유틸 추가

- 신규 모듈: `backend/app/utils/prompt_builder.py`
  - `build_system_prompt_from_placeholders(keys: list[str]) -> str`
  - 동작:
    - 템플릿에 존재하는 표준 키(TITLE/H1, SUMMARY/BACKGROUND/MAIN_CONTENT/CONCLUSION/H2)에 맞춰 Markdown 섹션을 요구
    - 누락/추가(커스텀) 키가 있으면 주제에 맞는 제목으로 H2/H3 섹션을 만들어 채우도록 지시
    - 프롬프트는 “순수 지침”만 포함(토픽 텍스트 삽입 금지)

예시 지침 스켈레톤:

```
당신은 금융 기관의 전문 보고서 작성자입니다.

출력은 반드시 Markdown 형식으로 작성하세요:
- H1: {TITLE}
- H2: {SUMMARY}, {BACKGROUND}, {MAIN_CONTENT}, {CONCLUSION} (템플릿에 존재하는 경우만)
- 템플릿에 존재하는 기타 플레이스홀더는 적절한 섹션 제목을 붙여 반영하세요.

문체는 격식 있고 명확하게. 금융 용어와 데이터를 적절히 사용하세요. 위 섹션 범위를 벗어나지 마세요.
```

## HWPX 변환 시 템플릿 사용
사용자 선택 템플릿을 우선 사용하도록 변환 로직을 보강

- 파일: `backend/app/routers/artifacts.py`
  - `download_message_hwpx`(또는 신규 통합 엔드포인트)에서 사용할 템플릿을 결정:
    - 우선순위: 요청 파라미터의 `template_id` → 없으면 기존 고정 템플릿으로 폴백
    - `TemplateDB.get_template_by_id`로 `template.file_path` 확보 후 `HWPHandler(template_path=...)`에 주입
  - MD → content dict 파싱(`parse_markdown_to_content`) 및 플레이스홀더 치환은 현행 유지
  - `TransformationDB.create_transformation`으로 변환 이력을 저장(작업=CONVERT, `params_json`에 template id/sha256 기입)

## 검증 및 권한
- `template_id` 소유권 검증 필수(현재 사용자 보유 템플릿만 사용)
- 업로드 시 중복 플레이스홀더 방지는 이미 구현됨; 빈/누락 키도 안전하게 처리
- 과도한 컨텍스트 크기 제한은 Ask에 이미 구현되어 있음

## 오류 처리
- 잘못된/존재하지 않는 `template_id` → `TEMPLATE.NOT_FOUND`(기존 패턴 재사용)
- 템플릿 파일 불존재 → 변환 오류와 `template_path` 힌트 반환
- Claude API 실패 → Ask에서 `SERVER_SERVICE_UNAVAILABLE` 처리 유지

## 보안
- 템플릿/토픽 소유권 엄격 검증
- 파일 경로는 DB에 저장된 `file_path`만 사용(임의 경로 금지)

## 성능 고려
- 프롬프트 빌더는 플레이스홀더 개수에 선형(O(n))
- 변환은 현행 임시/아티팩트 디렉터리 재사용(변경 없음)
- 컨텍스트 크기 제한은 그대로 적용

## 텔레메트리
- AI 사용량 추적(`AiUsageDB`) 재사용
- (권장) 변환 이력(라인리지) 기록(`TransformationDB`)

## 테스트 계획
1) 단위(Unit)
- 프롬프트 빌더:
  - 표준 플레이스홀더 제공 시 H1/H2 지침 포함
  - 추가 플레이스홀더 제공 시 추가 섹션 생성 지침 포함
- 템플릿 적용 Ask:
  - `template_id` 제공 시 커스텀 프롬프트 사용 여부(클라이언트 호출 파라미터 스파이)
- 아티팩트 변환:
  - `download_message_hwpx`가 제공된 템플릿 경로를 사용하고 파일이 존재하면 변환 성공

2) 통합(Integration)
- E2E: 토픽 생성 → 템플릿 지정 Ask → MD 저장 → 변환 → HWPX 다운로드
- 권한: 다른 사용자의 템플릿 사용 시 실패

3) 회귀(Regression)
- `template_id` 미제공 시 기존 디폴트 프롬프트로 정상 동작
- 변환 시 템플릿 미지정일 때 기존 고정 템플릿 경로 사용 유지

## 마이그레이션/호환성
- DB 스키마(templates/placeholders, artifacts, transformations) 이미 존재
- 스키마 변경 불필요
- 하위 호환: `template_id`는 선택 필드

## 롤아웃 단계
1) 프롬프트 빌더 유틸 구현
2) `AskRequest`에 `template_id`(optional) 추가 및 Topics 라우터 연계
3) Artifacts 라우터에서 템플릿 인지 변환 추가(또는 통합 엔드포인트 신설)
4) 단위/통합 테스트 추가
5) 기존 `tests/test_prompt_integration.py` + 신규 테스트로 로컬 검증

## 파일 변경 요약(타깃)
- 추가: `backend/app/utils/prompt_builder.py`(신규)
- 수정: `backend/app/models/message.py`(AskRequest에 `template_id` 추가)
- 수정: `backend/app/routers/topics.py`(플레이스홀더 로드 → 시스템 프롬프트 동적 생성 적용)
- 수정: `backend/app/routers/artifacts.py`(선택 템플릿을 사용한 HWPX 변환; 필요 시 신규 엔드포인트)
- 선택: `backend/app/database/transformation_db.py`로 변환 이력 기록

## 오픈 이슈(Open Questions)
- Ask 직후 자동으로 MD→HWPX 변환을 수행할지, 아니면 다운로드 시점에 온디맨드로 유지할지?
- 템플릿 플레이스홀더가 표준 세트와 다를 경우, 최소 세트(TITLE/SUMMARY 등)를 강제할지, 아니면 자유 형식으로 우선 매핑할지?
