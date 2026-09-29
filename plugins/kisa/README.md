# kisa Plugin

KISA 주요정보통신기반시설 취약점 점검 체계 기반 진단 스킬을 제공하는 보안 도메인 플러그인입니다.

## 🛠 포함 스킬 (4)

- **`linux`**: Unix/Linux 서버 취약점 점검 (KISA U-01~U-73, 읽기 전용 명령, 양호/취약 판정 + 증빙 리포트) — `/kisa:linux <ip-or-hostname>`
- **`web`**: 웹 서비스 취약점 점검 (KISA WEB-01~WEB-26, 외부 실측 curl·openssl + 서버측 kubectl 보완, 양호/취약 판정 + 증빙 리포트) — `/kisa:web <domain>`
- **`ai`**: AI 시스템 보안 점검 (KECO 별첨6 체크리스트 ①~⑮, 읽기 전용 kubectl, 충족/조치계획 판정 + 증빙 리포트) — `/kisa:ai [namespace...]`
- **`db`**: DB 보안 점검 (PostgreSQL·Doris 계정·권한·개인정보 필드, 읽기 전용 SQL, 양호/조치계획 판정 + 증빙 리포트) — `/kisa:db`

## 🚀 설치 방법

```bash
claude plugin install kisa@zzizily
```

## 로드맵

- `switch` (예정): 네트워크 스위치 점검 (N-01~N-15) — 관리 콘솔 접속 정보 확보 전제
