# Option A: URL Research Guide
## Quick 30-City Zoning Ordinance URL Lookup (15 minutes)

**Goal:** Find zoning ordinance URLs for 30 key municipalities  
**Time:** 15 minutes total (30 seconds per city)  
**Difficulty:** Very easy (mostly Google searches + copy/paste)  
**Output:** 30 URLs to add to script

---

## The 30 Cities to Research

### Illinois (15 cities)
1. Chicago
2. Evanston
3. Oak Park
4. Skokie
5. Des Plaines
6. Downers Grove
7. Naperville
8. Aurora
9. Schaumburg
10. Arlington Heights
11. Palatine
12. Park Ridge
13. Cicero
14. Oak Lawn
15. Berwyn

### Wisconsin (15 cities)
1. Madison
2. Milwaukee
3. Brookfield
4. Waukesha
5. Green Bay
6. Fitchburg
7. Verona
8. Sun Prairie
9. Wauwatosa
10. Shorewood
11. Oak Creek
12. Middleton
13. Dane
14. Mequon
15. Glendale

---

## How to Research Each City (30 seconds per city)

### Step 1: Google Search
**Open Google and search:**
```
[city name] zoning ordinance PDF
```

Examples:
- `Chicago zoning ordinance PDF`
- `Madison zoning ordinance PDF`
- `Milwaukee zoning ordinance PDF`

### Step 2: Find the Best URL
Look for:
- ✅ **Direct PDF links** (best - easiest to use)
  - Example: `https://www.chicago.gov/zoning-ordinance.pdf`
  
- ✅ **City zoning pages** (good - contains the ordinance)
  - Example: `https://www.chicago.gov/departments/planning/zoning`
  
- ✅ **Municode pages** (OK - searchable municipal codes)
  - Example: `https://library.municode.com/il/chicago/codes`
  
- ❌ **Avoid:** Generic city home pages without a direct zoning link

### Step 3: Copy the URL
- Copy the best URL you found
- Add it to your list (see Format section below)

**That's it. 30 seconds. Next city.**

---

## Search Tips for Hard-to-Find Cities

If Google doesn't immediately show a zoning ordinance:

### Tip 1: Try the City Website Directly
```
site:chicago.gov zoning ordinance
```
This searches Google but only within that city's domain.

### Tip 2: Look for "Municipal Code" or "City Code"
Sometimes municipalities call it:
- "Municipal Code"
- "City Code" 
- "City Ordinance"
- "Code of Ordinances"

### Tip 3: Check Planning/Zoning Department Page
Search for: `[city] planning department zoning`

These pages usually link to the ordinance directly.

### Tip 4: Try Municode Directly
If a city has posted on Municode, search:
```
site:library.municode.com [city name]
```

### Tip 5: Look for County Resources
Some counties host municipal ordinances. Try:
```
[county name] county zoning ordinances
```

---

## URL Formatting

**Keep it simple. Here's the format you'll use:**

```python
base_urls = {
    "Chicago": "https://www.chicago.gov/zoning-ordinance",
    "Madison": "https://www.cityofmadison.com/planning/zoning-code",
    "Milwaukee": "https://city.milwaukee.gov/zoning/ordinance",
    # ... add 27 more in this format
}
```

**Notes:**
- City name must exactly match the name in `target_municipalities.json`
- URL can be direct PDF or a zoning page (system handles both)
- Include `https://` but don't worry about trailing slashes
- The system will try multiple patterns on these URLs

---

## Expected Results by City

Here's what you'll typically find:

### Easy Cities (Direct PDFs Found)
- **Chicago** → Direct PDF on chicago.gov
- **Madison** → Direct PDF on cityofmadison.com
- **Milwaukee** → Zoning page on city.milwaukee.gov
- **Naperville** → Usually has direct PDF
- **Evanston** → Check cityofevanston.org

### Moderate Cities (Zoning Pages)
- **Skokie** → Zoning page skokie.org
- **Des Plaines** → Zoning on desplaines.org
- **Brookfield** → Zoning on brookfieldwis.us

### Harder Cities (Municode or County)
- **Small suburbs** → May need Municode
- **Rural areas** → May need county resources

**Note:** For any city, finding ANY zoning-related URL helps. The system will try multiple strategies from there.

---

## Sample Research Session

Let me walk through 3 examples:

### Example 1: Chicago (Illinois)
**Google:** `Chicago zoning ordinance PDF`
**Result:** Find https://www.chicago.gov/content/dam/city/sites/planning/supp_info/zoning/zoning_ordinance.pdf
**Add:** `"Chicago": "https://www.chicago.gov/zoning-ordinance"`

### Example 2: Madison (Wisconsin)
**Google:** `Madison Wisconsin zoning ordinance PDF`
**Result:** Find https://www.cityofmadison.com/planning-development/zoning-code
**Add:** `"Madison": "https://www.cityofmadison.com/planning/zoning-code"`

