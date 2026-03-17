#!/usr/bin/env python3
"""
Build Zoning Data v5 — Friction-Adjusted Institutional Scoring

Jane Street / Blackstone methodology:
- No municipality EVER scores 100. Even the best ones have friction.
- 5 factors, each 0-20, but calibrated so the BEST realistic score is ~85
- Forced distribution: ~15% green, ~25% light green, ~30% yellow, ~20% orange, ~10% red
- Every "permitted" municipality gets friction penalties for:
  * Process timeline (site plan review, design review boards)
  * Fee structure (impact fees, permit fees)
  * Competitive saturation (existing businesses reduce opportunity)
  * Political risk (even supportive councils can flip)
  * Site constraints (lot size, setbacks, buffering requirements)

The key insight: ZONING PERMISSIVENESS is only 20% of the score.
The other 80% is execution friction.
"""
import json, os, random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

def score_to_status(s):
    if s >= 80: return 'permitted'
    if s >= 65: return 'likely_permitted'
    if s >= 50: return 'conditional'
    if s >= 30: return 'restrictive'
    return 'prohibited'

# ============================================================
# FRICTION-ADJUSTED SCORING MODEL
#
# 5 Factors (each 0-20):
#   1. Zoning Permissiveness: Is the use allowed? How easily?
#   2. Process Friction: Timeline, fees, review boards, hearings
#   3. Site Availability: Parcel supply, lot requirements, setbacks
#   4. Competitive Landscape: Market saturation, existing operators
#   5. Political Climate: Council disposition, NIMBY risk, anti-auto sentiment
#
# Calibration targets:
#   - Best possible municipality: ~82-87 (never 100)
#   - Typical "permitted" suburb: 55-72
#   - Conditional use suburb: 40-60
#   - Special use / restrictive: 25-45
#   - Prohibited: 5-20
# ============================================================

# Population-based friction modifiers
# Larger cities = more process friction, more competition, more political complexity
def pop_friction(pop):
    """Returns (process_penalty, site_penalty, competition_penalty, political_penalty)"""
    if pop >= 500000:  return (6, 5, 7, 5)   # Major metro: tons of friction everywhere
    if pop >= 200000:  return (5, 4, 6, 4)
    if pop >= 100000:  return (4, 4, 5, 3)
    if pop >= 50000:   return (3, 3, 4, 3)
    if pop >= 25000:   return (2, 2, 3, 2)
    if pop >= 10000:   return (1, 1, 2, 1)
    if pop >= 5000:    return (0, 0, 1, 0)
    return (0, 0, 0, 0)  # Small towns: minimal friction

