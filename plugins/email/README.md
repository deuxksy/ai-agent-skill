# email Plugin

hiworks 메일 온디맨드 수신·조회·승인 발송(`hiworks`) 스킬을 제공하는 이메일 도메인 플러그인입니다.

## 🛠 포함 스킬 (1)

- **`hiworks`**: `hiworks-mail-sync`(Python stdlib POP3 증분 수신, 스킬 `scripts/` 동봉) + `himalaya`(Maildir 조회·SMTP 발송) 연동 — 발송은 매번 사용자 승인 후, 서버 메일 삭제 금지

## 🚀 설치 방법

```bash
claude plugin install email@zzizily
```

## 🔗 의존 구성 요소

- `hiworks-mail-sync` (`skills/hiworks/scripts/`) — Python 3 표준 라이브러리만 사용 (별도 설치 불필요, macOS/Linux/Windows 공통) — `~/.config/hiworks/.env` 자격증명 소비
- `himalaya` config (`~/.config/himalaya/config.toml`) — `hiworks` account (maildir backend), dotfiles 배포
