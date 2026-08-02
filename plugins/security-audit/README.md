# security-audit Plugin

코드 보안 정적 점검(SAST), 시스템 패키지 취약점 감사(CVE) 및 백도어 포렌식 진단/복구 스킬을 제공하는 보안 도메인 플러그인입니다.

## 🛠️ 포함 스킬 (4)

- **`code-audit`**: 정적 코드 보안 점검 (SAST scan, CWE 분류, OWASP Top 10 매핑)
- **`system-audit`**: 시스템 패키지 보안 취약점 감사 (CVE, CVSS, CISA KEV)
- **`backdoor-investigation`**: Linux 백도어/맬웨어 포렌식 진단 (read-only 안전 명령)
- **`backdoor-remediation`**: 백도어 제거, 프로세스 종료 및 방화벽 차단 (승인 필요)

## 🚀 설치 방법

```bash
claude plugin install security-audit@zzizily
```
