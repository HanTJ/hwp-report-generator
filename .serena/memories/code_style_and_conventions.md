# 코드 스타일 및 컨벤션

## 언어 및 인코딩
- 프로그래밍 언어: Python 3
- 파일 인코딩: UTF-8
- 주석 및 문서화: 한국어

## 네이밍 컨벤션
- **변수/함수**: snake_case (예: `user_db`, `generate_report`)
- **클래스**: PascalCase (예: `ClaudeClient`, `HWPHandler`)
- **상수**: UPPER_SNAKE_CASE (예: `TEMPLATE_PATH`)
- **프라이빗 멤버**: 앞에 언더스코어 (예: `_internal_method`)

## 함수/클래스 문서화
```python
def function_name(param1: str, param2: int) -> dict:
    """
    한 줄 요약
    
    Args:
        param1: 파라미터 설명
        param2: 파라미터 설명
    
    Returns:
        반환값 설명
    """
    pass
```

## 타입 힌트
- 모든 함수 파라미터와 반환값에 타입 힌트 사용
- Pydantic 모델을 적극 활용

## 로깅
```python
import logging
logger = logging.getLogger(__name__)

# 로그 레벨 사용
logger.info("정보성 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
```

## 예외 처리
- FastAPI의 HTTPException 사용
- 명확한 에러 메시지 제공 (한국어)
- 로그 기록 필수

```python
try:
    # 작업 수행
    pass
except SpecificError as e:
    logger.error(f"에러 발생: {str(e)}")
    raise HTTPException(status_code=500, detail="에러 메시지")
```

## 파일 구조
- 관련 기능은 같은 디렉토리에 모듈화
- 각 디렉토리에 `__init__.py` 포함
- 라우터는 `routers/` 디렉토리에 분리

## Pydantic 모델
- 입력/출력 데이터 검증용 모델 정의
- 네이밍: `{기능}Request`, `{기능}Response`

## 보안
- 비밀번호는 bcrypt로 해싱
- JWT 토큰 기반 인증
- 입력 값 검증 (파일명, 경로 등)