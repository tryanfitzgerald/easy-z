# Carwash Heat Map: 30-Day Execution Plan
## Quick-Start & Milestone Checklist

**Project:** Shorewood Development Group  
**Deliverable:** Interactive heat map (Friendly/NIMBY municipalities in IL/WI)  
**Timeline:** 30 days (parallel processing recommended to hit 15 days)  
**Status:** Ready to execute

---

## Week 1: Data Acquisition & Validation

### Day 1-2: Setup & Sample Testing
- [ ] Verify Python environment (`python3 --version`)
- [ ] Install dependencies: `pip install anthropic requests`
- [ ] Review target municipalities list: `data/target_municipalities.json` (98 total)
- [ ] Run ordinance fetch on sample (5 municipalities)
  ```bash
  # Edit data/target_municipalities.json to include only 5 cities
  python3 scripts/01_fetch_ordinances.py
  # Expected: 3-4 successful fetches out of 5 (sample validation)
  ```
- [ ] Check logs: `tail logs/ordinance_fetch.log`
- [ ] **GO/NO-GO DECISION**: If >60% success rate, proceed to full fetch

### Day 3-5: Full Ordinance Fetch
- [ ] Restore full municipalities list to `data/target_municipalities.json`
- [ ] Run full ordinance fetch (3-5 hours)
  ```bash
  python3 scripts/01_fetch_ordinances.py
  ```
- [ ] Monitor progress: `tail -f logs/ordinance_fetch.log`
- [ ] Check results: 
  ```bash
  cat output/ordinance_fetch_results.json | jq '.successful | length'
  # Expected: 60-80 successful fetches
  ```
- [ ] If <60% success: Manually research missing municipalities' websites, update base URLs

### Day 6-7: Parallel Processing Setup
- [ ] **While ordinances are downloading**, prepare for Stage 2 & 3
- [ ] Test Claude Vision parsing on 1-2 sample PDFs
  ```bash
  python3 scripts/02_parse_ordinances.py
  # Test on first few municipalities
  ```
- [ ] Test approval data scraping on 1-2 municipalities
  ```bash
  python3 scripts/03_scrape_approval_news.py
  # Edit script to process only 2 cities for testing
  ```
- [ ] Verify JSON output structure is valid
- [ ] **Resolve any API errors** before running full batch

---

## Week 2: Full Processing Pipeline

### Day 8-10: Ordinance Parsing (Claude Vision)
- [ ] Ensure ordinance fetch is complete (all PDFs downloaded)
- [ ] Run full ordinance parsing
  ```bash
  python3 scripts/02_parse_ordinances.py
  # Estimated: 2-3 hours
  ```
- [ ] Monitor: `tail -f logs/ordinance_parser.log`
- [ ] Check output:
  ```bash
  cat output/ordinance_extractions.json | jq '.[] | select(.success == true) | length'
  # Expected: 60-75 successful parses
  ```
- [ ] Review sample extraction:
  ```bash
  cat output/ordinance_extractions.json | jq '.[0]' | less
  # Verify structure: municipality, state, success, extracted_rules
  ```

### Day 10-14: Approval Data Scraping
- [ ] Run full approval/news data scraper (parallel with parsing if possible)
  ```bash
  python3 scripts/03_scrape_approval_news.py
  # Estimated: 4-6 hours
  ```
- [ ] Monitor: `tail -f logs/news_scraper.log`
- [ ] Check output:
  ```bash
  cat output/approval_data.json | jq '.[] | select(.success == true) | .approvals_found' | paste -sd+ | bc
  # Expected: 20-50 total approval records across all municipalities
  ```
- [ ] **Validation**: Spot-check 3-5 municipalities manually
  - Verify approval records match known projects in those towns
  - If major discrepancies, flag for manual review

### Day 15: Scoring & Heat Map Generation
- [ ] Ensure both ordinance + approval data are complete
- [ ] Run scoring engine
  ```bash
  python3 scripts/04_scoring_engine.py
  # Estimated: 30 min
  ```
- [ ] Monitor: `tail logs/scoring_engine.log`
- [ ] Verify output:
  ```bash
  cat output/heat_map_scores.json | jq '.metadata'
  # Check: friendly_count, nimby_count, total_municipalities
  ```
- [ ] Spot-check scores:
  ```bash
  cat output/heat_map_scores.json | jq '.friendly_municipalities[0:5]'
  # Review top 5 friendly municipalities
  ```

---

## Week 3: Validation & Deployment

### Day 16-20: Validation Against Known Projects
- [ ] Compare heat map to your known deal history
  - **Known friendly towns** (where you got approvals): Should score 70+
  - **Known NIMBY towns** (where you got denied): Should score <40
  - **Examples**:
    - Madison, WI: Should be FRIENDLY (known as approving)
    - Evanston, IL: Should be NIMBY (known as restrictive)