### Example 3: Oak Park (Illinois)
**Google:** `Oak Park Illinois zoning ordinance`
**Result:** Find zoning page at https://www.oak-park.us/city-services/planning-development/zoning
**Add:** `"Oak Park": "https://www.oak-park.us/zoning"`

---

## Copy-Paste Template

Use this template to keep your research organized:

```
1. Chicago: https://www.chicago.gov/...
2. Evanston: https://www.cityofevanston.org/...
3. Oak Park: https://www.oak-park.us/...
4. Skokie: https://www.skokie.org/...
5. Des Plaines: https://www.desplaines.org/...
... continue through 30
```

Then copy all 30 into the script.

---

## How to Update the Script

Once you have your 30 URLs:

### Step 1: Open the Script
```bash
nano /home/claude/carwash-heat-map/scripts/01_fetch_ordinances.py
```

Or use your favorite editor.

### Step 2: Find the Base URLs Section
Search for: `def get_municipality_base_urls`

You'll see something like:
```python
def get_municipality_base_urls(self) -> Dict[str, str]:
    """Base URL database"""
    return {
        "Chicago": "https://www.chicago.gov",
        "Evanston": "https://www.cityofevanston.org",
        ...
    }
```

### Step 3: Replace with Your URLs
Delete the existing dictionary values and add your 30:

```python
def get_municipality_base_urls(self) -> Dict[str, str]:
    """Base URL database"""
    return {
        "Chicago": "https://www.chicago.gov/zoning-ordinance",
        "Evanston": "https://www.cityofevanston.org/planning/zoning",
        "Oak Park": "https://www.oak-park.us/zoning",
        # ... all 30 cities here
    }
```

### Step 4: Save and Close
- Save the file (Ctrl+S in nano, :wq in vim)
- Don't change anything else in the script

### Step 5: Verify
Quick check that file was saved:
```bash
grep "Chicago" /home/claude/carwash-heat-map/scripts/01_fetch_ordinances.py
```

Should show your Chicago URL.

---

## Expected Success After Research

With 30 well-researched URLs, expect:

- **50-75% Success Rate** = 15-25 ordinances found
- **Why not 100%?** Some URLs may be slightly wrong, outdated, or the city website changed structure
- **That's OK!** The system tries 4 fallback strategies. Many will still be found through other methods

---

## Timeline: How This Flows

```
Your Work (15 minutes):
  Google 30 cities
  Copy URLs
  Update script
  ✅ DONE

System Work (12+ hours - you don't do anything):
  Stage 1: Try all strategies on 30 cities → 15-25 ordinances found
  Stage 2: Parse ordinances → Extract rules
  Stage 3: Scrape approvals → Get sentiment
  Stage 4: Score & map → Heat map ready

Result:
  Interactive map by end of today
  15-25 cities scored
  Sourcing intelligence ready
```

---

## Quick Reference: Common URL Patterns

If you're stuck on a city, these patterns often work:

```
City Website Patterns:
  https://www.[city].gov/zoning
  https://www.[city].org/zoning
  https://[city].[state].gov/zoning
  https://city[city].gov/planning/zoning

Common Department Paths:
  /departments/planning/zoning-ordinance
  /planning/zoning-ordinance
  /planning/municipal-code
  /city-services/zoning

Fallback (Municode):
  https://library.municode.com/[state_abbr]/[city]/codes
```

---

## What to Do Now

1. **Open Google** (or your favorite search engine)
2. **For each of the 30 cities:**
   - Google: `[city] zoning ordinance`
   - Copy best URL found
   - Write it down or paste into a document
3. **Update the script** with your 30 URLs
4. **Tell me when done** and I'll walk you through running it

**Should take 15 minutes total.**

---

## I'll Handle Everything Else

Once you give me the green light with your 30 URLs updated, I'll:
- ✅ Verify the URLs work
- ✅ Run the enhanced fetcher
- ✅ Execute all 4 stages automatically
- ✅ Generate your heat map
- ✅ Get it ready for deployment

---

## Questions?

**Q: What if I can't find a URL for a city?**  
A: Skip it. The system will try to find it through other strategies anyway.

**Q: Does the URL have to be perfect?**  
A: No. Close is good enough. The system tries multiple patterns and has fallback strategies.

**Q: Can I use Municode URLs?**  
A: Yes. Those work great and are often more reliable.

**Q: How do I know if a URL is good?**  
A: If it contains "zoning", "ordinance", or "code" and goes to a city website, it's probably fine.

**Q: What if the city has multiple PDF links?**  
A: Pick the most recent one. Usually says "Current" or has a recent date.

---

## Let's Go!

**Start researching. Google 30 cities. Copy 30 URLs. Update the script. You'll be done in 15 minutes.**

Then tell me and we'll run the full pipeline.

---

**Version:** 1.0  
**Difficulty:** Easy (mostly copy/paste)  
**Time:** 15 minutes  
**Next Step:** Start Googling!
