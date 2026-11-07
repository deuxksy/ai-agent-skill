# email Plugin

hiworks 메일 온디맨드 수신·조회·승인 발송(`hiworks-mail`) 스킬을 제공하는 이메일 도메인 플러그인입니다.

## 🛠 포함 스킬 (1)

- **`hiworks-mail`**: `hiworks-mail-sync`(getmail POP3 증분 수신) + `himalaya`(Maildir 조회·SMTP 발송) 연동 — 발송은 매번 사용자 승인 후, 서버 메일 삭제 금지

## 🚀 설치 방법

```bash
claude plugin install email@zzizily
```

## 🔗 의존 구성 요소 (dotfiles 배포)

- `hiworks-mail-sync` 래퍼 (`~/.local/bin/`) — `~/.config/hiworks/.env` 자격증명 소비
- `himalaya` config (`~/.config/himalaya/config.toml`) — `hiworks` account (maildir backend)
