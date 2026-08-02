# Response Format

모든 리포트는 Telegram card 형식. **markdown 테이블/헤더 사용 금지.**

## KEV + Critical/High (최우선)

```
🔴🔴 보안 경고: [패키지명]
━━━━━━━━━━━━━━━━
📋 취약점: [CVE-ID]
⚡ 심각도: Critical (CVSS [점수])
🚨 CISA KEV: 실제 악용 중 (조치 기한: [dueDate])
📝 내용: [1-2줄 요약]
📌 설치 버전: [버전] (영향 범위 내)
🔧 조치 방법: [매니저명] [업데이트 명령어]
🔗 참고: [NVD URL]
━━━━━━━━━━━━━━━━
```

## Critical/High (KEV 제외)

```
🔴 보안 경고: [패키지명]
━━━━━━━━━━━━━━━━
📋 취약점: [CVE-ID]
⚡ 심각도: [Critical/High] (CVSS [점수])
📝 내용: [1-2줄 요약]
📌 설치 버전: [버전] (영향 범위 내)
🔧 조치 방법: [매니저명] [업데이트 명령어]
🔗 참고: [NVD URL]
━━━━━━━━━━━━━━━━
```

## Medium/Low

```
🟡 [패키지명]
📋 취약점: [CVE-ID] | 심각도: [Medium/Low] (CVSS [점수])
🔧 조치: [매니저명] [업데이트 명령어]
```

## Update Available (CVE 없음)

```
🟢 [매니저] [패키지명]
→ [현재] → [최신]
```

## No Changes

```
⚪ System Audit
━━━━━━━━━━━━━━━━
[OS/Distro] [매니저 수]개 매니저 점검 완료
보안 이슈 및 업데이트 없음
━━━━━━━━━━━━━━━━
```

## Reference URL Priority

1. NVD: `https://nvd.nist.gov/vuln/detail/[CVE-ID]`
2. GitHub Advisory: GHSA page URL
3. Fallback: `https://www.cvedetails.com/cve/[CVE-ID]/`

## General Rules

- 한국어
- 보고 순서: KEV+Critical → Critical/High → Medium/Low → 업데이트만
- 텍스트 최소화, 기호와 줄바꿈으로 가독성 확보
- OS에 아키텍처 포함: `macOS/arm64`, `Fedora/x86_64`
- upgrade는 안내만, 실행은 `/zzizily:system-upgrade`
