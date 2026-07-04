#!/usr/bin/env python3
"""Fetch WHOOP data and write data/whoop.json for the dashboard."""
import os, json, sys
from datetime import datetime, timedelta, timezone
import urllib.request
import urllib.parse

def api_get(path, token, params=None):
    url = f"https://api.prod.whoop.com/developer/v2{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

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
    # get tokens from env (GitHub Secrets in CI, local env otherwise)
    access_token = os.environ.get("WHOOP_ACCESS_TOKEN")
    refresh_token = os.environ.get("WHOOP_REFRESH_TOKEN")
    client_id = os.environ.get("WHOOP_CLIENT_ID")
    client_secret = os.environ.get("WHOOP_CLIENT_SECRET")

    if not access_token and refresh_token and client_id and client_secret:
        print("Access token missing, refreshing...", file=sys.stderr)
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "offline read:recovery read:cycles read:sleep read:workout read:body_measurement",
        }).encode()
        req = urllib.request.Request("https://api.prod.whoop.com/oauth/oauth2/token", data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=10) as r:
            tok = json.loads(r.read())
        access_token = tok["access_token"]
        print(f"Refreshed access token (expires in {tok.get('expires_in')}s)", file=sys.stderr)

    if not access_token:
        print("ERROR: WHOOP_ACCESS_TOKEN not set and refresh failed", file=sys.stderr)
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

    # sort newest first, keep last 60 days worth
    def sort_key(x):
        return x.get("start") or x.get("created_at") or ""
    cycles.sort(key=sort_key, reverse=True)
    recovery.sort(key=sort_key, reverse=True)
    sleep.sort(key=sort_key, reverse=True)
    workouts.sort(key=sort_key, reverse=True)

    # trim to ~60 days / 100 items max each to keep JSON small
    cycles = cycles[:100]
    recovery = recovery[:100]
    sleep = sleep[:100]
    workouts = workouts[:100]

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycles": list(reversed(cycles)),  # oldest first for charts
        "recovery": list(reversed(recovery)),
        "sleep": list(reversed(sleep)),
        "workouts": list(reversed(workouts)),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/whoop.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote data/whoop.json — {len(cycles)} cycles, {len(recovery)} recovery, {len(sleep)} sleep, {len(workouts)} workouts", file=sys.stderr)

if __name__ == "__main__":
    main()
