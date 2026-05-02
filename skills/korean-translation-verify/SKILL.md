---
name: korean-translation-verify
description: Use when translating or verifying Korean documentation for GL.iNet router firmware, especially when checking translation quality, naturalness, and technical terminology accuracy. Use before marking translations as complete or committing translation changes.
---

# Korean Translation Verification

## Overview

한국어 기술 문서 번역의 품질을 Gemma-3-27b-it API를 사용하여 자동으로 검증합니다. 기계 번역투의 어색한 표현, 부정확한 기술 용어, 문장의 간결성 문제를 식별합니다.

## When to Use

**사용 시기:**
- 한국어 번역 문서 완료 후 품질 검증
- 기계 번역 결과 검토
- 기술 용어 번역 정확성 확인
- 문장의 자연스러움 평가
- 번역 일관성 검증

**사용하지 않을 때:**
- 영어 원문 작성
- 코드 수정
- 빌드/테스트 실행

## Core Pattern

### 검증 프로세스

1. **API 호출**: Gemma-3-27b-it에 번역 텍스트 전송
2. **피드백 수신**: ISSUE 또는 통과 판정
3. **문제 수정**: ISSUE가 있는 경우 수정 후 재검증

### 피드백 패턴

```python
# ISSUE: 구체적인 문제점과 개선 제안
"ISSUE: \"NC\"가 \"미사용\"으로 번역되는 것이 좋습니다."

# 통과: 번역이 적절함
"번역이 자연스럽고 기술 용어가 적절히 사용되었습니다."
```

## Quick Reference

| 검증 항목 | 확인 내용 |
|---------|---------|
| 자연스러움 | 기계 번역투 어색한 표현 없는지 |
| 기술 용어 | 영어 병기 또는 적절한 한국어 번역 |
| 간결성 | 불필요하게 긴 문장 없는지 |
| 형식 | 마크다운 형식 준수 (blockquote vs Note) |

## Implementation

### Python 스크립트 사용

```python
from scripts.verify_translation import TranslationVerifier

# API 키 설정 필요
verifier = TranslationVerifier(api_key="your_key")

# 단일 파일 검증
result = verifier.verify_file("docs/ko/docs/user_guide/gl-x300b/index.md")
print(f"Status: {result['status']}")
print(f"Feedback: {result.get('feedback', '')}")

# 배치 검증
files = ["file1.md", "file2.md"]
results = verifier.verify_batch(files, delay=1.0)

# 결과 저장
verifier.save_results(results, "output.json")
```

### CLI 사용

```bash
# 환경 변수 설정
export GEMMA_API_KEY="your_key"

# CLI 사용
python3 scripts/verify_translation.py --file path/to/file.md
python3 scripts/verify_translation.py --dir . --output results.json
```

## Common Mistakes

| 실수 | 영향 | 해결 |
|-----|------|------|
| API 키 미설정 | 검증 실패 | `export GEMMA_API_KEY="your_key"` |
| 너무 긴 텍스트 전송 | API 타임아웃 | 3000자로 제한 |
| delay 미설정 | 속도 제한 위반 | `delay=1.0` 기본값 사용 |
| 피드백 무시 | 품질 저하 | 모든 ISSUE 수정 필요 |

## Red Flags - STOP and Fix

- 피드백 없이 "완료" 선언
- ISSUE 발견 시 무시하고 진행
- 기계 번역 그대로 사용
- 영어 기술 용어 무조건 한국어 번역 (병기 필요 시 영어 병기)

## 검증 기준 상세

### 1. 자연스러운 한국어 표현

**Bad:** "휴대하기 편리하고 여행용으로 적합"
**Good:** "휴대용"

### 2. 기술 용어 처리

**Bad:** "무선 분배 시스템" (WDS)
**Good:** "WDS(무선 분배 시스템)" 또는 "WDS"

### 3. 마크다운 형식

**Bad:** `!!! Note` (영어 문법)
**Good:** `> **참고**` (한국어 blockquote)

### 4. 간결성

**Bad:** "30개 이상의 VPN 서비스 제공업체의 VPN 설정 파일을 업로드하여 VPN 클라이언트로 설정할 수 있어"
**Good:** "30개 이상의 VPN 서비스 제공업체 설정 파일을 업로드하여 VPN 클라이언트로 설정할 수 있습니다."

## API 설정

**엔드포인트:** `https://ai.bun-bull.ts.net/v1beta/models/gemma-3-27b-it:generateContent`

**헤더:**
```python
headers = {
    "Content-Type": "application/json",
    "X-goog-api-key": api_key
}
```

**페이로드 구조:**
```python
payload = {
    "contents": [{
        "parts": [{
            "text": user_message  # 검증할 텍스트
        }]
    }],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 2048
    }
}
```

## 결과 해석

### 통과 (passed)
- 번역이 자연스럽고 기술 용어가 적절함
- 수정 불필요

### 검증 필요 (needs_review)
- ISSUE 표시와 함께 구체적인 개선 제안 제시
- 수정 후 재검증 필요

### 오류 (error)
- API 호출 실패
- 파일 읽기 실패
- JSON 파싱 오류
