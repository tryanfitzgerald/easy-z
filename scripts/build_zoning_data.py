#!/usr/bin/env python3
"""
Build zoning data JSON from verified municipality scores.
Extracts data from 100_MUNICIPALITIES_HEAT_MAP_COMPLETE.md
and generates a lookup table keyed by "CityName, ST" for matching
against Census boundary data at runtime.
"""

import json
import re
import os

# Verified municipality data extracted from the markdown analysis
# Format: (city, state, carwash_score, coffee_score, population_approx)
VERIFIED_MUNICIPALITIES = [
    # PERFECT SCORE (100) cities
    ("Aurora", "IL", 100, 100, 197000),
    ("Joliet", "IL", 100, 100, 148000),
    ("Des Plaines", "IL", 100, 100, 58000),
    ("Wauwatosa", "WI", 100, 100, 48000),
    ("Oak Creek", "WI", 100, 100, 36500),
    ("Sun Prairie", "WI", 100, 100, 32000),
    ("Plainfield", "IL", 100, 100, 41000),
    ("Bolingbrook", "IL", 100, 100, 73000),
    ("Romeoville", "IL", 100, 100, 39000),
    ("Addison", "IL", 100, 100, 36000),
    ("Carol Stream", "IL", 100, 100, 40000),
    ("Glendale Heights", "IL", 100, 100, 34000),
    ("Bloomingdale", "IL", 100, 100, 22000),
    ("Bensenville", "IL", 100, 100, 21000),
    ("Wood Dale", "IL", 100, 100, 13000),
    ("Itasca", "IL", 100, 100, 8500),
    ("Elk Grove Village", "IL", 100, 100, 32000),
    ("Waukegan", "IL", 100, 100, 87000),
    ("Antioch", "IL", 100, 100, 14000),
    ("Round Lake", "IL", 100, 100, 18500),
    ("Mundelein", "IL", 100, 100, 31000),
    ("Grayslake", "IL", 100, 100, 21000),
    ("Tinley Park", "IL", 100, 100, 57000),
    ("Homer Glen", "IL", 100, 100, 21500),
    ("Blue Island", "IL", 100, 100, 23000),
    ("Alsip", "IL", 100, 100, 19000),
    ("Oak Forest", "IL", 100, 100, 28000),
    ("Berwyn", "IL", 100, 100, 55000),
    ("Cicero", "IL", 100, 100, 84000),
    ("Melrose Park", "IL", 100, 100, 23000),
    ("Bellwood", "IL", 100, 100, 19000),
    ("Green Bay", "WI", 100, 100, 104000),
    ("Warrenville", "IL", 100, 100, 13000),
    ("Winfield", "IL", 100, 100, 9200),
    ("Villa Park", "IL", 100, 100, 22000),
    ("Menomonee Falls", "WI", 100, 100, 35000),
    ("Germantown", "WI", 100, 100, 20000),
    ("West Bend", "WI", 100, 100, 32000),
    ("De Pere", "WI", 100, 100, 24000),
    ("Ashwaubenon", "WI", 100, 100, 17000),
    ("Grafton", "WI", 100, 100, 11600),
    ("Port Washington", "WI", 100, 100, 11600),
    ("Lockport", "IL", 100, 100, 25000),
    ("Fitchburg", "WI", 100, 100, 28000),
    ("Middleton", "WI", 100, 100, 19000),
    ("Glendale", "WI", 100, 100, 13000),
    # EXCELLENT TIER (97-98)
    ("Madison", "WI", 95, 100, 269000),
    ("Waukesha", "WI", 95, 100, 72000),
    ("Verona", "WI", 95, 100, 13800),
    # VERY GOOD TIER (82-90)
    ("Chicago", "IL", 95, 85, 2700000),
    ("Milwaukee", "WI", 80, 100, 577000),
    ("Wheaton", "IL", 75, 100, 53000),
    ("Skokie", "IL", 75, 100, 65000),
    ("Arlington Heights", "IL", 75, 85, 76000),
    ("Downers Grove", "IL", 75, 85, 49000),
    ("New Berlin", "WI", 75, 100, 39000),
    ("Palatine", "IL", 75, 100, 68000),
    ("Rolling Meadows", "IL", 75, 100, 24000),
    ("Mount Prospect", "IL", 75, 100, 54000),
    ("Hoffman Estates", "IL", 75, 100, 52000),
    ("Northbrook", "IL", 75, 100, 33000),
    ("Glenview", "IL", 75, 100, 47000),
    ("Elmhurst", "IL", 75, 100, 46000),
    ("Lombard", "IL", 75, 100, 44000),
    ("Orland Park", "IL", 75, 100, 58000),
    ("Evanston", "IL", 65, 100, 74000),
    ("Oak Park", "IL", 65, 100, 52000),
    ("Mequon", "WI", 65, 100, 24000),
    ("Shorewood", "WI", 65, 100, 13000),
    ("Park Ridge", "IL", 65, 100, 37000),
    ("Wilmette", "IL", 65, 100, 28000),
    ("Highland Park", "IL", 65, 100, 30000),
    ("Deerfield", "IL", 65, 100, 19000),
    ("Lake Forest", "IL", 65, 100, 19000),
    ("Libertyville", "IL", 65, 100, 20000),
    ("Palos Hills", "IL", 65, 100, 18000),
    ("Darien", "IL", 65, 100, 22000),
    ("Hinsdale", "IL", 65, 100, 17000),
    ("Westmont", "IL", 65, 100, 24000),
    ("Cedarburg", "WI", 65, 95, 12000),
    # ACCEPTABLE TIER (70-75)
    ("Brookfield", "WI", 75, 65, 38000),
    ("Naperville", "IL", 75, 65, 149000),
    ("Schaumburg", "IL", 75, 65, 74000),
    ("Barrington", "IL", 65, 75, 10000),
    ("Glencoe", "IL", 65, 75, 9000),
    ("Winnetka", "IL", 65, 75, 12000),
    ("Clarendon Hills", "IL", 65, 75, 9000),
    # RESTRICTIVE
    ("Kenilworth", "IL", 20, 20, 2500),
]


