#!/usr/bin/env python3
"""보유 Steam 게임 목록을 ~/.local/share/steam/my-steam-games.json으로 재생성.

키 로드: STEAM_API_KEY/STEAM_USER_ID 환경변수 우선, 없으면 ~/.config/steam/.env.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "steam" / ".env"
OUT_FILE = Path.home() / ".local" / "share" / "steam" / "my-steam-games.json"


def load_env_file(path: Path) -> None:
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    if not os.environ.get("STEAM_API_KEY") and ENV_FILE.exists():
        load_env_file(ENV_FILE)

    key = os.environ.get("STEAM_API_KEY")
    uid = os.environ.get("STEAM_USER_ID")
    if not key or not uid:
        print("STEAM_API_KEY/STEAM_USER_ID 없음. ~/.config/steam/.env를 확인.", file=sys.stderr)
        return 1

    url = (
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        f"?key={key}&steamid={uid}&include_appinfo=true&include_played_free_games=true&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "zzizily-trackers/2.0.1"})
    data = json.load(urllib.request.urlopen(req, timeout=15))

    games = data.get("response", {}).get("games", [])
    if not games:
        print("응답에 게임 없음 — 키 또는 steamid 확인 필요", file=sys.stderr)
        return 1

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False))
    print(f"저장: {OUT_FILE} ({len(games)}게임)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
