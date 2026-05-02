# Response Format

All reports use Telegram card format. **No markdown tables or headers.**

## Security Vulnerability Found

```
🔴 보안 경고: [패키지명]
━━━━━━━━━━━━━━━━
📋 취약점: [이름/ID]
⚡ 심각도: [Critical/High/Medium/Low]
📝 내용: [1-2줄 요약]
📌 설치 버전: [버전] (영향 범위 내)
🔧 조치 방법: [매니저명] [업데이트 명령어]
🔗 참고: [NVD 또는 Advisory 상세페이지 URL]
━━━━━━━━━━━━━━━━
```

### Reference URL Priority

1. NVD: `https://nvd.nist.gov/vuln/detail/[CVE-ID]`
2. GitHub Advisory: GHSA page URL
3. Fallback: `https://www.cvedetails.com/vulnerability-list/vendor_id-([vendor_id]).html`

## Update Available (no security issue)

```
🟢 [매니저] [패키지명]
→ [현재] → [최신]
```

## No Changes

```
⚪ Daily Security & Update Check
━━━━━━━━━━━━━━━━
[OS/Distro] [매니저 수]개 매니저 점검 완료
보안 이슈 및 업데이트 없음
━━━━━━━━━━━━━━━━
```

## General Rules

- Korean language
- Security issues first, then updates
- Minimize text, use symbols and line breaks for readability
- Include architecture in OS label when relevant: `macOS/arm64`, `Fedora/x86_64`
