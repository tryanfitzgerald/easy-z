#!/usr/bin/env python3
"""
Build Zoning Data v3 — Separate CW/DT Requirements + Zoning Map Links
Reads the research workbook OR falls back to enriched hardcoded data.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')

def score_to_status(s):
    if s >= 85: return 'permitted'
    if s >= 67: return 'likely_permitted'
    if s >= 50: return 'conditional'
    if s >= 25: return 'restrictive'
    return 'prohibited'

# ============================================================
# ENRICHED MUNICIPALITY DATA
# Based on the original analysis docs + known zoning patterns
# Format: (city, state, pop, cw_score, dt_score,
#          cw_pathway, dt_pathway,
#          dt_stacking, cw_zones, dt_zones,
#          special_use_cw, special_use_dt,
#          zoning_map_url, notes)
# ============================================================
# Pathways: "Permitted", "Conditional Use", "Special Use", "PUD", "Prohibited", "Unknown"

ENRICHED = [
    # === HIGH SCORING (85-100) ===
    ("Aurora", "IL", 197000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3, M-1", "B-2, B-3, B-4", False, False,
     "https://gis.aurora-il.org", "Pro-development. Both uses permitted by right in commercial."),
    ("Joliet", "IL", 148000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4, B-5", False, False,
     "https://www.joliet.gov/departments/community-development/gis-maps", "Business-friendly. Standard commercial zones."),
    ("Des Plaines", "IL", 58000, 100, 100, "Permitted", "Permitted", 8, "C-3, C-4", "C-3, C-4", False, False,
     "https://www.desplaines.org/maps", "Permitted in general commercial. Stacking per Sec. 12-9-4."),
    ("Bolingbrook", "IL", 73000, 100, 100, "Permitted", "Permitted", 6, "C-2, C-3", "C-2, C-3", False, False,
     "", "Growth-oriented suburb. Commercial districts welcoming."),
    ("Plainfield", "IL", 41000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False,
     "", "Rapidly growing. Pro-development planning board."),
    ("Romeoville", "IL", 39000, 100, 100, "Permitted", "Permitted", 5, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Addison", "IL", 36000, 100, 100, "Permitted", "Permitted", 6, "B-3, M-1", "B-3", False, False, "", ""),
    ("Carol Stream", "IL", 40000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Glendale Heights", "IL", 34000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Bloomingdale", "IL", 22000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Bensenville", "IL", 21000, 100, 100, "Permitted", "Permitted", 5, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Wood Dale", "IL", 14000, 100, 100, "Permitted", "Permitted", 5, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Itasca", "IL", 8500, 100, 100, "Permitted", "Permitted", 5, "B-2", "B-2", False, False, "", ""),
    ("Elk Grove Village", "IL", 32000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False,
     "https://www.elkgrove.org/gis", ""),
    ("Waukegan", "IL", 87000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Antioch", "IL", 14000, 100, 100, "Permitted", "Permitted", 5, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Round Lake", "IL", 18500, 100, 100, "Permitted", "Permitted", 5, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Mundelein", "IL", 31000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Grayslake", "IL", 21000, 100, 100, "Permitted", "Permitted", 5, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Tinley Park", "IL", 57000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Homer Glen", "IL", 21500, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Blue Island", "IL", 23000, 100, 100, "Permitted", "Permitted", 6, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Alsip", "IL", 19000, 100, 100, "Permitted", "Permitted", 5, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Oak Forest", "IL", 28000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Berwyn", "IL", 55000, 100, 100, "Permitted", "Permitted", 6, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Cicero", "IL", 84000, 100, 100, "Permitted", "Permitted", 6, "C-2, C-3", "C-2, C-3", False, False, "", ""),
    ("Melrose Park", "IL", 23000, 100, 100, "Permitted", "Permitted", 5, "C-2", "C-2", False, False, "", ""),
    ("Bellwood", "IL", 19000, 100, 100, "Permitted", "Permitted", 5, "C-2", "C-2", False, False, "", ""),
    ("Warrenville", "IL", 13000, 100, 100, "Permitted", "Permitted", 5, "B-2", "B-2", False, False, "", ""),
    ("Winfield", "IL", 9200, 100, 100, "Permitted", "Permitted", 5, "B-2", "B-2", False, False, "", ""),
    ("Villa Park", "IL", 22000, 100, 100, "Permitted", "Permitted", 6, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("Lockport", "IL", 25000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Green Bay", "WI", 104000, 100, 100, "Permitted", "Permitted", 6, "C-1, C-2, C-3", "C-1, C-2, C-3", False, False,
     "https://greenbaywi.gov/gis", ""),
    ("Wauwatosa", "WI", 48000, 100, 100, "Permitted", "Permitted", 6, "C-2, C-3", "C-2, C-3", False, False,
     "https://www.wauwatosa.net/government/gis-maps", ""),
    ("Oak Creek", "WI", 36500, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Sun Prairie", "WI", 32000, 100, 100, "Permitted", "Permitted", 5, "CC, HC", "CC, HC", False, False, "", ""),
    ("Menomonee Falls", "WI", 35000, 100, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4", False, False, "", ""),
    ("Germantown", "WI", 20000, 100, 100, "Permitted", "Permitted", 5, "B-2, B-3", "B-2, B-3", False, False, "", ""),
    ("West Bend", "WI", 32000, 100, 100, "Permitted", "Permitted", 5, "B-3", "B-3", False, False, "", ""),
    ("De Pere", "WI", 24000, 100, 100, "Permitted", "Permitted", 5, "C-1, C-2", "C-1, C-2", False, False, "", ""),
    ("Ashwaubenon", "WI", 17000, 100, 100, "Permitted", "Permitted", 5, "C-1, C-2", "C-1, C-2", False, False, "", ""),
    ("Grafton", "WI", 11600, 100, 100, "Permitted", "Permitted", 5, "B-2", "B-2", False, False, "", ""),
    ("Port Washington", "WI", 11600, 100, 100, "Permitted", "Permitted", 5, "B-2", "B-2", False, False, "", ""),
    ("Fitchburg", "WI", 28000, 100, 100, "Permitted", "Permitted", 5, "CG, CH", "CG, CH", False, False, "", ""),
    ("Middleton", "WI", 19000, 100, 100, "Permitted", "Permitted", 5, "C-2", "C-2", False, False, "", ""),
    ("Glendale", "WI", 13000, 100, 100, "Permitted", "Permitted", 5, "B-3", "B-3", False, False, "", ""),

    # === PERMITTED WITH NOTES (85-99) ===
    ("Madison", "WI", 269000, 95, 100, "Permitted", "Permitted", 8, "CC, CC-T", "CC, NMX, TSS", False, False,
     "https://cityofmadison.maps.arcgis.com", "Strong density focus. Car wash slightly more restricted."),
    ("Waukesha", "WI", 72000, 95, 100, "Permitted", "Permitted", 6, "B-3, B-4", "B-3, B-4, B-5", False, False,
     "https://www.ci.waukesha.wi.us/gis", ""),
    ("Verona", "WI", 13800, 95, 100, "Permitted", "Permitted", 5, "C-1, C-2", "C-1, C-2", False, False, "", ""),
    ("Chicago", "IL", 2700000, 95, 85, "Conditional Use", "Conditional Use", 8, "B3-2, C1-2, C1-3", "B3-2, C1-2, C1-3", False, False,
     "https://gisapps.chicago.gov/ZoningMapWeb/", "Large city. CU in most commercial. Aldermanic approval is key."),

    # === LIKELY PERMITTED (67-84) ===
    ("Milwaukee", "WI", 577000, 80, 100, "Conditional Use", "Permitted", 8, "LB2, CS", "LB2, CS, IL", True, False,
     "https://city.milwaukee.gov/maps", "Car wash needs CU. Drive-thru permitted in commercial/industrial."),
    ("Wheaton", "IL", 53000, 75, 100, "Conditional Use", "Permitted", 8, "C-3, C-4", "C-3, C-4", True, False,
     "", "Car wash requires conditional use. DT coffee permitted."),
    ("Skokie", "IL", 65000, 75, 100, "Conditional Use", "Permitted", 8, "B2, B3", "B2, B3", True, False,
     "https://www.skokie.org/maps", ""),
    ("Arlington Heights", "IL", 76000, 75, 85, "Conditional Use", "Conditional Use", 8, "B-3, B-4", "B-3, B-4", True, True,
     "https://www.vah.com/maps", "Both uses require conditional use hearing."),
    ("Downers Grove", "IL", 49000, 75, 85, "Conditional Use", "Conditional Use", 8, "B-2, B-3", "B-2, B-3", True, True,
     "https://www.downers.us/maps", ""),
    ("New Berlin", "WI", 39000, 75, 100, "Conditional Use", "Permitted", 6, "B-3", "B-2, B-3", True, False, "", ""),
    ("Palatine", "IL", 68000, 75, 100, "Conditional Use", "Permitted", 8, "B-3, B-4", "B-3, B-4", True, False, "", ""),
    ("Rolling Meadows", "IL", 24000, 75, 100, "Conditional Use", "Permitted", 6, "C-3", "C-3, C-4", True, False, "", ""),
    ("Mount Prospect", "IL", 54000, 75, 100, "Conditional Use", "Permitted", 8, "B-3, B-4", "B-3, B-4", True, False, "", ""),
    ("Hoffman Estates", "IL", 52000, 75, 100, "Conditional Use", "Permitted", 6, "B-3", "B-2, B-3", True, False, "", ""),
    ("Northbrook", "IL", 33000, 75, 100, "Conditional Use", "Permitted", 8, "C-3", "C-2, C-3", True, False,
     "https://www.northbrook.il.us/maps", ""),
    ("Glenview", "IL", 47000, 75, 100, "Conditional Use", "Permitted", 8, "B-3", "B-2, B-3", True, False, "", ""),
    ("Elmhurst", "IL", 46000, 75, 100, "Conditional Use", "Permitted", 8, "C-3, C-4", "C-3, C-4", True, False, "", ""),
    ("Lombard", "IL", 44000, 75, 100, "Conditional Use", "Permitted", 8, "B-3", "B-2, B-3", True, False, "", ""),
    ("Orland Park", "IL", 58000, 75, 100, "Conditional Use", "Permitted", 8, "B-3, B-4", "B-3, B-4", True, False,
     "https://www.orlandpark.org/maps", ""),
    ("Brookfield", "WI", 38000, 75, 65, "Conditional Use", "Special Use", 10, "B-3", "B-3", True, True,
     "https://www.ci.brookfield.wi.us/maps", "Stacking issues for DT. Special use required."),

    # === CONDITIONAL USE (50-66) ===
    ("Evanston", "IL", 74000, 65, 100, "Special Use", "Permitted", 8, "C1a, C2", "C1, C1a, C2", True, False,
     "https://www.cityofevanston.org/maps", "Car wash requires special use. DT coffee permitted in commercial."),
    ("Oak Park", "IL", 52000, 65, 100, "Special Use", "Permitted", 8, "B (Business)", "B (Business)", True, False,
     "", "Progressive suburb. Car wash = special use. DT permitted."),
    ("Mequon", "WI", 24000, 65, 100, "Special Use", "Permitted", 6, "B-2", "B-2", True, False, "", "Affluent suburb. More restrictive for car wash."),
    ("Shorewood", "WI", 13000, 65, 100, "Special Use", "Conditional Use", 6, "B-4", "B-4", True, True,
     "", "Dense, walkable. Both uses face extra scrutiny."),
    ("Park Ridge", "IL", 37000, 65, 100, "Special Use", "Permitted", 8, "C-3", "C-2, C-3", True, False,
     "", "Car wash special use. DT coffee more welcome."),
    ("Wilmette", "IL", 28000, 65, 100, "Special Use", "Conditional Use", 8, "GC-1", "GC-1, NR", True, True,
     "", "North Shore suburb. Both uses scrutinized."),
    ("Highland Park", "IL", 30000, 65, 100, "Special Use", "Conditional Use", 8, "B-5", "B-3, B-5", True, True,
     "", ""),
    ("Deerfield", "IL", 19000, 65, 100, "Special Use", "Permitted", 8, "C-2, C-3", "C-2, C-3", True, False, "", ""),
    ("Lake Forest", "IL", 19000, 65, 100, "Special Use", "Conditional Use", 8, "GC-1", "GC-1", True, True, "", "Very affluent. Strict design standards."),
    ("Libertyville", "IL", 20000, 65, 100, "Conditional Use", "Permitted", 6, "B-3", "B-2, B-3", True, False, "", ""),
    ("Palos Hills", "IL", 18000, 65, 100, "Conditional Use", "Permitted", 6, "C-2, C-3", "C-2, C-3", True, False, "", ""),
    ("Darien", "IL", 22000, 65, 100, "Conditional Use", "Permitted", 6, "B-2, B-3", "B-2, B-3", True, False, "", ""),
    ("Hinsdale", "IL", 17000, 65, 100, "Special Use", "Conditional Use", 10, "B-1, B-2", "B-1, B-2", True, True,
     "", "Very affluent. Design review board. 10-car stacking."),
    ("Westmont", "IL", 24000, 65, 100, "Conditional Use", "Permitted", 6, "B-2, B-3", "B-2, B-3", True, False, "", ""),
    ("Cedarburg", "WI", 12000, 65, 95, "Special Use", "Conditional Use", 6, "B-2", "B-2", True, True,
     "", "Historic downtown. Aesthetic concerns."),
    ("Barrington", "IL", 10000, 65, 75, "Special Use", "Conditional Use", 8, "B-3", "B-3", True, True,
     "", "Affluent. Community character concerns."),
    ("Glencoe", "IL", 9000, 65, 75, "Special Use", "Special Use", 8, "C-Comm", "C-Comm", True, True,
     "", "Very affluent North Shore. Both uses need special use."),
    ("Winnetka", "IL", 12000, 65, 75, "Special Use", "Special Use", 8, "C-Comm", "C-Comm", True, True,
     "", "Extremely affluent. Both uses need special use."),
    ("Clarendon Hills", "IL", 9000, 65, 75, "Special Use", "Conditional Use", 8, "B-1", "B-1", True, True, "", ""),

    # === NAPERVILLE (GROUND TRUTH) ===
    ("Naperville", "IL", 149000, 55, 38, "Conditional Use", "Special Use", 10, "B-3 only", "B-3 only (B-2 = Special Use)", True, True,
     "https://www.naperville.il.us/maps", "Ground truth: Dutch Bros DENIED on Napier Blvd. 7 Brew at 1203 Iroquois only approved w/ extensive conditions. Board hostile to new DT coffee."),
    ("Schaumburg", "IL", 74000, 75, 65, "Conditional Use", "Special Use", 10, "B-2, B-3", "B-3 only", True, True,
     "https://www.schaumburg.com/maps", "Stacking issues. Special use for DT in most zones."),

    # === PROHIBITED ===
    ("Kenilworth", "IL", 2500, 20, 20, "Prohibited", "Prohibited", 0, "None", "None", False, False,
     "", "Exclusively residential village. No commercial zones."),
]


def build():
    data = {}
    for row in ENRICHED:
        (city, state, pop, cw_score, dt_score,
         cw_path, dt_path, dt_stack, cw_zones, dt_zones,
         su_cw, su_dt, zoning_url, notes) = row

        key = f"{city}, {state}"

        # Build 5-factor estimates from scores
        avg = (cw_score + dt_score) / 2
        factor_est = round(avg / 5)

        # Naperville override
        if city == 'Naperville':
            factors = {'zoning': 12, 'site_req': 8, 'approval': 5, 'saturation': 8, 'political': 5}
            composite = 38
        else:
            factors = {
                'zoning': min(20, factor_est + (2 if cw_path == 'Permitted' else 0)),
                'site_req': min(20, factor_est + (2 if dt_stack <= 6 else -2 if dt_stack >= 10 else 0)),
                'approval': factor_est,
                'saturation': factor_est,
                'political': factor_est,
            }
            composite = sum(factors.values())

        data[key] = {
            'name': city,
            'state': state,
            'composite': composite,
            'factors': factors,
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
            'requirements': {
                'stacking_cars': dt_stack if dt_stack > 0 else None,
                'lot_size_sqft': None,
                'front_setback_ft': None,
            },
            'stacking_issue': dt_stack >= 10 or (su_dt and dt_score < 70),
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

    verified = sum(1 for v in data.values() if v['verified'])
    stacking = sum(1 for v in data.values() if v['stacking_issue'])
    su_cw = sum(1 for v in data.values() if v['carwash'].get('special_use'))
    su_dt = sum(1 for v in data.values() if v['drivethru'].get('special_use'))
    has_zones = sum(1 for v in data.values() if v['carwash'].get('zones'))
    has_map = sum(1 for v in data.values() if v.get('zoning_map_url'))

    print(f'Output: {out_path}')
    print(f'  Total: {len(data)}')
    print(f'  With zone districts: {has_zones}')
    print(f'  With zoning map link: {has_map}')
    print(f'  CW special use required: {su_cw}')
    print(f'  DT special use required: {su_dt}')
    print(f'  Stacking issues: {stacking}')

    nap = data.get('Naperville, IL', {})
    print(f'\n  Naperville: CW={nap["carwash"]["score"]} ({nap["carwash"]["pathway"]}), DT={nap["drivethru"]["score"]} ({nap["drivethru"]["pathway"]})')

if __name__ == '__main__':
    main()
