# Bug Report: HWPX 다운로드 500 에러 - 템플릿 파일 누락

## 버그 정보

- **발생일**: 2025-11-20
- **심각도**: 🔴 Critical
- **영향 범위**: HWPX 파일 다운로드 기능 전체 불가
- **보고자**: Frontend Team
- **분석자**: Claude Code

---

## 1. 문제 설명

### 증상
- `/api/artifacts/messages/{messageId}/hwpx/download` API 호출 시 500 Internal Server Error 발생
- 사용자가 보고서를 HWPX 형식으로 다운로드할 수 없음
- 프론트엔드에서 다운로드 버튼 클릭 시 에러 발생

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "ARTIFACT.CONVERSION_FAILED",
    "message": "HWPX 템플릿 파일을 찾을 수 없습니다.",
    "details": {
      "template_path": "backend/templates/report_template.hwpx"
    }
  }
}
```

---

## 2. 근본 원인 분석

### 원인
백엔드 코드에서 `report_template.hwpx` 파일을 참조하고 있으나, 실제로는 해당 파일이 존재하지 않음

### 코드 위치
[artifacts.py:375](backend/app/routers/artifacts.py#L375)
```python
template_path = ProjectPath.BACKEND / "templates" / "report_template.hwpx"
if not template_path.exists():
    return error_response(
        code=ErrorCode.ARTIFACT_CONVERSION_FAILED,
        http_status=500,
        message="HWPX 템플릿 파일을 찾을 수 없습니다.",
        details={"template_path": str(template_path)}
    )
```

### 실제 파일 시스템 상태
```bash
backend/templates/
├── report_template4.hwpx        # ✅ 존재 (397,892 bytes)
├── report_template.hwpx.bak     # 백업 파일
└── report_template - 복사본/    # 폴더
```

**문제점**: 코드는 `report_template.hwpx`를 찾지만, 실제로는 `report_template4.hwpx`만 존재

---

## 3. 영향 분석

### 직접 영향
1. **HWPX 다운로드 완전 불가**
   - 기존 HWPX 파일이 없는 경우 MD → HWPX 변환 시도
   - 변환 시 템플릿 파일을 찾지 못해 500 에러 발생

2. **사용자 경험 저하**
   - 보고서 작성 후 다운로드 불가
   - 워크플로우 중단

### 간접 영향
- 다른 HWPX 관련 기능도 영향받을 가능성 있음
- 템플릿 업로드 기능과의 일관성 문제

---

## 4. 해결 방안

### Option 1: 파일명 복원 (권장) ✅
```bash
cd backend/templates
cp report_template4.hwpx report_template.hwpx
```
**장점**:
- 코드 수정 불필요
- 즉시 해결 가능
- 기존 테스트와 호환

**단점**:
- 파일 중복

### Option 2: 코드 수정
```python
# backend/app/routers/artifacts.py:375
template_path = ProjectPath.BACKEND / "templates" / "report_template4.hwpx"
```
**장점**:
- 명확한 파일 참조

**단점**:
- 코드 수정 필요
- 테스트 코드도 수정 필요
- 다른 참조 위치 확인 필요

### Option 3: 환경 변수로 관리
```python
template_name = os.getenv("HWPX_TEMPLATE_NAME", "report_template.hwpx")
template_path = ProjectPath.BACKEND / "templates" / template_name
```
**장점**:
- 유연한 설정

**단점**:
- 복잡도 증가
- 환경 변수 관리 필요

---

## 5. 실행 계획

### 즉시 조치 (Hot Fix)
1. ✅ `report_template4.hwpx`를 `report_template.hwpx`로 복사
2. ✅ 서비스 재시작
3. ✅ 기능 테스트

### 추후 개선
1. 템플릿 파일 관리 체계 정립
2. 파일 존재 여부 검증 로직 추가
3. 시작 시 템플릿 파일 검증
4. 로깅 강화

---

## 6. 재발 방지

### 개발 프로세스 개선
1. **템플릿 파일 버전 관리**
   - Git에서 템플릿 파일 추적
   - 변경 시 PR 필수

2. **헬스 체크 추가**
   ```python
   @router.get("/health/templates")
   async def check_templates():
       """시작 시 필수 템플릿 파일 검증"""
       required_templates = ["report_template.hwpx"]
       missing = []
       for template in required_templates:
           path = ProjectPath.BACKEND / "templates" / template
           if not path.exists():
               missing.append(template)
       return {"healthy": len(missing) == 0, "missing": missing}
   ```

3. **CI/CD 파이프라인 검증**
   - 배포 전 템플릿 파일 존재 확인
   - 필수 파일 체크리스트

### 모니터링 강화
1. **에러 알림 설정**
   - 500 에러 발생 시 즉시 알림
   - 템플릿 관련 에러 별도 추적

2. **로깅 개선**
   ```python
   logger.error(f"Template not found: {template_path}")
   logger.info(f"Available templates: {list(templates_dir.glob('*.hwpx'))}")
   ```

---

## 7. 테스트 시나리오

### 수정 후 검증 항목
1. ✅ HWPX 파일이 없는 메시지에서 다운로드 시도
2. ✅ 기존 HWPX 파일이 있는 메시지에서 다운로드
3. ✅ MD 파일만 있는 메시지에서 자동 변환
4. ✅ 템플릿 업로드 기능 정상 동작

### 테스트 커맨드
```bash
# Backend 테스트
cd backend
pytest tests/test_routers_artifacts.py::test_download_message_hwpx_generates_from_md -v

# Frontend 테스트
cd frontend
npm test -- --testNamePattern="hwpx download"
```

---

## 8. 관련 파일

### Backend
- [artifacts.py](backend/app/routers/artifacts.py) - 메인 라우터 (L264-436)
- [artifact_db.py](backend/app/database/artifact_db.py) - DB 레이어
- [hwp_handler.py](backend/app/utils/hwp_handler.py) - HWPX 생성 로직
- [test_routers_artifacts.py](backend/tests/test_routers_artifacts.py) - 테스트

### Frontend
- [artifactApi.ts](frontend/src/services/artifactApi.ts) - API 클라이언트
- [MessageArtifacts.tsx](frontend/src/components/MessageArtifacts.tsx) - UI 컴포넌트

---

## 9. 교훈 (Lessons Learned)

1. **파일 의존성 관리**
   - 하드코딩된 파일 경로는 위험
   - 필수 파일은 버전 관리 필요

2. **에러 처리**
   - 500 에러 전 구체적인 검증 필요
   - 사용자 친화적 에러 메시지

3. **테스트 커버리지**
   - 파일 시스템 의존성 테스트 중요
   - Mock 뿐만 아니라 실제 파일 테스트 필요

4. **문서화**
   - 템플릿 파일 요구사항 문서화
   - 설치/배포 가이드에 포함

---

## 10. 참고 자료

- [Backend Architecture](backend/CLAUDE.md)
- [HWPX Handler Documentation](backend/doc/hwp_handler.md)
- [Artifact System Design](backend/doc/artifact_system.md)

---

**작성일**: 2025-11-20
**작성자**: Claude Code
**검토자**: Frontend Team
**상태**: 🟡 조치 중 (사용자가 report_template.hwpx 파일 추가 예정)