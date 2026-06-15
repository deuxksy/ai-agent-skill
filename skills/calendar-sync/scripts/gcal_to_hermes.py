#!/usr/bin/env python3
"""
Flow 2: Google Calendar [Life] → Hermes (Notion database or local report)
단방향 READ(Google Calendar) → READ report to Hermes

Usage: uv run gcal_to_hermes.py [--dry-run]
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google_auth_httplib2 import Request
from googleapiclient.discovery import build

# --- Config ---
GOOGLE_TOKEN_PATH = "/opt/data/google_token.json"
GCAL_SOURCE_CALENDAR = "primary"  # Life calendar
OUTPUT_FILE = "/opt/data/calendar-sync/gcal_hermes_report.json"
TZ = "Asia/Seoul"
SYNC_DAYS_FUTURE = 14
SYNC_DAYS_PAST = 3
DRY_RUN = "--dry-run" in sys.argv


def load_google_credentials():
    with open(GOOGLE_TOKEN_PATH) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"],
    )
    if not creds.valid:
        creds.refresh(Request())
        token_data["token"] = creds.token
        token_data["expiry"] = creds.expiry.isoformat()
        if creds.refresh_token:
            token_data["refresh_token"] = creds.refresh_token
        with open(GOOGLE_TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=2)
        print("[Google] Token refreshed")
    return creds


def fetch_gcal_events(gcal_service):
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=SYNC_DAYS_PAST)).isoformat()
    time_max = (now + timedelta(days=SYNC_DAYS_FUTURE)).isoformat()

    events = []
    page_token = None

    while True:
        result = gcal_service.events().list(
            calendarId=GCAL_SOURCE_CALENDAR,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
            pageToken=page_token,
        ).execute()
        events.extend(result.get("items", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    print(f"[Google Calendar] Fetched {len(events)} events from Life calendar")
    return events


def format_event(gcal_event):
    """Format a Google Calendar event into a readable dict."""
    summary = gcal_event.get("summary", "(제목 없음)")
    start = gcal_event.get("start", {})
    end = gcal_event.get("end", {})

    # All-day: start["date"], Timed: start["dateTime"]
    if "date" in start:
        date_str = start["date"]
        end_str = end.get("date", date_str)
        return {
            "title": summary,
            "type": "all-day",
            "date": date_str,
            "end_date": end_str,
            "time": None,
            "description": gcal_event.get("description", ""),
            "location": gcal_event.get("location", ""),
            "id": gcal_event["id"],
        }
    elif "dateTime" in start:
        dt_str = start["dateTime"]
        # Parse ISO datetime
        dt_obj = datetime.fromisoformat(dt_str)
        date_str = dt_obj.strftime("%Y-%m-%d")
        time_str = dt_obj.strftime("%H:%M")

        end_dt_obj = datetime.fromisoformat(end.get("dateTime", dt_str))
        end_time_str = end_dt_obj.strftime("%H:%M")

        return {
            "title": summary,
            "type": "timed",
            "date": date_str,
            "end_date": date_str,
            "time": f"{time_str} ~ {end_time_str}",
            "description": gcal_event.get("description", ""),
            "location": gcal_event.get("location", ""),
            "id": gcal_event["id"],
        }

    return None


def sync(gcal_service):
    events = fetch_gcal_events(gcal_service)
    formatted = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for e in events:
        fmt = format_event(e)
        if fmt:
            formatted.append(fmt)

    # Sort by date, then time
    formatted.sort(key=lambda x: (x["date"], x["time"] or ""))

    # Save report
    report = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "source": f"Google Calendar [Life] (primary)",
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
    else:
        print("[DRY-RUN] Would save report")

    # Print summary
    print(f"\n📋 Life 캘린더 일정 ({today} 기준 ±{SYNC_DAYS_PAST}/{SYNC_DAYS_FUTURE}일)\n")
    for e in formatted:
        date_label = e["date"]
        time_label = e["time"] or "종일"
        location = f" 📍{e['location']}" if e["location"] else ""
        print(f"  📌 {date_label} {time_label} — {e['title']}{location}")

    print(f"\n총 {len(formatted)}건")
    return formatted


def main():
    if DRY_RUN:
        print("=== DRY RUN (no changes) ===\n")
    creds = load_google_credentials()
    gcal = build("calendar", "v3", credentials=creds)
    sync(gcal)


if __name__ == "__main__":
    main()
