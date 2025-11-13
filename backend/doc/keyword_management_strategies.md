# 키워드 매칭 관리 전략 비교

## 문제 정의

```
현재 상황:
- "RISK", "위험성" 같은 커스텀 키워드는 정의되지 않음
- 따라서 기본값(section_content)으로만 처리됨
- 이런 경우들이 누적되면 메타정보의 정확성 ↓

예:
{{RISK}}           → "RISK 섹션" (너무 일반적)
{{POSITION}}       → "POSITION 섹션" (불명확)
{{MARKET_TREND}}   → "MARKET_TREND 섹션" (길고 부정확)
{{REGULATION}}     → "REGULATION 섹션" (부정확)
```

**질문:** 이런 상황에서 어떻게 관리할 것인가?

---

## 3가지 전략 비교

### 🟢 **전략 1: Admin 페이지에서 관리자가 직접 등록**

#### 개념
```
Admin이 직접 커스텀 키워드를 등록하는 방식

예:
- "RISK" → section_content (위험 분석)
- "POSITION" → section_title (직책/직위)
- "위험성" → section_content (위험 요소)
```

#### 장점 ✅
```
1. 최고의 정확성
   - Admin이 직접 관리하므로 100% 정확

2. 완전한 커스터마이징
   - 조직의 특정 상황에 맞춤
   - "위험성" 같은 한글 키워드도 지원

3. 유지보수 명확
   - Admin 페이지 하나로 관리
   - 버전 관리 용이
```

#### 단점 ❌
```
1. 관리 부담 증가
   - 템플릿마다 새로운 키워드는 수동으로 등록 필요
   - Admin이 모든 것을 다 알아야 함

2. 초기 설정 복잡
   - 첫 설정이 번거로움
   - 실수 가능성 높음

3. 확장성 제한
   - 새로운 조직이 추가되면 처음부터 시작
   - 키워드 중복 가능성

4. 사용자가 자동화를 못함
   - Template 업로드 후 즉시 완벽한 메타정보를 못 받음
   - Admin의 등록을 기다려야 함
```

#### 구현 복잡도
```
중간 ~ 높음
- Admin API 추가 필요
- 키워드 관리 UI 개발 필요
- 데이터베이스 스키마 확장 필요
```

#### 예시
```
관리자 페이지:
┌─────────────────────────────────────────┐
│ 커스텀 키워드 관리                       │
├─────────────────────────────────────────┤
│ [추가] [수정] [삭제]                    │
├─────────────────────────────────────────┤
│ 키워드        │ 타입              │ 설명 │
├─────────────────────────────────────────┤
│ RISK          │ section_content   │ 위험 분석 │
│ POSITION      │ section_title     │ 직책    │
│ 위험성        │ section_content   │ 위험    │
│ MARKET_TREND  │ section_content   │ 시장 트렌드 │
└─────────────────────────────────────────┘
```

---

### 🔵 **전략 2: 기본 키워드 사전을 점진적으로 확장 (권장)**

#### 개념
```
처음에는 기본 키워드로 시작하되,
사용 패턴을 분석하여 점진적으로 추가

1단계 (현재): 5개 기본 키워드
   TITLE, SUMMARY, BACKGROUND, CONCLUSION, DATE

2단계 (1개월): 추가로 자주 사용되는 키워드 5개
   RISK, OVERVIEW, MARKET, REGULATION, EXECUTIVE

3단계 (3개월): 조직별 특화 키워드 추가
   ...
```

#### 장점 ✅
```
1. 점진적 개선
   - 처음부터 완벽하지 않아도 괜찮음
   - 사용 데이터를 기반으로 개선

2. 데이터 기반 의사결정
   - 실제 사용 패턴 분석 가능
   - 불필요한 키워드 추가 방지

3. 유지보수 용이
   - 필요한 만큼만 추가
   - 코드 변경으로 간단히 처리 가능

4. 사용자 만족도 향상
   - 시간이 지날수록 더 정확한 메타정보
   - 점진적 개선을 체감

5. 낮은 초기 비용
   - Admin 페이지 불필요
   - 코드만 수정하면 됨
```