# State-level regulatory friction
# IL = most bureaucratic, IN = most business-friendly, WI = moderate
STATE_FRICTION = {
    # Very high friction
    'CA': {'process': 5, 'political': 4}, 'NY': {'process': 4, 'political': 3},
    'MA': {'process': 4, 'political': 3}, 'NJ': {'process': 4, 'political': 3},
    'CT': {'process': 4, 'political': 3}, 'DC': {'process': 4, 'political': 3},
    'HI': {'process': 3, 'political': 3},
    # High friction
    'IL': {'process': 3, 'political': 2}, 'PA': {'process': 3, 'political': 2},
    'MD': {'process': 3, 'political': 2}, 'VA': {'process': 3, 'political': 2},
    'OR': {'process': 3, 'political': 3}, 'WA': {'process': 3, 'political': 3},
    'NH': {'process': 3, 'political': 2}, 'VT': {'process': 3, 'political': 2},
    'RI': {'process': 3, 'political': 2}, 'DE': {'process': 3, 'political': 2},
    # Moderate friction
    'WI': {'process': 1, 'political': 1}, 'MI': {'process': 2, 'political': 1},
    'MN': {'process': 2, 'political': 1}, 'OH': {'process': 2, 'political': 1},
    'CO': {'process': 2, 'political': 2}, 'ME': {'process': 2, 'political': 1},
    'NC': {'process': 1, 'political': 1}, 'GA': {'process': 1, 'political': 1},
    'FL': {'process': 1, 'political': 1},
    # Low friction
    'TX': {'process': 0, 'political': 0}, 'IN': {'process': 0, 'political': 0},
    'AL': {'process': 0, 'political': 0}, 'MS': {'process': 0, 'political': 0},
    'AR': {'process': 0, 'political': 0}, 'LA': {'process': 0, 'political': 0},
    'OK': {'process': 0, 'political': 0}, 'KS': {'process': 0, 'political': 0},
    'SC': {'process': 0, 'political': 0}, 'TN': {'process': 1, 'political': 0},
    'KY': {'process': 1, 'political': 0}, 'WV': {'process': 1, 'political': 0},
    'MO': {'process': 1, 'political': 0}, 'IA': {'process': 1, 'political': 0},
    'NE': {'process': 1, 'political': 0}, 'SD': {'process': 1, 'political': 0},
    'ND': {'process': 1, 'political': 0}, 'MT': {'process': 1, 'political': 0},
    'WY': {'process': 0, 'political': 0}, 'ID': {'process': 0, 'political': 0},
    'UT': {'process': 0, 'political': 0}, 'NV': {'process': 1, 'political': 0},
    'AZ': {'process': 1, 'political': 0}, 'NM': {'process': 1, 'political': 0},
    'AK': {'process': 0, 'political': 0},
}

# Affluence penalty — wealthy suburbs fight everything
def affluence_penalty(city):
    """Extra friction for known affluent communities"""
    affluent = {
        'Kenilworth': 6, 'Winnetka': 5, 'Glencoe': 5, 'Lake Forest': 5,
        'Hinsdale': 5, 'Wilmette': 4, 'Barrington': 4, 'Deerfield': 3,
        'Highland Park': 4, 'Northbrook': 3, 'Glenview': 2,
        'Park Ridge': 2, 'Mequon': 3, 'Shorewood': 4,
        'Clarendon Hills': 2, 'Cedarburg': 1, 'Brookfield': 1,
        'Naperville': 3,  # Ground truth — very resistant
    }
    return affluent.get(city, 0)


# ============================================================
# ENRICHED DATA with FRICTION FACTORS
#
# Format: (city, state, pop,
#   cw_zoning, dt_zoning, cr_zoning, as_zoning,  (0-20 raw zoning permissiveness)
#   cw_pathway, dt_pathway, cr_pathway, as_pathway,
#   dt_stacking,
#   cw_zones, dt_zones, cr_zones, as_zones,
#   su_cw, su_dt, su_cr, su_as,
#   process_adj, site_adj, competition_adj, political_adj,  (per-city adjustments ±)
#   zoning_map_url, notes)
#
# Zoning scores (0-20):
#   20 = explicitly listed as permitted by right, minimal conditions
#   16 = permitted but with site plan review / design standards
#   12 = conditional use
#   8  = special use permit required
#   4  = heavily restricted, PUD only, or effectively prohibited
#   0  = prohibited
# ============================================================

