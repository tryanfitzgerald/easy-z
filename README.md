# EASY Z — Nationwide Municipal Zoning Friction Map

**Shorewood Development Group**
Live: [tryanfitzgerald.github.io/easy-z](https://tryanfitzgerald.github.io/easy-z)
Repo: [github.com/tryanfitzgerald/easy-z](https://github.com/tryanfitzgerald/easy-z)

---

## What It Does

Easy Z is an interactive map that scores every incorporated municipality in the United States on how easy or hard it is to get zoning approval for four commercial use types:

- **Car Wash** — express tunnel, flex-serve, self-serve
- **Drive-Thru** — coffee (Starbucks, Dutch Bros, Dunkin, Seven Brews), QSR
- **Collision Repair** — auto body, paint shops
- **Auto Sales/Service/Delivery** — dealerships, service centers

Each municipality gets a **friction score from 0–100** based on five institutional-grade factors: Zoning permissiveness, Process complexity, Site requirements, Competition saturation, and Political risk.

---

## Key Features

**Scoring Engine**
- Friction-adjusted 5-factor model inspired by institutional underwriting (Zoning, Process, Site, Competition, Political — each 0–20)
- 88 ground-truth researched municipalities (IL, IN, WI) with real ordinance data
- Auto-estimation engine for all ~19,500 US incorporated places using population, state friction, and affluence signals
- Color scale: Green (80+) → Light green (65–79) → Yellow (50–64) → Orange (30–49) → Red (<30)

**Interactive Map**
- Leaflet.js with Canvas renderer for nationwide polygon performance
- US Census TIGERweb API for municipal boundaries (loaded in parallel, 5 states at a time)
- Click any municipality for detailed popup: score breakdown, approval pathway, zone districts, special use permit status, site requirements, stacking minimums
- Three basemap options: Dark, Streets, Satellite
- Address geocoding search (Nominatim/OpenStreetMap)
- Municipality name search with score preview

**Competitor Overlay**
- Toggle to show existing businesses from OpenStreetMap (Overpass API)
- Auto-reloads on pan/zoom (debounced, zoom 8+ required)
- Drive-thru layer is brand-colored: Starbucks (green), Dutch Bros (blue), Dunkin (orange), Seven Brews (burgundy), others (gray)
- Hover for name + address, click for full detail card with phone/website

**Zoning Intel**
- Live news feed in every municipality popup (Google News RSS)
- Dual search: zoning news + city council minutes/agendas
- Quick-link buttons: News, Council Minutes, Ordinances
- Weekly automated ordinance monitoring (scheduled task, runs Mondays 8am)

---

## Project Structure

```
Easy Z/
├── index.html                          # Interactive map (main deliverable, self-contained)
├── data/
│   ├── zoning_data.json                # 88 researched municipalities with per-use scoring
│   ├── easy_z_research_workbook.xlsx   # 6-sheet team research workbook
│   └── content_hashes.json             # Data integrity checksums
├── scripts/
│   ├── build_zoning_data_v5.py         # Current data builder (friction-adjusted 5-factor model)
│   ├── build_html_map.py               # HTML assembler (injects JSON data into map template)
│   ├── xlsx_to_json.py                 # Workbook-to-JSON pipeline
│   ├── weekly_refresh.py               # Automated data refresh script
│   └── build_zoning_data_v[1-4].py     # Previous model iterations (archived)
├── docs/
│   ├── EASY_Z_PROGRAM_ROADMAP.md       # Strategic roadmap and punchlist
│   └── RESEARCH_GUIDE.md               # Team guide for adding new municipalities
├── reports/                            # Weekly ordinance monitoring reports (auto-generated)
└── logs/                               # Refresh and pipeline logs
```

---

## How to Add a Municipality

1. Open `data/easy_z_research_workbook.xlsx`
2. Fill in the municipality row: zoning districts, approval pathway, special use requirements, stacking, site requirements
3. Run `python3 scripts/build_zoning_data_v5.py` to regenerate `zoning_data.json`
4. Run `python3 scripts/build_html_map.py` to rebuild the map
5. See `docs/RESEARCH_GUIDE.md` for detailed field definitions

---

## Tech Stack

- **Frontend:** Leaflet.js, vanilla JS, CSS — single self-contained HTML file (~140KB)
- **Data:** US Census TIGERweb ArcGIS REST API (boundaries), OpenStreetMap Overpass API (competitors), Nominatim (geocoding), Google News RSS (intel)
- **Build tools:** Python 3 (data pipeline), Node.js (syntax validation)
- **Hosting:** GitHub Pages (static, free)
- **Monitoring:** Weekly scheduled task via Claude (ordinance change detection)

No API keys required. Everything uses free public APIs.

---

## Deployment

The map is deployed via GitHub Pages. To update:

```bash
# After making changes to data or code:
python3 scripts/build_zoning_data_v5.py    # Rebuild scoring data
python3 scripts/build_html_map.py          # Rebuild HTML map
git add -A && git commit -m "Update"
git push
```

Changes go live within ~60 seconds of pushing.

---

## Scoring Methodology

Each municipality is scored on five factors (0–20 each, summed to 0–100):

| Factor | What It Measures |
|---|---|
| **Zoning** | Is the use permitted by right, conditional, special use, or prohibited? |
| **Process** | How long and complex is the approval process? Public hearings, plan commission, board votes? |
| **Site** | Lot size minimums, setbacks, stacking requirements, landscaping, screening? |
| **Competition** | Market saturation — how many existing competitors per capita? |
| **Political** | Council disposition, NIMBY risk, recent denials, moratoriums? |

Friction adjustments are applied based on population (bigger = more friction), state regulatory environment (CA highest, TX/IN lowest), and affluence (wealthy suburbs get political penalty).

---

**Built by Shorewood Development Group**
**Last updated:** March 2026
