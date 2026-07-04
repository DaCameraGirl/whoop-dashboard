# WHOOP Dashboard 🐆

Live WHOOP stats dashboard — auto-updates daily.

**Live site:** https://dacameragirl.github.io/whoop-dashboard/

![WHOOP](https://img.shields.io/badge/WHOOP-connected-00e5cc)

## What's tracked

- **Strain** — daily cardiovascular load
- **Recovery** — recovery %, HRV, resting heart rate
- **Sleep** — sleep performance & efficiency
- **Workouts** — logged training sessions

Charts built with [Chart.js](https://www.chartjs.org/).

## How it works

1. `scripts/fetch_whoop.py` pulls data from the WHOOP API
2. Data is saved to `data/whoop.json`
3. `index.html` renders charts from that JSON
4. GitHub Action runs daily, fetches fresh data, commits, deploys to Pages

Fully automated. Set it and forget it.

## Setup (for your own fork)

### 1. WHOOP API credentials

You need a WHOOP developer app: https://developer.whoop.com/

You'll need:
- `WHOOP_CLIENT_ID`
- `WHOOP_CLIENT_SECRET`
- `WHOOP_ACCESS_TOKEN`
- `WHOOP_REFRESH_TOKEN`

### 2. GitHub Secrets

In your fork, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `WHOOP_ACCESS_TOKEN` | your access token |
| `WHOOP_REFRESH_TOKEN` | your refresh token |
| `WHOOP_CLIENT_ID` | your client ID |
| `WHOOP_CLIENT_SECRET` | your client secret |

The fetch script auto-refreshes expired access tokens using the refresh token.

### 3. Enable GitHub Pages

Settings → Pages → Source: **GitHub Actions**

### 4. Run it

- Manual: Actions tab → "Update WHOOP Data" → Run workflow
- Automatic: runs daily at 14:00 UTC (~10am ET)

## Local development

```bash
# 1. Set your WHOOP tokens
export WHOOP_ACCESS_TOKEN="..."
export WHOOP_REFRESH_TOKEN="..."
export WHOOP_CLIENT_ID="..."
export WHOOP_CLIENT_SECRET="..."

# 2. Fetch data
python scripts/fetch_whoop.py

# 3. Open index.html in a browser
# (or: python -m http.server 8000)
```

No build step. No npm. Just a static site.

## Tech stack

- Vanilla HTML/CSS/JS — no framework bloat
- Chart.js — charts
- GitHub Actions — daily auto-update + Pages deploy
- Python — WHOOP API client (`urllib` only, zero dependencies)

---

Built with 🐆 by [DaCameraGirl](https://github.com/DaCameraGirl)