ENRICHED = [
    # === HIGHLY PERMISSIVE (but still with friction) ===
    # Even the best get dinged: process time, competition, political risk
    # city, state, pop,
    # cw_z, dt_z, cr_z, as_z,
    # cw_path, dt_path, cr_path, as_path,
    # dt_stack,
    # cw_zones, dt_zones, cr_zones, as_zones,
    # su_cw, su_dt, su_cr, su_as,
    # process_adj, site_adj, comp_adj, pol_adj,
    # map_url, notes

    ("Aurora", "IL", 197000,
     18, 18, 14, 16,
     "Permitted", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3, M-1", "B-2, B-3, B-4", "M-1, M-2", "B-3, B-4, M-1",
     False, False, True, False,
     0, 1, -1, 1,
     "https://gis.aurora-il.org", "Pro-development, but large city = process friction."),

    ("Joliet", "IL", 148000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4, B-5", "B-4, M-1, M-2", "B-3, B-4, B-5",
     False, False, False, False,
     1, 1, 0, 1,
     "https://www.joliet.gov/departments/community-development/gis-maps", "Business-friendly but growing = competition."),

    ("Des Plaines", "IL", 58000,
     18, 16, 12, 16,
     "Permitted", "Permitted", "Conditional Use", "Permitted", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4",
     False, False, True, False,
     -1, 0, -1, 0,
     "https://www.desplaines.org/maps", "8-car stacking per Sec. 12-9-4."),

    ("Bolingbrook", "IL", 73000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     1, 1, 0, 1,
     "", "Growth-oriented but IL process friction."),

    ("Plainfield", "IL", 41000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     2, 2, 1, 2,
     "", "Rapidly growing. Less competition. Pro-development."),

    ("Romeoville", "IL", 39000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     2, 1, 1, 2,
     "", ""),

    ("Addison", "IL", 36000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, M-1", "B-3", "M-1, M-2", "B-3, M-1",
     False, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Carol Stream", "IL", 40000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Glendale Heights", "IL", 34000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Bloomingdale", "IL", 22000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 1, 1, 1,
     "", ""),

    ("Bensenville", "IL", 21000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Wood Dale", "IL", 14000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Itasca", "IL", 8500,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2",
     False, False, False, False,
     2, 0, 3, 2,
     "", "Small town — less competition but limited sites."),

    ("Elk Grove Village", "IL", 32000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 1, 0, 1,
     "https://www.elkgrove.org/gis", ""),

    ("Waukegan", "IL", 87000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     1, 1, 0, 0,
     "", ""),

    ("Antioch", "IL", 14000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     2, 1, 3, 2,
     "", ""),

    ("Round Lake", "IL", 18500,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     2, 1, 3, 2,
     "", ""),

    ("Mundelein", "IL", 31000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Grayslake", "IL", 21000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Tinley Park", "IL", 57000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     0, 0, -1, 0,
     "", ""),

    ("Homer Glen", "IL", 21500,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 1, 2, 1,
     "", ""),

    ("Blue Island", "IL", 23000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     1, 1, 1, 0,
     "", ""),

    ("Alsip", "IL", 19000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     1, 1, 1, 1,
     "", ""),

    ("Oak Forest", "IL", 28000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 0, 1, 1,
     "", ""),

    ("Berwyn", "IL", 55000,
     18, 18, 12, 14,
     "Permitted", "Permitted", "Conditional Use", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, True, False,
     0, -1, -1, 0,
     "", "Dense inner suburb. Limited parcels."),

    ("Cicero", "IL", 84000,
     18, 18, 14, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     False, False, False, False,
     -1, -1, -2, -1,
     "", "Dense. Political complexity."),

    ("Melrose Park", "IL", 23000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2",
     False, False, False, False,
     1, 0, 1, 1,
     "", ""),

    ("Bellwood", "IL", 19000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2",
     False, False, False, False,
     1, 0, 2, 1,
     "", ""),

    ("Warrenville", "IL", 13000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2",
     False, False, False, False,
     2, 0, 3, 2,
     "", ""),

    ("Winfield", "IL", 9200,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2",
     False, False, False, False,
     2, 0, 3, 2,
     "", ""),

    ("Villa Park", "IL", 22000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Lockport", "IL", 25000,
     18, 18, 16, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     1, 1, 1, 1,
     "", ""),

    # === WISCONSIN HIGH SCORERS ===
    ("Green Bay", "WI", 104000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-1, C-2, C-3", "C-1, C-2, C-3", "C-3, IL", "C-2, C-3, IL",
     False, False, False, False,
     1, 1, 0, 1,
     "https://greenbaywi.gov/gis", ""),

    ("Wauwatosa", "WI", 48000,
     18, 18, 12, 12,
     "Permitted", "Permitted", "Conditional Use", "Conditional Use", 6,
     "C-2, C-3", "C-2, C-3", "C-3, IL", "C-3",
     False, False, True, True,
     0, 0, -1, 0,
     "https://www.wauwatosa.net/government/gis-maps", "Collision/auto sales more restricted."),

    ("Oak Creek", "WI", 36500,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     2, 1, 1, 2,
     "", ""),

    ("Sun Prairie", "WI", 32000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "CC, HC", "CC, HC", "HC, LI", "CC, HC",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Menomonee Falls", "WI", 35000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     False, False, False, False,
     2, 1, 1, 2,
     "", ""),

    ("Germantown", "WI", 20000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("West Bend", "WI", 32000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-3", "B-3", "B-3, M-1", "B-3",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("De Pere", "WI", 24000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, IL", "C-1, C-2",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Ashwaubenon", "WI", 17000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, IL", "C-1, C-2",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Grafton", "WI", 11600,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2",
     False, False, False, False,
     2, 1, 3, 2,
     "", ""),

    ("Port Washington", "WI", 11600,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2",
     False, False, False, False,
     2, 1, 3, 2,
     "", ""),

    ("Fitchburg", "WI", 28000,
     18, 18, 16, 18,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "CG, CH", "CG, CH", "CH, LI", "CG, CH",
     False, False, False, False,
     2, 1, 2, 2,
     "", ""),

    ("Middleton", "WI", 19000,
     18, 18, 14, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2",
     False, False, False, False,
     1, 0, 1, 1,
     "", "Near Madison — some design review friction."),

    ("Glendale", "WI", 13000,
     18, 18, 14, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-3", "B-3", "B-3, M-1", "B-3",
     False, False, False, False,
     1, 0, 1, 1,
     "", ""),

    # === PERMITTED WITH FRICTION (scores will land ~60-75) ===
    ("Madison", "WI", 269000,
     16, 18, 10, 10,
     "Permitted", "Permitted", "Conditional Use", "Conditional Use", 8,
     "CC, CC-T", "CC, NMX, TSS", "IL, IG", "CC-T, SE",
     False, False, True, True,
     -2, -2, -2, -2,
     "https://cityofmadison.maps.arcgis.com", "Large city. Design review. Auto uses restricted in core."),

    ("Waukesha", "WI", 72000,
     16, 18, 14, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4, B-5", "B-4, M-1", "B-3, B-4, B-5",
     False, False, False, False,
     0, 0, -1, 0,
     "https://www.ci.waukesha.wi.us/gis", ""),

    ("Verona", "WI", 13800,
     16, 18, 14, 16,
     "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, M-1", "C-1, C-2",
     False, False, False, False,
     1, 0, 2, 1,
     "", ""),

    ("Chicago", "IL", 2700000,
     12, 12, 8, 8,
     "Conditional Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B3-2, C1-2, C1-3", "B3-2, C1-2, C1-3", "C2-3, M1-2", "C2-2, C2-3, M1-2",
     False, False, True, True,
     -4, -3, -4, -3,
     "https://gisapps.chicago.gov/ZoningMapWeb/", "Aldermanic approval is key. Massive process friction."),

    # === CONDITIONAL USE (scores ~45-65) ===
    ("Milwaukee", "WI", 577000,
     12, 18, 10, 10,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "LB2, CS", "LB2, CS, IL", "CS, IL, IG", "CS, IL",
     True, False, True, True,
     -2, -2, -3, -2,
     "https://city.milwaukee.gov/maps", "Large metro. Auto uses face extra friction."),

    ("Wheaton", "IL", 53000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4",
     True, False, True, True,
     0, 0, -1, 0,
     "", ""),

    ("Skokie", "IL", 65000,
     12, 16, 8, 10,
     "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B2, B3", "B2, B3", "B3, M-1", "B2, B3",
     True, False, True, True,
     -1, -1, -2, -1,
     "https://www.skokie.org/maps", "Collision repair special use in commercial."),

    ("Arlington Heights", "IL", 76000,
     12, 12, 8, 8,
     "Conditional Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     True, True, True, True,
     -1, -1, -2, -1,
     "https://www.vah.com/maps", "All auto uses face scrutiny."),

    ("Downers Grove", "IL", 49000,
     12, 12, 10, 10,
     "Conditional Use", "Conditional Use", "Conditional Use", "Conditional Use", 8,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     True, True, True, True,
     0, 0, -1, 0,
     "https://www.downers.us/maps", ""),

    ("New Berlin", "WI", 39000,
     12, 16, 14, 14,
     "Conditional Use", "Permitted", "Permitted", "Permitted", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3",
     True, False, False, False,
     1, 0, 0, 1,
     "", ""),

    ("Palatine", "IL", 68000,
     12, 16, 8, 10,
     "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     True, False, True, True,
     -1, 0, -1, 0,
     "", ""),

    ("Rolling Meadows", "IL", 24000,
     12, 16, 12, 14,
     "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "C-3", "C-3, C-4", "C-4, M-1", "C-3, C-4",
     True, False, True, False,
     1, 0, 0, 1,
     "", ""),

    ("Mount Prospect", "IL", 54000,
     12, 16, 8, 10,
     "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     True, False, True, True,
     0, 0, -1, 0,
     "", ""),

    ("Hoffman Estates", "IL", 52000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3",
     True, False, True, True,
     0, 0, -1, 0,
     "", ""),

    ("Northbrook", "IL", 33000,
     12, 16, 8, 8,
     "Conditional Use", "Permitted", "Special Use", "Special Use", 8,
     "C-3", "C-2, C-3", "C-4, M-1", "C-3, C-4",
     True, False, True, True,
     -1, -1, -1, -1,
     "https://www.northbrook.il.us/maps", "Affluent. Auto-intensive uses face resistance."),

    ("Glenview", "IL", 47000,
     12, 16, 8, 8,
     "Conditional Use", "Permitted", "Special Use", "Special Use", 8,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3",
     True, False, True, True,
     -1, -1, -1, -1,
     "", ""),

    ("Elmhurst", "IL", 46000,
     12, 16, 8, 10,
     "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4",
     True, False, True, True,
     0, 0, -1, 0,
     "", ""),

    ("Lombard", "IL", 44000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3",
     True, False, True, True,
     0, 0, 0, 0,
     "", ""),

    ("Orland Park", "IL", 58000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4",
     True, False, True, True,
     0, 0, -1, 0,
     "https://www.orlandpark.org/maps", ""),

    ("Brookfield", "WI", 38000,
     12, 8, 10, 12,
     "Conditional Use", "Special Use", "Conditional Use", "Conditional Use", 10,
     "B-3", "B-3", "B-3, M-1", "B-3",
     True, True, True, True,
     0, 0, -1, 0,
     "https://www.ci.brookfield.wi.us/maps", "Stacking issues for DT. 10-car requirement."),

    # === SPECIAL USE / RESTRICTIVE (scores ~25-50) ===
    ("Evanston", "IL", 74000,
     8, 16, 6, 6,
     "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C1a, C2", "C1, C1a, C2", "C2, I1", "C2",
     True, False, True, True,
     -2, -2, -2, -2,
     "https://www.cityofevanston.org/maps", "Dense urban. Anti-auto sentiment. High process friction."),

    ("Oak Park", "IL", 52000,
     8, 16, 6, 6,
     "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "B (Business)", "B (Business)", "B, I (Industrial)", "B (Business)",
     True, False, True, True,
     -2, -2, -2, -2,
     "", "Progressive suburb. Anti-auto sprawl sentiment."),

    ("Mequon", "WI", 24000,
     8, 16, 10, 10,
     "Special Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-2", "B-2", "B-2, M-1", "B-2",
     True, False, True, True,
     0, -1, 0, -1,
     "", "Affluent suburb."),

    ("Shorewood", "WI", 13000,
     8, 12, 4, 4,
     "Special Use", "Conditional Use", "Prohibited", "Prohibited", 6,
     "B-4", "B-4", "None", "None",
     True, True, False, False,
     -2, -3, -2, -2,
     "", "Dense, walkable. Anti-auto. No auto-intensive uses allowed."),

    ("Park Ridge", "IL", 37000,
     8, 16, 6, 8,
     "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C-3", "C-2, C-3", "C-4, M-1", "C-3",
     True, False, True, True,
     -1, -1, -1, -1,
     "", ""),

    ("Wilmette", "IL", 28000,
     8, 12, 4, 6,
     "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "GC-1", "GC-1, NR", "GC-1", "GC-1",
     True, True, True, True,
     -2, -2, -1, -2,
     "", "North Shore. Very restrictive for auto uses."),

    ("Highland Park", "IL", 30000,
     8, 12, 4, 6,
     "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-5", "B-3, B-5", "B-5, M-1", "B-5",
     True, True, True, True,
     -2, -2, -1, -2,
     "", ""),

    ("Deerfield", "IL", 19000,
     8, 16, 6, 8,
     "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-3",
     True, False, True, True,
     -1, -1, -1, -1,
     "", ""),

    ("Lake Forest", "IL", 19000,
     8, 12, 4, 4,
     "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "GC-1", "GC-1", "GC-1, LI", "GC-1",
     True, True, True, True,
     -3, -2, -1, -2,
     "", "Very affluent. Strict design standards. Historic preservation."),

    ("Libertyville", "IL", 20000,
     12, 16, 10, 10,
     "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3",
     True, False, True, True,
     0, 0, 0, 0,
     "", ""),

    ("Palos Hills", "IL", 18000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3",
     True, False, True, False,
     0, 0, 0, 0,
     "", ""),

    ("Darien", "IL", 22000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     True, False, True, False,
     0, 0, 0, 0,
     "", ""),

    ("Hinsdale", "IL", 17000,
     8, 12, 0, 6,
     "Special Use", "Conditional Use", "Prohibited", "Special Use", 10,
     "B-1, B-2", "B-1, B-2", "None", "B-2",
     True, True, False, True,
     -3, -2, -1, -3,
     "", "Very affluent. No collision repair. 10-car stacking. Design review board."),

    ("Westmont", "IL", 24000,
     12, 16, 10, 12,
     "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3",
     True, False, True, False,
     0, 0, 0, 0,
     "", ""),

    ("Cedarburg", "WI", 12000,
     8, 12, 10, 10,
     "Special Use", "Conditional Use", "Conditional Use", "Conditional Use", 6,
     "B-2", "B-2", "B-2, M-1", "B-2",
     True, True, True, True,
     -1, -1, 0, -1,
     "", "Historic downtown. Aesthetic concerns."),

    ("Barrington", "IL", 10000,
     8, 10, 6, 8,
     "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-3", "B-3", "B-3, M-1", "B-3",
     True, True, True, True,
     -1, -1, 0, -2,
     "", "Affluent. Community character concerns."),

    ("Glencoe", "IL", 9000,
     8, 8, 0, 0,
     "Special Use", "Special Use", "Prohibited", "Prohibited", 8,
     "C-Comm", "C-Comm", "None", "None",
     True, True, False, False,
     -3, -3, -1, -3,
     "", "Very affluent North Shore. Auto uses extremely restricted."),

    ("Winnetka", "IL", 12000,
     8, 8, 0, 0,
     "Special Use", "Special Use", "Prohibited", "Prohibited", 8,
     "C-Comm", "C-Comm", "None", "None",
     True, True, False, False,
     -3, -3, -1, -3,
     "", "Extremely affluent. Auto uses extremely restricted."),

    ("Clarendon Hills", "IL", 9000,
     8, 12, 6, 8,
     "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-1", "B-1", "B-1, M-1", "B-1",
     True, True, True, True,
     -1, -1, 0, -1,
     "", ""),

    # === NAPERVILLE (GROUND TRUTH) ===
    ("Naperville", "IL", 149000,
     10, 6, 8, 10,
     "Conditional Use", "Special Use", "Special Use", "Conditional Use", 10,
     "B-3 only", "B-3 only (B-2 = Special Use)", "B-3, M-1", "B-3, B-4",
     True, True, True, True,
     -3, -2, -3, -4,
     "https://www.naperville.il.us/maps",
     "Ground truth: Dutch Bros DENIED on Napier Blvd. 7 Brew at 1203 Iroquois only w/ extensive conditions."),

    ("Schaumburg", "IL", 74000,
     12, 8, 8, 10,
     "Conditional Use", "Special Use", "Special Use", "Conditional Use", 10,
     "B-2, B-3", "B-3 only", "B-3, M-1", "B-2, B-3",
     True, True, True, True,
     -2, -1, -2, -2,
     "https://www.schaumburg.com/maps", "10-car stacking. Auto uses face extra scrutiny."),

    # === PROHIBITED ===
    ("Kenilworth", "IL", 2500,
     0, 0, 0, 0,
     "Prohibited", "Prohibited", "Prohibited", "Prohibited", 0,
     "None", "None", "None", "None",
     False, False, False, False,
     -4, -4, 0, -4,
     "", "Exclusively residential village. No commercial zones."),
]


def compute_score(zoning_raw, city, state, pop, process_adj, site_adj, comp_adj, pol_adj):
    """
    Compute friction-adjusted score for a single use type.

    zoning_raw: 0-20 raw zoning permissiveness
    Returns: 0-100 composite score
    """
    proc_pen, site_pen, comp_pen, polit_pen = pop_friction(pop)
    sf = STATE_FRICTION.get(state, {'process': 0, 'political': 0})
    aff = affluence_penalty(city)

    # Factor 1: Zoning Permissiveness (raw, 0-20)
    f_zoning = max(0, min(20, zoning_raw))

    # Factor 2: Process Friction (start at 16, subtract penalties)
    f_process = max(0, min(20, 16 - proc_pen - sf['process'] + process_adj))

    # Factor 3: Site Availability (start at 16, subtract penalties)
    f_site = max(0, min(20, 16 - site_pen + site_adj))

    # Factor 4: Competitive Landscape (start at 16, subtract penalties)
    f_competition = max(0, min(20, 16 - comp_pen + comp_adj))

    # Factor 5: Political Climate (start at 16, subtract penalties)
    f_political = max(0, min(20, 16 - polit_pen - sf['political'] - aff + pol_adj))

    factors = {
        'zoning': f_zoning,
        'process': f_process,
        'site': f_site,
        'competition': f_competition,
        'political': f_political,
    }

    composite = sum(factors.values())
    return composite, factors


def build():
    data = {}
    for row in ENRICHED:
        (city, state, pop,
         cw_z, dt_z, cr_z, as_z,
         cw_path, dt_path, cr_path, as_path,
         dt_stack,
         cw_zones, dt_zones, cr_zones, as_zones,
         su_cw, su_dt, su_cr, su_as,
         process_adj, site_adj, comp_adj, pol_adj,
         zoning_url, notes) = row

        key = f"{city}, {state}"

        # Compute per-use scores
        cw_score, cw_factors = compute_score(cw_z, city, state, pop, process_adj, site_adj, comp_adj, pol_adj)
        dt_score, dt_factors = compute_score(dt_z, city, state, pop, process_adj, site_adj, comp_adj, pol_adj)
        cr_score, cr_factors = compute_score(cr_z, city, state, pop, process_adj, site_adj, comp_adj, pol_adj)
        as_score, as_factors = compute_score(as_z, city, state, pop, process_adj, site_adj, comp_adj, pol_adj)

        # Composite = average of all 4 use types (weighted toward CW/DT since that's the primary use case)
        composite = round((cw_score * 0.3 + dt_score * 0.3 + cr_score * 0.2 + as_score * 0.2))

        # Use the CW factors as the "general" display factors (close enough)
        display_factors = {
            'zoning': cw_factors['zoning'],
            'process': cw_factors['process'],
            'site': cw_factors['site'],
            'competition': cw_factors['competition'],
            'political': cw_factors['political'],
        }

        # Naperville ground truth override for composite
        if city == 'Naperville':
            composite = 35  # Ground truth: very difficult but not impossible

        data[key] = {
            'name': city,
            'state': state,
            'composite': composite,
            'factors': display_factors,
            'carwash': {
                'status': score_to_status(cw_score),
                'score': cw_score,
                'pathway': cw_path,
                'zones': cw_zones,
                'special_use': su_cw,
            },
            'drivethru': {
                'status': score_to_status(dt_score),
                'score': dt_score,
                'pathway': dt_path,
                'zones': dt_zones,
                'special_use': su_dt,
                'stacking_cars': dt_stack if dt_stack > 0 else None,
            },
            'collision': {
                'status': score_to_status(cr_score),
                'score': cr_score,
                'pathway': cr_path,
                'zones': cr_zones,
                'special_use': su_cr,
            },
            'autosales': {
                'status': score_to_status(as_score),
                'score': as_score,
                'pathway': as_path,
                'zones': as_zones,
                'special_use': su_as,
            },
            'requirements': {
                'stacking_cars': dt_stack if dt_stack > 0 else None,
                'lot_size_sqft': None,
                'front_setback_ft': None,
            },
            'stacking_issue': dt_stack >= 10 or (su_dt and dt_score < 50),
            'moratorium': False,
            'zoning_map_url': zoning_url,
            'confidence': 'High' if city == 'Naperville' else 'AI Estimate',
            'verified': city == 'Naperville',
            'override_reason': notes if city == 'Naperville' else '',
            'notes': notes if city != 'Naperville' else 'Ground truth: Dutch Bros DENIED on Napier Blvd.',
            'population': pop,
        }

    return data


def main():
    data = build()

    out_path = os.path.join(DATA, 'zoning_data.json')
    with open(out_path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

    # Score distribution analysis
    all_cw = sorted([v['carwash']['score'] for v in data.values()])
    all_dt = sorted([v['drivethru']['score'] for v in data.values()])

    print(f'Output: {out_path}')
    print(f'  Total: {len(data)}')
    print()
    print(f'  === SCORE DISTRIBUTION (Car Wash) ===')
    print(f'  Min: {min(all_cw)}, Max: {max(all_cw)}, Avg: {sum(all_cw)/len(all_cw):.0f}')
    brackets = [(80, 100, 'Green'), (65, 79, 'Lt Green'), (50, 64, 'Yellow'), (30, 49, 'Orange'), (0, 29, 'Red')]
    for lo, hi, label in brackets:
        count = sum(1 for s in all_cw if lo <= s <= hi)
        pct = count / len(all_cw) * 100
        print(f'  {label:10s} ({lo:2d}-{hi:3d}): {count:3d} ({pct:4.1f}%)')

    print()
    print(f'  === SCORE DISTRIBUTION (Drive-Thru) ===')
    print(f'  Min: {min(all_dt)}, Max: {max(all_dt)}, Avg: {sum(all_dt)/len(all_dt):.0f}')
    for lo, hi, label in brackets:
        count = sum(1 for s in all_dt if lo <= s <= hi)
        pct = count / len(all_dt) * 100
        print(f'  {label:10s} ({lo:2d}-{hi:3d}): {count:3d} ({pct:4.1f}%)')

    print()
    nap = data.get('Naperville, IL', {})
    sep = ', '
    print(f'  Naperville: CW={nap["carwash"]["score"]}{sep}DT={nap["drivethru"]["score"]}{sep}CR={nap["collision"]["score"]}{sep}AS={nap["autosales"]["score"]}')
    print(f'  Naperville factors: {nap["factors"]}')


if __name__ == '__main__':
    main()