#### 단점 ❌
```
1. 초기에는 부정확
   - 첫 달은 기본값이 많음
   - 사용자가 답답해할 수 있음

2. 특수한 키워드는 영구적으로 기본값
   - 한글 키워드 (예: "위험성") 미지원
   - 조직 특화 키워드는 못 다룸

3. 모니터링 필요
   - 어떤 키워드를 추가할지 수시로 결정
   - 데이터 분석 인력 필요
```

#### 구현 복잡도
```
낮음
- 기존 코드에 키워드만 추가
- Admin 페이지 불필요
- 간단한 데이터 수집만 필요
```

#### 예시

**1단계 (현재)**
```python
keyword_classification = {
    "TITLE": {...},
    "SUMMARY": {...},
    "BACKGROUND": {...},
    "CONCLUSION": {...},
    "DATE": {...},
}
```

**2단계 (1개월 후)**
```python
keyword_classification = {
    "TITLE": {...},
    "SUMMARY": {...},
    "BACKGROUND": {...},
    "CONCLUSION": {...},
    "DATE": {...},

    # 추가된 키워드들
    "RISK": {"type": "section_content", "section": "위험 분석"},
    "OVERVIEW": {"type": "section_title", "section": "개요"},
    "MARKET": {"type": "section_content", "section": "시장 분석"},
    "REGULATION": {"type": "section_content", "section": "규제 현황"},
    "EXECUTIVE": {"type": "section_content", "section": "요약"},
}
```

---

### 🟡 **전략 3: 하이브리드 (전략 1 + 2)**

#### 개념
```
기본 키워드는 코드에서 관리
조직별/사용자별 커스텀 키워드는 Admin에서 관리

기본 키워드 (코드):
- TITLE, SUMMARY, BACKGROUND, CONCLUSION, DATE, RISK

커스텀 키워드 (Admin 등록):
- 조직 특화: "위험성", "POSITION", "MARKET_TREND"
- 사용자 정의: Template 별로 추가
```

#### 장점 ✅
```
1. 최고의 유연성
   - 일반적인 것은 자동
   - 특수한 것은 커스터마이징

2. 점진적 개선 + 완전한 제어
   - 기본 키워드 확장 가능
   - Admin이 필요시 오버라이드 가능

3. 조직별 특화 가능
   - 각 조직의 용어 체계 반영
   - 한글 키워드 지원 가능

4. 최고의 정확성
   - 자동화 + 수동 관리 조합
```

#### 단점 ❌
```
1. 구현 복잡도 높음
   - Admin 페이지 필요
   - DB 스키마 복잡
   - 코드와 DB 관리 동시 필요

2. 관리 복잡도 높음
   - 어떤 것을 Admin에 등록할지 판단 필요
   - 중복 가능성 (코드 + DB)

3. 유지보수 어려움
   - 코드와 데이터베이스를 동시에 봐야 함
   - 버전 관리 복잡
```

#### 구현 복잡도
```
높음
- Admin API 필요
- 키워드 병합 로직 필요 (코드 + DB)
- 우선순위 처리 필요
```

#### 예시

**Meta_info_generator.py**
```python
# 코드에 정의된 기본 키워드
BUILT_IN_KEYWORDS = {
    "TITLE": {...},
    "SUMMARY": {...},
    "BACKGROUND": {...},
    "CONCLUSION": {...},
    "DATE": {...},
    "RISK": {...},
}

def create_meta_info_from_placeholders(placeholders, custom_keywords=None):
    # 기본 키워드 + 커스텀 키워드 병합
    all_keywords = {**BUILT_IN_KEYWORDS, **(custom_keywords or {})}

    # 이후 진행...
```

**Admin API**
```
POST /api/admin/custom-keywords
{
    "keyword": "위험성",
    "type": "section_content",
    "display_name": "위험 요소",
    "description": "...",
    "examples": [...]
}
```

---

## 종합 비교 테이블

