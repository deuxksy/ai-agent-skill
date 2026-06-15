---
name: calendar-sync
description: Notion [연구소 일정]과 Google Calendar [Life] 일정을 읽어서 Hermes에 동기화하는 단방향 READ 스크립트. 하루 3번 (08:00, 13:00, 19:00) 실행.
---

# Calendar Sync

Notion과 Google Calendar에서 일정을 읽어 Hermes가 활용할 수 있는 JSON 리포트로 저장.

## 명령어

### `notion-sync` — Notion [연구소 일정] → Hermes
회사 일정을 READ하여 리포트 저장. 개인 캘린더에는 쓰지 않음.

```bash
cd /opt/data/calendar-sync && uv run python scripts/notion_to_hermes.py [--dry-run]
```

### `gcal-sync` — Google Calendar [Life] → Hermes
개인 일정을 READ하여 리포트 저장.

```bash
cd /opt/data/calendar-sync && uv run python scripts/gcal_to_hermes.py [--dry-run]
```

### `today` — 오늘 일정 요약
두 리포트에서 오늘 날짜(Asia/Seoul) 이벤트를 필터링하여 요약.

리포트 파일:
- `/opt/data/calendar-sync/notion_hermes_report.json`
- `/opt/data/calendar-sync/gcal_hermes_report.json`

## 동기화 방향 (모두 단방향 READ)

- **Notion [연구소 일정]** → Hermes (회사 일정, 개인 캘린더에는 쓰지 않음)
- **Google Calendar [Life]** → Hermes (개인 일정)

## 필수 환경변수

- `NOTION_API_KEY` — Notion PAT 토큰 (Hermes config.yaml MCP 서버 설정에 있음)
- `GOOGLE_TOKEN_PATH` — Google OAuth 토큰 파일 경로 (기본: `/opt/data/google_token.json`)

## 의존성

uv 가상환경 (`/opt/data/calendar-sync/.venv`):

```bash
cd /opt/data/calendar-sync && uv add notion-client==2.2.1 google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib pyyaml
```

> **주의**: `notion-client` v3.x에서 `databases.query()`가 제거됨. 반드시 v2.2.1 사용.

## 스크립트

### scripts/notion_to_hermes.py

Notion [연구소 일정] DB에서 ±7/30일 이벤트를 읽어 리포트 생성.

```bash
cd /opt/data/calendar-sync && uv run python scripts/notion_to_hermes.py [--dry-run]
```

출력: `/opt/data/calendar-sync/notion_hermes_report.json`

DB ID: `151d9199-464c-8047-88f5-c1eb02fbac4e`

### scripts/gcal_to_hermes.py

Google Calendar [Life] (primary)에서 ±3/14일 이벤트를 읽어 리포트 생성.

```bash
cd /opt/data/calendar-sync && uv run python scripts/gcal_to_hermes.py [--dry-run]
```

출력: `/opt/data/calendar-sync/gcal_hermes_report.json`

Calendar ID: `primary` (= deuxksy@gmail.com)

## Google OAuth 토큰 관리

- 토큰 파일 위치: `GOOGLE_TOKEN_PATH` 환경변수로 제어 (기본 `/opt/data/google_token.json`)
- 토큰 만료 시 스크립트가 자동으로 refresh 후 파일에 저장
- **중요**: 토큰 파일은 스킬에 포함하지 않음 (보안 센서티브)

## Cron 스케줄

매일 3회 실행 (Asia/Seoul):

| 시간 | 동작 |
|------|------|
| 08:00 | 두 스크립트 실행 + 리포트 갱신 |
| 13:00 | 동일 |
| 19:00 | 동일 |

| 시간 | 동작 |
|------|------|
| 08:55 | Hermes가 두 리포트에서 오늘 일정을 읽어 Discord로 알림 |

## 리포트 형식

```json
{
  "synced_at": "2026-06-15T16:30:00+00:00",
  "source": "Notion [연구소 일정]",
  "range": { "past_days": 7, "future_days": 30 },
  "total_events": 25,
  "events": [
    {
      "title": "가산IDC 신규장비 입고",
      "date": "2026-06-18",
      "end_date": "2026-06-18",
      "time": null,
      "tags": ["인프라"],
      "people": ["Crong (김석영)", "김평식"],
      "source": "Notion [연구소 일정]"
    }
  ]
}
```

Google Calendar 리포트는 `tags` 대신 `location`, `type`("all-day"/"timed") 포함.

## Pitfalls

- `notion-client` v3은 `databases.query()` 없음 → 반드시 v2.2.1 핀
- Google OAuth 토큰 expiry 비교 시 timezone-aware/naive 충돌 가능 → `creds.valid` 사용으로 회피
- rate limit: Google Calendar ~1 req/s, Notion ~3 req/s → loop에 `time.sleep(0.1)`
