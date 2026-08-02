#!/usr/bin/env python3
"""
Flow 1: Notion [연구소 일정] → Hermes
READ-ONLY on Notion. Generates a report for Hermes to consume.

Usage: uv run notion_to_hermes.py [--dry-run]
"""

import json
import os
import re
import sys
import yaml
from datetime import datetime, timedelta, timezone
from notion_client import Client

# --- Config ---
NOTION_DB_ID = "151d9199-464c-8047-88f5-c1eb02fbac4e"
OUTPUT_FILE = "/opt/data/calendar-sync/notion_hermes_report.json"
SYNC_DAYS_FUTURE = 30
SYNC_DAYS_PAST = 7
DRY_RUN = "--dry-run" in sys.argv


def load_notion_client():
    key = os.environ.get("NOTION_API_KEY", "")
    if not key:
        config_path = "/opt/data/.hermes/config.yaml"
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            key = cfg.get("mcp_servers", {}).get("notion", {}).get("env", {}).get("NOTION_API_KEY", "")
    if not key:
        print("ERROR: NOTION_API_KEY not set")
        sys.exit(1)
    return Client(auth=key)


def fetch_notion_events(notion):
    today = datetime.now(timezone.utc)
    past = (today - timedelta(days=SYNC_DAYS_PAST)).strftime("%Y-%m-%d")
    future = (today + timedelta(days=SYNC_DAYS_FUTURE)).strftime("%Y-%m-%d")

    results = []
    has_more = True
    cursor = None

    while has_more:
        body: dict = {
            "database_id": NOTION_DB_ID,
            "filter": {
                "and": [
                    {"property": "날짜", "date": {"on_or_after": past}},
                    {"property": "날짜", "date": {"on_or_before": future}},
                ]
            },
            "sorts": [{"property": "날짜", "direction": "ascending"}],
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor

        response = notion.databases.query(**body)
        results.extend(response["results"])
        has_more = response.get("has_more", False)
        cursor = response.get("next_cursor")

    print(f"[Notion] Fetched {len(results)} events ({past} ~ {future})")
    return results


def format_event(page):
    props = page["properties"]

    # Name
    name = ""
    title_prop = props.get("이름", {})
    if title_prop.get("title"):
        name = "".join([t["plain_text"] for t in title_prop["title"]])
    if not name:
        name = "(제목 없음)"

    # Date
    date_prop = props.get("날짜", {}).get("date") or {}
    date_start = date_prop.get("start")
    if not date_start:
        return None

    # Time
    time_str = ""
    time_prop = props.get("시간", {})
    if time_prop.get("rich_text"):
        time_str = "".join([t["plain_text"] for t in time_prop["rich_text"]])

    # Parse time
    parsed_time = None
    if time_str:
        ts = time_str.strip().replace("~", "-").replace("～", "-")
        m = re.match(r"(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})", ts)
        if m:
            parsed_time = f"{int(m[1]):02d}:{m[2]} ~ {int(m[3]):02d}:{m[4]}"
        else:
            m = re.match(r"(오전|오후)\s*(\d{1,2}):?(\d{2})", ts)
            if m:
                hour, minute = int(m[2]), int(m[3])
                if m[1] == "오후" and hour != 12:
                    hour += 12
                elif m[1] == "오전" and hour == 12:
                    hour = 0
                parsed_time = f"{hour:02d}:{minute:00}"

    # Tags
    tags = [t["name"] for t in props.get("태그", {}).get("multi_select", [])]

    # People
    people = [p["name"] for p in props.get("참여자", {}).get("people", []) if p.get("name")]

    return {
        "title": name,
        "date": date_start,
        "end_date": date_prop.get("end") or date_start,
        "time": parsed_time,
        "tags": tags,
        "people": people,
        "source": "Notion [연구소 일정]",
    }


def sync(notion):
    pages = fetch_notion_events(notion)
    formatted = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for p in pages:
        fmt = format_event(p)
        if fmt:
            formatted.append(fmt)

    # Sort by date, then time
    formatted.sort(key=lambda x: (x["date"], x["time"] or ""))

    report = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "source": "Notion [연구소 일정]",
        "range": {
            "past_days": SYNC_DAYS_PAST,
            "future_days": SYNC_DAYS_FUTURE,
        },
        "total_events": len(formatted),
        "events": formatted,
    }

    if not DRY_RUN:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[Report] Saved to {OUTPUT_FILE}")

    # Print summary
    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    print(f"\n📋 연구소 일정 ({today} 기준, ±{SYNC_DAYS_PAST}/{SYNC_DAYS_FUTURE}일)\n")
    for e in formatted:
        time_label = e["time"] or "종일"
        tags = f" [{', '.join(e['tags'])}]" if e["tags"] else ""
        people = f" 👥{', '.join(e['people'])}" if e["people"] else ""
        print(f"  📌 {e['date']} {time_label} — {e['title']}{tags}{people}")

    print(f"\n[{mode}] 총 {len(formatted)}건")
    return formatted


def main():
    if DRY_RUN:
        print("=== DRY RUN (no changes) ===\n")
    notion = load_notion_client()
    sync(notion)


if __name__ == "__main__":
    main()
