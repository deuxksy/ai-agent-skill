---
name: system-audit
description: "보안 취약점 감사. CVE → NVD/NIST → CVSS → CISA KEV → upgrade 흐름. macOS, Linux, 언어별 패키지 매니저 크로스 플랫폼 지원. 패키지 업그레이드는 /zzizily:system-upgrade 사용."
---

# System Audit

보안 취약점 점검. 상세 절차는 [references/workflow.md](references/workflow.md) 참조.

## 핵심 프로세스

```text
CVE 탐지 → NVD/NIST (영향 범위) → CVSS (심각도) → CISA KEV (실제 악용 여부) → upgrade 안내
```

| 단계 | 소스 | 인증 |
| :--- | :--- | :--- |
| CVE 탐지 | GitHub Advisory / Built-in audit | 없음 |
| NVD/NIST | `https://services.nvd.nist.gov/` | 없음 (rate limit) |
| CVSS | NVD 응답에 포함 (`baseMetricV3.cvssV3`) | 없음 |
| CISA KEV | 공개 JSON 피드 | 없음 |

## Workflow Summary

1. **OS/Distro 감지** → 시스템 패키지 매니저 자동 선택
2. **버전 수집** → 모든 설치 패키지 버전 수집
3. **Phase 1: Built-in audit** → `brew audit`, `npm audit`, `pip-audit`, `dnf updateinfo`
4. **Phase 2: 구버전 필터링** → 업데이트 가능한 패키지만 대상
5. **Phase 3: CVE → NVD → CVSS → CISA KEV** → 취약점 상세 분석
6. **CVE 검증** → 설치 버전이 영향 범위 내인지 확인
7. **리포트** → [references/response-format.md](references/response-format.md) 형식으로 출력

## 패키지 매니저 우선순위

1. mise
2. uv tool
3. pnpm
4. Homebrew
5. nix
6. 시스템 (dnf/apt/pacman)

> **pip, npm 제외**: pip는 uv tool의 전이 의존성이므로 직접 관리하지 않음. npm은 pnpm으로 대체.

## Key Rules

- **No false positives**: CVE가 설치 버전의 영향 범위 내인지 필수 검증 (semver check)
- **No redundant searches**: Phase 1에서 이미 탐지된 패키지는 Phase 3에서 중복 검색 금지
- **CVSS 우선순위**: Critical/High 먼저 보고, Medium/Low는 별도 섹션
- **CISA KEV 강조**: 실제 악용 중인 취약점은 최우선 보고
- **한국어 리포트**: 결과는 항상 한국어로 출력
- **upgrade는 별도 스킬**: 취약점 안내만, 실제 업그레이드는 `/zzizily:system-upgrade`
