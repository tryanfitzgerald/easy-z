# Easy Z Municipal Research Guide

## How to Research a Municipality (15-30 minutes each)

### Step 1: Find the Zoning Ordinance

Try these sources in order:

1. **Municode.com** — Search "[city name] [state] zoning"
2. **Sterling Codifiers** (sterlingcodifiers.com)
3. **American Legal Publishing** (amlegal.com)
4. **City website** → look for "Municipal Code" or "Zoning Ordinance" link

### Step 2: Find the Permitted Use Table

In the zoning code, look for the chapter called "Zoning" or "Land Use" and find the **Table of Permitted Uses** (sometimes called "Use Matrix" or "Schedule of Uses").

Search the document for these terms:
- "drive-through" or "drive-thru" or "drive-in"
- "automobile laundry" or "car wash" or "vehicle washing"

The table will show zoning districts across the top (B-1, B-2, C-1, etc.) and uses down the side. The cells contain:
- **P** = Permitted by right (best — score 18-20)
- **C** or **CU** = Conditional use (requires hearing — score 12-15)
- **S** or **SU** = Special use (harder — score 8-12)
- **PUD** = Planned unit development required (hardest — score 4-8)
- **Blank or X** = Not allowed (score 0-4)

**Record which districts allow each use and the approval pathway.**

### Step 3: Find Site Requirements

Search the code for "supplemental standards" or "additional requirements" for drive-throughs. Look for:

- **Stacking/queuing requirement** — How many cars must fit in the drive-thru lane? (Coffee concepts need short stacking. If they require 10+ cars, that's a problem.)
- **Lot size minimum** — Square footage or acreage needed
- **Setback requirements** — Front, side, rear in feet
- **Proximity restrictions** — Minimum distance from residential zones, schools, churches
- **Hours of operation limits** — Any restrictions on operating hours?
- **Traffic study** — Is one required?
- **Architectural review** — Does the design need board approval?

### Step 4: Check Approval History

Go to the city website → "Agendas & Minutes" → find **Planning Commission** or **Zoning Board of Appeals** minutes.

Search minutes from the last 3 years for "drive-through" or "car wash." Record:
- Project name and applicant
- Date
- Outcome (approved, approved with conditions, denied, tabled, withdrawn)
- Any conditions imposed

### Step 5: Count Competitors

Open Google Maps, zoom to the municipality, and search:
- "car wash" — count locations, note chain names
- "drive thru coffee" — count locations, note chain names
- Look specifically for: Dutch Bros, 7 Brew, Scooter's Coffee, Starbucks drive-thru, Dunkin' drive-thru

### Step 6: Score It

Open the research workbook (`data/easy_z_research_workbook.xlsx`) and fill in the **Zoning Research** sheet:

| Factor | 20 pts | 15 pts | 10 pts | 5 pts | 0 pts |
|--------|--------|--------|--------|-------|-------|
| **Zoning Code** | Permitted by right in multiple districts | Permitted in 1 district | Conditional use | Special use only | Prohibited |
| **Site Requirements** | No stacking req or ≤6 cars, standard setbacks | 6-8 car stacking, reasonable setbacks | 8-10 car stacking, some restrictions | 10-12 car stacking, heavy restrictions | 12+ cars or impossible requirements |
| **Approval Track Record** | 3+ approvals, 0 denials in 3 years | 2+ approvals, 0 denials | 1 approval, 0 denials | Mixed record | Denials or no applications (bad sign) |
| **Competitive Saturation** | 0-1 similar businesses | 2-3 similar businesses | 4-5 similar businesses | 6+ or recent saturation resistance | Active pushback due to oversaturation |
| **Political Temperature** | Very friendly board | Friendly/neutral | Neutral with some caution | Cautious/slow | Hostile or moratorium |

### Step 7: Rebuild the Map

After updating the workbook, run:
```bash
python3 scripts/xlsx_to_json.py
```
This rebuilds the JSON data and the HTML map automatically.

## Priority Research Order

**Tier A (research first)**: Population > 10,000 — these are your real markets
**Tier B (second wave)**: Population 5,000-10,000
**Tier C (as needed)**: Population < 5,000

Within each tier, prioritize by:
1. Municipalities you have active deal interest in
2. Collar counties around Chicago (Cook, DuPage, Lake, Will, Kane, McHenry)
3. Milwaukee metro (Milwaukee, Waukesha, Ozaukee, Washington counties)
4. Madison metro (Dane County)
5. NW Indiana (Lake, Porter, LaPorte counties)

## Tips

- **Don't trust the AI estimates.** They were generated from surface-level code analysis. Your 15 minutes of real research is worth more.
- **Check the meeting minutes.** The zoning code tells you what's technically possible. The minutes tell you what actually happens.
- **Note the political climate.** A town that just denied a drive-thru is very different from one that hasn't had an application in years.
- **Track your sources.** Put URLs in the Source columns so anyone can verify.
- **Log ground truth.** When you learn the actual outcome of a deal, add it to the Ground Truth sheet. This is how the model gets smarter.