def score_to_status(score):
    """Convert numeric score to human-readable status."""
    if score >= 85:
        return "permitted"
    elif score >= 67:
        return "likely_permitted"
    elif score >= 50:
        return "conditional"
    elif score >= 25:
        return "restrictive"
    else:
        return "prohibited"


def has_stacking_issue(city, state, carwash_score, coffee_score):
    """Determine if municipality has known stacking/queuing restrictions."""
    # Cities known or likely to have stacking restrictions based on scores
    # Drive-thru score significantly lower than carwash = likely stacking issue
    if coffee_score < carwash_score - 15:
        return True
    # Known restrictive North Shore / affluent suburbs
    restrictive_cities = [
        "Kenilworth", "Winnetka", "Glencoe", "Barrington",
        "Naperville", "Schaumburg", "Brookfield", "Clarendon Hills"
    ]
    if city in restrictive_cities and coffee_score < 75:
        return True
    return False


def build_zoning_data():
    """Build complete zoning data dictionary."""
    zoning = {}

    for city, state, cw_score, dt_score, pop in VERIFIED_MUNICIPALITIES:
        key = f"{city}, {state}"
        stacking = has_stacking_issue(city, state, cw_score, dt_score)

        zoning[key] = {
            "name": city,
            "state": state,
            "carwash": {
                "status": score_to_status(cw_score),
                "score": cw_score
            },
            "drivethru": {
                "status": score_to_status(dt_score),
                "score": dt_score
            },
            "stacking_issue": stacking,
            "verified": True,
            "population": pop
        }

    return zoning


def main():
    zoning = build_zoning_data()

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "zoning_data.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(zoning, f, indent=2)

    # Print summary
    verified = sum(1 for v in zoning.values() if v["verified"])
    stacking = sum(1 for v in zoning.values() if v["stacking_issue"])
    permitted_cw = sum(1 for v in zoning.values()
                       if v["carwash"]["score"] >= 67)
    permitted_dt = sum(1 for v in zoning.values()
                       if v["drivethru"]["score"] >= 67)

    print(f"Zoning data built: {output_path}")
    print(f"  Verified municipalities: {verified}")
    print(f"  Carwash-friendly (67+): {permitted_cw}")
    print(f"  Drive-thru-friendly (67+): {permitted_dt}")
    print(f"  Stacking issues flagged: {stacking}")


if __name__ == "__main__":
    main()
