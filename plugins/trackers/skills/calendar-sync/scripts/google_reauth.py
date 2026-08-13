#!/usr/bin/env python3
"""Google OAuth 재인증 (refresh token 만료/폐기 시).

두 가지 모드:

1) 수동 모드 (기본, Hermes 세션 안에서 실행 가능):
   /opt/data/.venv/bin/python /opt/data/skills/calendar-sync/scripts/google_reauth.py
   - 출력되는 URL을 브라우저에서 열어 동의
   - 리다이렉트 후 localhost 연결 실패 화면이 떠도 OK
   - 주소창의 전체 URL (http://localhost:8085/?code=...)을 복사해서 붙여넣기

2) 서버 모드 (SSH 터널 있을 때):
   로컬 PC: ssh -L 8085:localhost:8085 brla
   /opt/data/.venv/bin/python /opt/data/skills/calendar-sync/scripts/google_reauth.py --serve
"""

import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET = "/opt/data/.hermes/secret/google_client_secret.json"
TOKEN_PATH = "/opt/data/google_token.json"
PORT = 8085
REDIRECT_URI = f"http://localhost:{PORT}/"

# 기존 토큰의 스코프를 그대로 재사용 (없으면 기본 calendar + gmail.modify)
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
]


def load_scopes():
    real = os.path.realpath(TOKEN_PATH)
    if os.path.exists(real):
        try:
            scopes = json.load(open(real)).get("scopes")
            if scopes:
                return scopes
        except Exception:
            pass
    return DEFAULT_SCOPES


def save_token(creds, scopes):
    installed = json.load(open(CLIENT_SECRET)).get("installed", {})
    data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": installed.get("token_uri", "https://oauth2.googleapis.com/token"),
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or scopes),
    }
    real = os.path.realpath(TOKEN_PATH)
    with open(real, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(real, 0o600)
    print(f"\n[OK] 새 토큰 저장: {TOKEN_PATH}", flush=True)


def manual_mode(flow, scopes):
    flow.redirect_uri = REDIRECT_URI
    url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="false",
        prompt="consent",
    )
    print("=" * 60, flush=True)
    print("브라우저에서 이 URL을 여세요:\n", flush=True)
    print(url, flush=True)
    print("\n동의 후 주소창 URL 전체를 복사해서 붙여넣으세요.", flush=True)
    print("(localhost 연결 실패 화면이 떠도 주소만 복사하면 됨)", flush=True)
    print("=" * 60, flush=True)
    pasted = input("URL 붙여넣기: ").strip()
    # 붙여넣은 URL에서 code 추출 (전체 URL이든 code만이든 처리)
    code = pasted
    if "code=" in pasted:
        from urllib.parse import parse_qs, urlparse
        code = parse_qs(urlparse(pasted).query)["code"][0]
    flow.fetch_token(code=code)
    save_token(flow.credentials, scopes)


def serve_mode(flow, scopes):
    print(f"[Port] localhost:{PORT} — ssh -L {PORT}:localhost:{PORT} brla 필요\n", flush=True)
    creds = flow.run_local_server(
        port=PORT,
        open_browser=False,
        authorization_prompt_message="브라우저에서 이 URL을 여세요:\n\n{url}\n",
    )
    save_token(creds, scopes)


def main():
    scopes = load_scopes()
    print(f"[Scopes] {', '.join(scopes)}", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, scopes=scopes)
    if "--serve" in sys.argv:
        serve_mode(flow, scopes)
    else:
        manual_mode(flow, scopes)
    print("이제 gcal_to_hermes.py를 다시 실행하세요.", flush=True)


if __name__ == "__main__":
    main()