| 항목 | 전략 1 (Admin 관리) | 전략 2 (점진적 확장) | 전략 3 (하이브리드) |
|------|---|---|---|
| **정확성** | ⭐⭐⭐⭐⭐ | ⭐⭐�� | ⭐⭐⭐⭐⭐ |
| **초기 구현 시간** | 1-2주 | 1-2일 | 2-3주 |
| **관리 복잡도** | 중간 | 낮음 | 높음 |
| **자동화 정도** | 낮음 | 높음 | 중간 |
| **한글 키워드 지원** | ✅ 가능 | ❌ 불가능 | ✅ 가능 |
| **조직별 커스터마이징** | ✅ 완전 | ❌ 불가능 | ✅ 완전 |
| **초기 정확성** | 높음 | 낮음 | 높음 |
| **장기 확장성** | ✅ 좋음 | ✅ 좋음 | ✅ 최고 |
| **사용자 자동화** | 필요 (Admin 등록 후) | ✅ 즉시 | ✅ 즉시 + 개선 |
| **운영 비용** | 높음 | 낮음 | 중간 |

---

## 추천 로드맵

### 🎯 **Phase별 추천 전략**

#### **Phase 1 (지금, MVP 단계): 전략 2 (점진적 확장)**

```
이유:
1. 빠른 출시 필요
   - Admin 페이지 개발 시간 절약
   - 바로 사용 가능한 기본 키워드

2. 실제 사용 데이터 수집
   - 어떤 키워드가 자주 나오는지 파악
   - 데이터 기반 의사결정

3. 낮은 위험도
   - 초기에 완벽할 필요 없음
   - 점진적 개선 가능

로드맵:
시작 (5개): TITLE, SUMMARY, BACKGROUND, CONCLUSION, DATE
1개월 후 (10개): 위의 5개 + RISK, OVERVIEW, MARKET, REGULATION, EXECUTIVE
3개월 후 (15개): 더 자주 사용되는 키워드 추가
```

#### **Phase 2 (3-6개월 후): 전략 3 (하이브리드) 전환**

```
이유:
1. 사용 패턴 분석 완료
   - 어떤 키워드가 필요한지 알게 됨

2. 조직별 특화 필요성 파악
   - 고객마다 다른 용어 체계 존재
   - 커스터마이징 요청 증가

3. Admin 페이지 개발 타이밍
   - Phase 1의 경험으로 더 나은 UI/UX 설계 가능
   - 실제 필요한 기능만 구현

로드맵:
- 기본 키워드 (코드): 10-15개
- Admin 관리: 조직별 커스텀 키워드
- 병합 로직: 자동 + 수동 종합
```

#### **Phase 3 (1년 이상): 전략 3 고도화**

```
이유:
1. 충분한 데이터 축적
   - 패턴 분석 완료
   - 자주 등장하는 키워드 파악

2. 고객 다양성 증가
   - 다양한 업계의 고객 증가
   - 각자의 특수 키워드 필요

3. ML/AI 도입 고려
   - 자동 키워드 추천 시스템
   - 자동 분류 강화
```

---

## 구체적 예시: Phase 1 구현 방안

### 📝 **Step 1: 기본 키워드 정의**

```python
# backend/app/utils/meta_info_generator.py

# 1단계: 기본 키워드 (현재)
PHASE_1_KEYWORDS = {
    "TITLE": {"type": "section_title", "section": "제목"},
    "SUMMARY": {"type": "section_content", "section": "요약"},
    "BACKGROUND": {"type": "section_content", "section": "배경"},
    "CONCLUSION": {"type": "section_content", "section": "결론"},
    "DATE": {"type": "metadata", "section": "날짜"},
}

# 2단계: 추가 키워드 (1개월 후 추가)
PHASE_2_KEYWORDS = {
    **PHASE_1_KEYWORDS,
    "RISK": {"type": "section_content", "section": "위험"},
    "OVERVIEW": {"type": "section_title", "section": "개요"},
    "MARKET": {"type": "section_content", "section": "시장"},
    "REGULATION": {"type": "section_content", "section": "규제"},
    "EXECUTIVE": {"type": "section_content", "section": "요약"},
}

# 현재 사용할 키워드
KEYWORD_CLASSIFICATION = PHASE_1_KEYWORDS  # Phase 1
# KEYWORD_CLASSIFICATION = PHASE_2_KEYWORDS  # Phase 2로 업그레이드 시 변경
```

