#!/usr/bin/env python3
"""Fetch WHOOP data and write data/whoop.json for the dashboard."""
import os, json, sys
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import urllib.error

API_BASE = "https://api.prod.whoop.com/developer/v2"
UA = "whoop-cli/1.0"

def refresh_token(refresh_token, client_id, client_secret):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "offline",
    }).encode()
    req = urllib.request.Request("https://api.prod.whoop.com/oauth/oauth2/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["access_token"]

def api_get(path, token, params=None):
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {path}: {body[:200]}")

def paginate(path, token, key="records", limit=25, max_pages=20):
    out = []
    next_token = None
    for _ in range(max_pages):
        params = {"limit": limit}
        if next_token:
            params["nextToken"] = next_token
        data = api_get(path, token, params)
        batch = data.get(key, [])
        out.extend(batch)
        next_token = data.get("next_token")
        if not next_token or not batch:
            break
    return out

def main():
    refresh_tok = os.environ.get("WHOOP_REFRESH_TOKEN")
    client_id = os.environ.get("WHOOP_CLIENT_ID")
    client_secret = os.environ.get("WHOOP_CLIENT_SECRET")
    access_token = os.environ.get("WHOOP_ACCESS_TOKEN")

    if refresh_tok and client_id and client_secret:
        try:
            access_token = refresh_token(refresh_tok, client_id, client_secret)
            print(f"Refreshed access token", file=sys.stderr)
        except Exception as e:
            print(f"Refresh failed: {e}, using existing access_token", file=sys.stderr)

    if not access_token:
        print("ERROR: No WHOOP access token", file=sys.stderr)
        sys.exit(1)

    def try_fetch(path, label):
        try:
            data = paginate(path, access_token)
            print(f"{label}: {len(data)} records", file=sys.stderr)
            return data
        except Exception as e:
            print(f"{label} failed: {e}", file=sys.stderr)
            return []

    cycles = try_fetch("/cycle", "cycles")
    recovery = try_fetch("/recovery", "recovery")
    sleep = try_fetch("/activity/sleep", "sleep")
    workouts = try_fetch("/activity/workout", "workouts")

    if not cycles and not recovery and not sleep and not workouts:
        print("All fetches failed — keeping existing data/whoop.json", file=sys.stderr)
        sys.exit(0)

    def sort_key(x):
        return x.get("start") or x.get("created_at") or ""
    for lst in (cycles, recovery, sleep, workouts):
        lst.sort(key=sort_key, reverse=True)
        del lst[100:]

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycles": list(reversed(cycles)),
        "recovery": list(reversed(recovery)),
        "sleep": list(reversed(sleep)),
        "workouts": list(reversed(workouts)),
    }
    os.makedirs("data", exist_ok=True)
    with open("data/whoop.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote data/whoop.json — {len(cycles)}c {len(recovery)}r {len(sleep)}s {len(workouts)}w", file=sys.stderr)

if __name__ == "__main__":
    main()
