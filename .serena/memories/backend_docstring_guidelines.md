# Backend DocString Guidelines

## 핵심 규칙

**백엔드 Python 코드의 모든 함수와 클래스에는 반드시 Google Style DocString을 작성해야 합니다.**

## Google Style DocString 구조

```python
def function_name(arg1: type1, arg2: type2 = default) -> return_type:
    """함수를 한 줄로 요약합니다.

    상세 설명이 필요한 경우 여기에 작성합니다.

    Args:
        arg1: 첫 번째 인자 설명
        arg2: 두 번째 인자 설명 (선택, 기본값: default)

    Returns:
        반환값 설명

    Raises:
        ExceptionType: 예외 발생 조건

    Examples:
        >>> result = function_name(1, 2)
        >>> print(result)
        3
    """
    pass
```

## 주요 섹션

1. **Summary** (필수): 첫 줄, 명령형 동사로 시작
2. **Args** (파라미터 있으면 필수): 각 파라미터 설명
3. **Returns** (반환값 있으면 필수): 반환값 설명
4. **Raises** (권장): 발생 가능한 예외들
5. **Examples** (복잡한 함수는 권장): 사용 예시

## 적용 파일

- `app/routers/*.py`
- `app/models/*.py`
- `app/database/*.py`
- `app/utils/*.py`
- backend 디렉토리의 모든 Python 파일

## 참고

상세 가이드라인: `backend/.CLAUDE.md`
