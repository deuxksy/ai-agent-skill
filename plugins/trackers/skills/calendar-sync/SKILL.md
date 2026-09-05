---
name: calendar-sync
description: Notion [연구소 일정]과 Google Calendar [Life] 일정을 읽어서 Hermes에 동기화하는 단방향 READ 스크립트. 매일 08:00 cron 동기화, 일정 알림은 별도 크론잡.
---

# Calendar Sync

Notion과 Google Calendar에서 일정을 읽어 Hermes가 활용할 수 있는 JSON 리포트로 저장.

## 명령어

실행 환경: `/opt/data/.venv` (pyproject 없음, venv python 직접 호출).

### `notion-sync` — Notion [연구소 일정] → Hermes

```bash
/opt/data/.venv/bin/python /opt/data/skills/calendar-sync/scripts/notion_to_hermes.py [--dry-run]
```

출력: `/opt/data/calendar-sync/notion_hermes_report.json`

### `gcal-sync` — Google Calendar [Life] → Hermes

```bash
/opt/data/.venv/bin/python /opt/data/skills/calendar-sync/scripts/gcal_to_hermes.py [--dry-run]
```

출력: `/opt/data/calendar-sync/gcal_hermes_report.json`

## 동기화 방향 (모두 단방향 READ)

- **Notion [연구소 일정]** → Hermes (회사 일정, 개인 캘린더에는 쓰지 않음)
- **Google Calendar [Life]** → Hermes (개인 일정)

## 필수 환경변수 / 파일

- `NOTION_API_KEY` — 없으면 `/opt/data/.hermes/config.yaml`의 `mcp_servers.notion.env`에서 자동 로드
- Google OAuth 토큰: `/opt/data/google_token.json` (symlink → `/opt/data/.hermes/secret/google_token.json`)
- client secret: `/opt/data/.hermes/secret/google_client_secret.json`

## 스크립트

- `scripts/notion_to_hermes.py` — DB ID `151d9199-464c-8047-88f5-c1eb02fbac4e`, ±7/30일
- `scripts/gcal_to_hermes.py` — Calendar ID `primary` (deuxksy@gmail.com), ±3/14일

Canonical 소스: `/opt/data/ai-agent-skill/skills/calendar-sync/` (zzizily repo).
복사본: `/opt/data/plugins/ai-agent-skill/plugins/trackers/skills/calendar-sync/`, `/opt/data/skills/calendar-sync/`.
스크립트 수정 시 3곳 모두 동기화할 것.

## Google OAuth 재인증 (토큰 만료 시)

`invalid_grant: Token has been expired or revoked` 발생 시 refresh token이 죽은 것.
사용자 OAuth 동의가 필요하므로 에이전트가 자동 해결 불가 → 주인님에게 안내:

```bash
# 1) 로컬 PC: ssh -L 8085:localhost:8085 brla
# 2) brla에서:
/opt/data/.venv/bin/python /opt/data/skills/calendar-sync/scripts/google_reauth.py
# 3) 출력된 URL을 로컬 브라우저에서 열어 동의 (자동 저장)
```

Google OOB(run_console)는 폐기됨 → `run_local_server(port=8085, open_browser=False)` + SSH 터널 방식 사용. 스코프는 기존 토큰 파일에서 재사용.

## Cron 프롬프트 규칙 (Discord deliver 공통)

Cron 서브에이전트는 시스템 메모리를 상속하지 않으므로 프롬프트에 매번 명시:

1. 마크다운 테이블(`| col |`) 절대 금지. 불릿/헤더/리스트만.
2. 시간 표기: 24시간제 + 오전/오후 병기 (예: "09:00 (오전 9:00)").
3. 각 일정은 `– **시간**: 제목 (참여자)` 형식. 하루 종일은 "하루 종일".
4. 장소는 `📍`, 참여자는 `👥` 접두사.
5. `no_agent: true` + `script` 필드에는 파일명만 (쉘 명령어 넣으면 `Script not found`). 권장: `no_agent: false` + `skills: ["calendar-sync"]`.

## Pitfalls

- 🔴 **notion-client 3.x**: `databases.query()` 제거됨 → `databases.retrieve()`로 `data_sources[0].id` 조회 후 `data_sources.query()` 사용 (스크립트에 fallback 구현됨). v2.2.1 핀하던 옛 방식 폐기.
- Google OAuth 토큰 expiry 비교 시 timezone-aware/naive 충돌 가능 → `creds.valid` 사용으로 회피.
- rate limit: Google Calendar ~1 req/s, Notion ~3 req/s → loop에 `time.sleep(0.1)`.
- 스킬명 중복 금지: 같은 이름의 스킬이 2곳에 있으면 skill_view가 ambiguous로 거부하고 cron 스킬 로드도 실패함.
- 리포트 저장 디렉터리 `/opt/data/calendar-sync/`는 미리 존재해야 함 (스크립트가 mkdir 안 함).
- 🔴 **OAuth 클라이언트 ID 삭제 시 그 클라이언트로 발급된 모든 토큰(리프레시 포함)이 즉시 사망**. 에러: `deleted_client: The OAuth client was deleted.` 액티브 액세스 토큰은 수명(~1시간) 동안 동작해서 "동기화 성공"으로 오해할 수 있음 → `refresh_token` grant를 직접 호출해 리프레시 가능 여부를 확인해야 정확한 진단.
- 클라이언트 재생성은 Google Cloud Console에서 수동으로만 가능 (`데스크톱 앱` 유형). `gcloud iam oauth-clients create`는 Workforce Identity용이라 calendar/gmail 스코프 미지원. 공개 REST API도 없음.
- 호스트 경로 매핑: 컨테이너 `/opt/data` = 호스트 brla의 `/data/hermes/data`. scp 시 `brla:/data/hermes/data/.hermes/secret/google_client_secret.json`.
