<div align="center">

# 🐆 WHOOP Dashboard

### Live WHOOP stats — strain, recovery, HRV, sleep

[![Live Site](https://img.shields.io/badge/🌐_Live_Site-whoop--dashboard-00e5cc?style=for-the-badge)](https://dacameragirl.github.io/whoop-dashboard/)
[![WHOOP](https://img.shields.io/badge/WHOOP-Auto--Updating-b794f6?style=for-the-badge)](https://developer.whoop.com/)
[![License](https://img.shields.io/badge/license-MIT-ff6b9d?style=flat-square)](LICENSE)

<img src="https://img.shields.io/github/actions/workflow/status/DaCameraGirl/whoop-dashboard/update.yml?label=auto--update&style=flat-square" alt="auto-update">
<img src="https://img.shields.io/badge/charts-Chart.js-00e5cc?style=flat-square" alt="Chart.js">
<img src="https://img.shields.io/badge/deploy-GitHub_Pages-b794f6?style=flat-square" alt="GitHub Pages">

<sub>Auto-updates daily at 10am ET · charts animate on load · dark teal/purple theme</sub>

</div>

---

## ✨ What's tracked

| Metric | What it means |
|---|---|
| **🔥 Strain** | Daily cardiovascular load — bar chart, color-coded by intensity |
| **💚 Recovery** | Recovery %, HRV (ms), resting heart rate — with trend lines |
| **😴 Sleep** | Sleep performance & efficiency per night |
| **💪 Workouts** | Logged training sessions with strain scores |

All animated, all responsive, all dark-mode-gorgeous.

---

## 🚀 Live site

### 👉 [dacameragirl.github.io/whoop-dashboard](https://dacameragirl.github.io/whoop-dashboard/)

---

## ⚙️ How it works

```
WHOOP API ──→ fetch_whoop.py ──→ data/whoop.json ──→ Chart.js dashboard
     ↑                                                      │
     │              ┌───────────────────────────────────────┘
     │              │
  GitHub Action (daily @ 14:00 UTC)
     │
     └── auto-commits fresh data → auto-deploys to Pages
```

Zero servers. Zero cost. Set it and forget it.

**Tech stack:**

- Vanilla HTML/CSS/JS — no framework bloat
- [Chart.js](https://www.chartjs.org/) — animated charts
- GitHub Actions — daily auto-update + Pages deploy
- Python `urllib` — WHOOP API client, zero dependencies

---

## 🔧 Setup (fork your own)

### 1. WHOOP developer app

Get API credentials at **[developer.whoop.com](https://developer.whoop.com/)**

You need:
- `WHOOP_CLIENT_ID`
- `WHOOP_CLIENT_SECRET`
- `WHOOP_ACCESS_TOKEN` *(generated via OAuth)*
- `WHOOP_REFRESH_TOKEN` *(generated via OAuth)*

### 2. GitHub Secrets

Fork this repo → **Settings → Secrets and variables → Actions** → add:

| Secret | Where to find it |
|---|---|
| `WHOOP_ACCESS_TOKEN` | OAuth flow |
| `WHOOP_REFRESH_TOKEN` | OAuth flow |
| `WHOOP_CLIENT_ID` | WHOOP dev dashboard |
| `WHOOP_CLIENT_SECRET` | WHOOP dev dashboard |

The fetch script auto-refreshes expired access tokens — just make sure the refresh token is set.

### 3. Enable GitHub Pages

**Settings → Pages → Source: GitHub Actions**

That's it. The Action runs daily at 14:00 UTC (~10am ET) and on every push.

Run it manually: **Actions tab → Update WHOOP Data → Run workflow**

---

## 💻 Local development

```bash
# 1. Set your WHOOP tokens
export WHOOP_ACCESS_TOKEN="..."
export WHOOP_REFRESH_TOKEN="..."
export WHOOP_CLIENT_ID="..."
export WHOOP_CLIENT_SECRET="..."

# 2. Fetch data
python scripts/fetch_whoop.py

# 3. Open in browser
open index.html
# or: python -m http.server 8000
```

No build step. No npm. Just a static site that slaps.

---

<div align="center">

### Built with 💚 🐆

**[Angela Hudson](https://github.com/DaCameraGirl)** · [@DaCameraGirl](https://github.com/DaCameraGirl)

*Track your recovery. Own your strain. Sleep like a champion.*

[![GitHub](https://img.shields.io/badge/GitHub-DaCameraGirl-181717?style=flat-square&logo=github)](https://github.com/DaCameraGirl)

</div>
