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

    # --- Clean up data ---
    # Filter out invalid cycles (strain=0, hr=0 = bogus/incomplete records)
    def is_valid_cycle(c):
        s = c.get("score", {})
        strain = s.get("strain", 0)
        hr = s.get("average_heart_rate", 0)
        return strain > 0.5 and hr > 30

    cycles_before = len(cycles)
    cycles = [c for c in cycles if is_valid_cycle(c)]
    print(f"Filtered cycles: {cycles_before} → {len(cycles)} (removed {cycles_before - len(cycles)} invalid)", file=sys.stderr)

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

    # --- Generate flat CSV for Google Sheets export ---
    rec_map = {r.get("cycle_id"): r for r in out["recovery"]}
    sleep_map = {}
    for s in out["sleep"]:
        cid = s.get("cycle_id")
        if cid not in sleep_map:
            sleep_map[cid] = s
    rows = []
    for c in out["cycles"]:
        cid = c["id"]
        r = rec_map.get(cid, {}).get("score", {})
        s = sleep_map.get(cid, {}).get("score", {})
        stage = s.get("stage_summary", {})
        sleep_hrs = sum(stage.values()) / 3600000 if stage else None
        rows.append([
            c["start"][:10],
            round(c["score"]["strain"], 2),
            c["score"]["average_heart_rate"],
            c["score"]["max_heart_rate"],
            round(c["score"]["kilojoule"], 0),
            r.get("recovery_score", ""),
            round(r.get("hrv_rmssd_milli", 0), 1) if r.get("hrv_rmssd_milli") else "",
            r.get("resting_heart_rate", ""),
            round(sleep_hrs, 2) if sleep_hrs else "",
            s.get("sleep_efficiency_percentage", ""),
            s.get("sleep_performance_percentage", ""),
        ])
    with open("data/whoop.csv", "w") as f:
        f.write("Date,Strain,Avg HR,Max HR,KJ,Recovery %,HRV,RHR,Sleep Hrs,Sleep Eff %,Sleep Perf %\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print(f"Wrote data/whoop.csv — {len(rows)} rows", file=sys.stderr)

if __name__ == "__main__":
    main()