- [ ] If major discrepancies:
  - [ ] Manually review ordinance extraction for that municipality
  - [ ] Manually verify approval data (check local news)
  - [ ] Adjust scoring weights if systematic bias detected
- [ ] Document any manual corrections

### Day 21-24: Interactive Map Deployment
- [ ] Test map locally:
  ```bash
  cd output
  python3 -m http.server 8000
  # Open: http://localhost:8000/index.html
  ```
- [ ] Verify all features:
  - [ ] Map loads with all municipalities
  - [ ] Click on municipality, see popup with score + data
  - [ ] Sidebar shows top 5 friendly municipalities
  - [ ] Filters work (show/hide Friendly/Neutral/NIMBY)
  - [ ] Stats update correctly
  - [ ] Responsive design on mobile (resize browser)
- [ ] Customize map (optional):
  - [ ] Update header/title with your branding
  - [ ] Change color scheme if desired
  - [ ] Add company logo
- [ ] Deploy to web server (if applicable)
  ```bash
  scp output/index.html output/heat_map_scores.json user@server:/var/www/html/carwash-map/
  ```

### Day 25-28: Documentation & Training
- [ ] Create internal documentation:
  - [ ] "Top Friendly Municipalities" spreadsheet (export from JSON)
  - [ ] "NIMBY-Adjacent Opportunities" map layer (border properties)
  - [ ] "Approval Timeline Benchmarks" (from approval_data.json)
- [ ] Train deal sourcing team on using heat map
  - [ ] How to identify Friendly vs. NIMBY municipalities
  - [ ] How to use NIMBY-adjacent strategy
  - [ ] How to interpret scores and recommendations
- [ ] Set up weekly update process:
  - [ ] Cron job to re-run scraper weekly
  - [ ] Process to incorporate new deal data back into system

### Day 29-30: Refinement & Handoff
- [ ] Final QA:
  - [ ] All links in map work
  - [ ] No broken data fields
  - [ ] Performance acceptable (map loads <2 seconds)
- [ ] Create summary report:
  - [ ] Top 10 Friendly municipalities
  - [ ] Top 10 NIMBY municipalities
  - [ ] Underserved opportunities (Friendly + 0 existing carwashes)
  - [ ] NIMBY-adjacent border properties to scout
- [ ] Handoff to deal sourcing team
- [ ] Schedule 2-week follow-up review

---

## Go/No-Go Checkpoints

### Day 7 (Sample Testing)
**Checkpoint:** Ordinance fetch success rate on sample 5 municipalities  
- **GO**: ≥4/5 successful downloads (80%)
- **NO-GO**: <3/5 successful — identify URL pattern issues, update base URLs
- **Action if NO-GO**: Manual research of failing municipalities' websites

### Day 10 (Ordinance Parsing)
**Checkpoint:** Claude Vision parsing success rate  
- **GO**: ≥60 municipalities with extracted rules
- **NO-GO**: <50 successful parses — check for API errors, PDF format issues
- **Action if NO-GO**: Debug 5 failing ordinances, adjust parsing prompt if needed

### Day 15 (Scoring)
**Checkpoint:** Heat map generated with valid scores for all municipalities  
- **GO**: All municipalities have friendliness_score (0-100)
- **NO-GO**: >10% missing or null scores
- **Action if NO-GO**: Investigate missing data sources, fill gaps

### Day 20 (Validation)
**Checkpoint:** Heat map validates against known projects  
- **GO**: Known friendly towns score 65+, known NIMBY towns score <40
- **NO-GO**: Systematic bias detected
- **Action if NO-GO**: Adjust scoring weights or investigate data quality issues

### Day 24 (Map Deployment)
**Checkpoint:** Interactive map fully functional and deployed  
- **GO**: Map loads without errors, all features work, responsive design confirmed
- **NO-GO**: Bugs or performance issues
- **Action if NO-GO**: Debug and retest

---

## Daily Tracking Template

Use this to track progress each day:

```
DATE: [Day X]
TASK: [Stage/Step]
STATUS: [ ] Started [ ] In Progress [ ] Complete
TIME SPENT: [X hours]
OUTPUT GENERATED: [File path or count]
BLOCKERS: [Any issues?]
NEXT STEPS: [What's next?]
```

---

## Estimated Timeline (with parallelization)