### 📊 **Step 2: 사용 패턴 로깅**

```python
# backend/app/routers/templates.py

async def upload_template(...):
    # ... 기존 코드 ...

    # 신규: 사용된 Placeholder 로깅
    for placeholder in placeholders:
        key = placeholder.placeholder_key.replace("{{", "").replace("}}", "")

        # DB에 로깅 (추후 분석용)
        KeywordUsageLog.create(
            user_id=current_user.id,
            template_id=template.id,
            keyword=key,
            matched_keyword=matched_keyword,  # 일치한 키워드 (없으면 None)
            created_at=datetime.now()
        )

# 로깅 예시:
# keyword="RISK_ANALYSIS", matched_keyword=None → 기본값 사용
# keyword="POSITION_TITLE", matched_keyword="TITLE" → 매칭됨
# keyword="DATE_PUBLISHED", matched_keyword="DATE" → 매칭됨
```

### 📈 **Step 3: 월간 분석 및 업데이트**

```
매월 첫째 주:
1. 로그 분석
   SELECT keyword, COUNT(*) as count
   FROM keyword_usage_logs
   WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
   GROUP BY keyword
   ORDER BY count DESC
   LIMIT 20

2. 상위 5개 추가 후보 검토
   - RISK: 120건
   - OVERVIEW: 95건
   - MARKET: 88건
   - REGULATION: 76건
   - POSITION: 65건

3. 추가할 키워드 결정
   → 다음 달부터 PHASE_2_KEYWORDS 사용
```

---

## 최종 권장사항

### 🎯 **현재 단계: 전략 2 (점진적 확장) 채택**

#### 이유:
```
1. 빠른 출시 가능
   - Unit Spec 바로 구현 가능
   - Admin 페이지 개발 불필요

2. 실제 데이터 기반 개선
   - 사용 패턴 분석으로 다음 단계 계획
   - 불필요한 기능 개발 방지

3. 낮은 초기 위험도
   - 기본값이 있으므로 안전
   - 점진적 개선으로 사용자 만족도 향상

4. 향후 전략 3으로 전환 용이
   - 기본값 구조가 그대로 사용됨
   - 나중에 Admin 추가 가능
```

#### 구현 체크리스트:
```
Phase 1 (지금):
- [ ] 기본 키워드 5개로 구현
- [ ] 키워드 사용 로깅 추가
- [ ] Unit Spec 완료

Phase 2 (1개월 후):
- [ ] 로그 분석
- [ ] 추가 키워드 5개 선정
- [ ] 코드 업데이트

Phase 3 (3개월 후):
- [ ] Admin 페이지 개발 계획
- [ ] 하이브리드 전략 전환 검토
```

---

## 추가 고려사항

### 🔒 **보안**
```
Admin 페이지 추가 시:
- 관리자 인증 필수
- 키워드 검증 (SQL Injection 방지)
- 감사 로그 기록
```

### 📊 **모니터링**
```
Phase 1/2 사용:
- 기본값 사용 비율 추적
- 매치된 키워드 비율 추적
- 목표: 기본값 사용 < 20%
```

### 🔄 **버전 관리**
```
키워드 추가 시:
- CHANGELOG에 기록
- 버전 업데이트 (v2.1.0)
- Release note에 설명
```

---

## 결론

| 항목 | 선택 | 이유 |
|------|------|------|
| **현재 (Phase 1)** | 전략 2 | 빠른 출시 + 데이터 기반 의사결정 |
| **3-6개월 후 (Phase 2)** | 전략 3 | 안정성 + 유연성 조합 |
| **1년 이상 (Phase 3)** | 전략 3 고도화 | ML/AI 통합, 완전 자동화 |
