# EASY Z — PROGRAM ROADMAP & PUNCHLIST

**Program Owner:** T. Ryan Fitzgerald
**Organization:** Shorewood Development Group
**Created:** 2026.03.15
**Last Updated:** 2026.03.16
**Status:** Phase 2 complete, Phase 3 in progress

---

## PROGRAM SUMMARY

Easy Z is a nationwide municipal zoning friction map that scores every US incorporated place on how easy or hard it is to get zoning approval for car washes, drive-thrus, collision repair, and auto sales/service. The platform combines ground-truth research with AI-estimated scoring, live competitor data, and real-time zoning news intel.

---

## COMPLETED PHASES

### Phase 1: Foundation (Mar 15) — COMPLETE
- [x] Core map framework (Leaflet.js, Census TIGERweb API)
- [x] Initial 88 municipalities researched (IL, IN, WI)
- [x] Binary scoring model (permitted/conditional/prohibited)
- [x] Popup with zoning details per municipality
- [x] Search and zoom-to-municipality
- [x] Dark/Streets/Satellite basemap toggle
- [x] Data pipeline: xlsx workbook → JSON → HTML build

### Phase 2: Nationwide Scaling (Mar 15–16) — COMPLETE
- [x] Expanded from 3 states to all 50 states + DC
- [x] Auto-estimation engine for ~19,500 municipalities
- [x] Friction-adjusted 5-factor scoring model (Zoning, Process, Site, Competition, Political)
- [x] State-level regulatory friction for all 50 states
- [x] Population-based friction penalties
- [x] Affluence penalty for wealthy suburbs
- [x] Per-city adjustment parameters for fine-tuning
- [x] Parallel state loading (5 at a time via Promise.allSettled)
- [x] 4 use type layers: Car Wash, Drive-Thru, Collision Repair, Auto Sales

### Phase 3: Intelligence Layer (Mar 16) — COMPLETE
- [x] Competitor overlay via OpenStreetMap Overpass API
- [x] Brand-colored drive-thru markers (Starbucks, Dutch Bros, Dunkin, Seven Brews)
- [x] Competitor hover tooltips with name + address
- [x] Competitor click popups with phone, website, full address
- [x] Custom Leaflet pane for competitors (no event conflicts with polygons)
- [x] Debounced moveend reload with zoom-level gate (8+)
- [x] Address geocoding search (Nominatim)
- [x] Live zoning news feed in popups (Google News RSS)
- [x] Council minutes + ordinance quick-search links
- [x] Weekly automated ordinance monitoring (scheduled task)
- [x] Eazy-E inspired logo and branding
- [x] GitHub repo + GitHub Pages deployment
- [x] Info tooltip icons on all UI controls

---

## CURRENT PUNCHLIST

### High Priority — Next Sprint
- [x] Rename `municipal_zoning_heatmap.html` → `index.html` for GitHub Pages
- [ ] Research 50 more municipalities (expand ground-truth from 88 to 138)
- [ ] Add per-use-type Overpass queries for collision repair (currently uses generic `shop=car_repair`)
- [ ] Add real zoning map URLs for researched municipalities
- [ ] Test competitor overlay at scale (high-density metro areas)

### Medium Priority — v2 Features
- [ ] Parcel-level drill-down (click municipality → see individual parcels)
- [ ] Export to CSV/Excel (filtered municipality list with scores)
- [ ] Time-series tracking (score changes over time as ordinances update)
- [ ] Push notifications for ordinance changes in watchlist municipalities
- [ ] Mobile-responsive sidebar (currently optimized for desktop)
- [ ] Custom municipality watchlist / favorites
- [ ] Team collaboration features (shared research assignments)

### Low Priority — Future Vision
- [ ] Integration with Shorewood DDP (Due Diligence Platform)
- [ ] Property-level analysis (overlay available parcels for sale)
- [ ] Drive-time / trade area analysis per site
- [ ] Demographic overlay (income, traffic counts, population density)
- [ ] PDF report generation per municipality (one-pager for deal packages)
- [ ] API endpoint for programmatic access to scoring data
- [ ] Expand use types (gas station, storage facility, medical office, etc.)

---

## RESEARCH EXPANSION PLAN

### Priority States for Ground-Truth Research
Current: 88 municipalities across IL, IN, WI

| Priority | State | Target Count | Rationale |
|---|---|---|---|
| 1 | Texas | 30 | Low friction, high growth, major metros |
| 2 | Florida | 25 | High demand, diverse municipal structures |
| 3 | Arizona | 15 | Fast-growing, car-wash-friendly climate |
| 4 | Ohio | 15 | Midwest expansion, similar regulatory |
| 5 | Georgia | 15 | Southeast anchor, Atlanta metro |
| 6 | Tennessee | 10 | Business-friendly, growing metros |
| 7 | Colorado | 10 | Mountain West anchor |
| 8 | North Carolina | 10 | East coast growth corridor |

**Target:** 200+ ground-truth municipalities by end of Q2 2026

### Research Process
1. Identify target municipalities by population and market potential
2. Pull zoning ordinance from municipal website (Municode, American Legal, Sterling Codifiers)
3. Extract use-type-specific requirements per `docs/RESEARCH_GUIDE.md`
4. Enter data into `data/easy_z_research_workbook.xlsx`
5. Run build pipeline: `build_zoning_data_v5.py` → `build_html_map.py`
6. Commit and push to GitHub Pages

---

## SCORING MODEL HISTORY

| Version | Date | Model | Distribution |
|---|---|---|---|
| v1 | Mar 15 | Binary (permitted/prohibited) | 80% green, 15% yellow, 5% red |
| v2 | Mar 15 | Weighted 3-factor | 60% green, 25% yellow, 15% red |
| v3 | Mar 15 | 4 use types added | Same as v2 |
| v4 | Mar 15 | Population friction | 40% green, 35% yellow, 25% red |
| v5 | Mar 16 | 5-factor institutional model | 10% green, 43% lt green, 34% yellow, 12% orange |

v5 is the current production model. Score distributions are now realistic and differentiated.

---

## WEEKLY OPERATIONS

**Monday 8:00 AM** — Automated ordinance monitoring runs
- Searches Google News for zoning ordinance changes
- Checks city council agendas for zoning items
- Reports saved to `reports/` directory
- Flags municipalities where scores may need updating

**As-needed** — Manual research updates
- New municipalities added via workbook
- Score adjustments based on monitoring alerts
- Build pipeline re-run and deploy

---

**Program Status: ACTIVE**
**Next milestone:** 138 researched municipalities (50 additional)