| Phase | Days | Duration | Effort |
|-------|------|----------|--------|
| Setup + Sample Testing | 1-7 | 7 days | 4 hrs/day |
| Full Ordinance Fetch | 3-5 | (parallel with above) | 2 hrs/day |
| Ordinance Parsing | 8-10 | 3 days | 1 hr/day (monitoring) |
| Approval Scraping | 8-14 | (parallel with parsing) | 1 hr/day (monitoring) |
| Scoring | 15 | 1 day | 0.5 hrs |
| Validation | 16-20 | 5 days | 2 hrs/day |
| Deployment | 21-24 | 4 days | 3 hrs/day |
| Training + Handoff | 25-30 | 6 days | 2 hrs/day |
| **TOTAL** | **30 days** | **14 working days** | **~100 hours** |

**If run in sequence (non-parallel):** 30-35 days  
**With parallelization:** 14-18 days ✅

---

## Risk Mitigation

### Risk: Ordinance fetch fails for many municipalities
**Probability:** Medium (30-40% of municipalities don't post ordinances online)  
**Mitigation:**
- Build comprehensive base URL database upfront
- Set up fallback: County Assessor, State archives, Internet Archive
- Manual research for critical municipalities (top 20 by deal volume)

### Risk: Claude Vision parsing produces gibberish
**Probability:** Low (5-10% of ordinances)  
**Mitigation:**
- Pre-test on 5 sample PDFs
- If >20% fail, adjust parsing prompt or pre-process PDFs (OCR)
- Manual review of failed extractions

### Risk: No approval data found for a municipality
**Probability:** Medium (30-50% may have no recent projects)  
**Mitigation:**
- Assume "no approval data" = "neutral" scoring (default 50)
- For critical municipalities, manual phone research (call planning dept)
- Consider: No approvals ≠ No carwashes; some municipalities may have older projects

### Risk: Heat map validation fails (scores don't match known projects)
**Probability:** Low (10-20%)  
**Mitigation:**
- Validate against top 10 municipalities you know well
- Adjust scoring weights if systematic bias
- Document any manual corrections
- Don't delay deployment; iterate post-launch

### Risk: Pipeline takes longer than 30 days
**Probability:** Medium (40-50%)  
**Mitigation:**
- Start with parallel processing from day 1
- Automate everything; eliminate manual steps
- If falling behind: Focus on top 50 municipalities first (Cook + Milwaukee + Madison counties), expand later

---

## Success Criteria

By Day 30, you should have:

✅ **Interactive heat map** displaying all 80-100 municipalities color-coded by friendliness  
✅ **Data validated** against known projects (spot-checks confirm accuracy)  
✅ **Top 10 friendly municipalities identified** and ready for sourcing  
✅ **NIMBY-adjacent opportunities** identified (border properties)  
✅ **Sourcing team trained** on using the heat map  
✅ **Weekly update process** in place (refresh data every 7 days)  
✅ **Documentation complete** (how to use, score definitions, recommendations)  

---

## Sample Output

### Heat Map Statistics (Expected)
```
Total Municipalities: 98
Friendly (67-100): 20-25
Neutral (34-66): 40-50
NIMBY (0-33): 25-30
```

### Sample Top 5 Friendly Municipalities
```
1. Madison, WI - Score: 82 (FRIENDLY)
   Approvals: 3/3 (100%), Ordinance: 85, Sentiment: LOW_NIMBY
   Recommendation: HIGH PRIORITY - Green-light sourcing

2. Fitchburg, WI - Score: 78 (FRIENDLY)
   Approvals: 2/2 (100%), Ordinance: 80, Sentiment: LOW_NIMBY
   Recommendation: HIGH PRIORITY - Consider saturation

3. Middleton, WI - Score: 75 (FRIENDLY)
   Approvals: 2/2 (100%), Ordinance: 78, Sentiment: MEDIUM_NIMBY
   Recommendation: GREEN-LIGHT - Active sourcing

[... etc]
```

### Sample NIMBY-Adjacent Opportunities
```
High-Risk Adjacent to Low-Risk:
- Properties bordering Evanston, IL (NIMBY) in Skokie, IL (FRIENDLY)
- Properties bordering Chicago, IL (NEUTRAL) in Oak Park, IL (FRIENDLY)
- Properties bordering Wauwatosa, WI (NIMBY) in Brookfield, WI (FRIENDLY)
[... etc]
```

---

## Questions?

**Technical issues?** Check logs in `/logs/` directory  
**Data quality concerns?** Cross-reference manual with `output/` JSON files  
**Deployment help?** See README.md for full documentation  
**Timeline concerns?** Parallelize; prioritize top 50 municipalities first  

**Let's go.** You've got 30 days. Execute.

---

**Document Version:** 1.0  
**Last Updated:** 2026.03.14  
**Status:** READY TO EXECUTE
