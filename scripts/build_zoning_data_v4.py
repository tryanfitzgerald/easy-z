#!/usr/bin/env python3
"""
Build Zoning Data v4 — 4 Use Types: Car Wash, Drive-Thru, Collision Repair, Auto Sales/Service
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
# ENRICHED MUNICIPALITY DATA — 4 USE TYPES
# Format: (city, state, pop,
#          cw_score, dt_score, cr_score, as_score,
#          cw_pathway, dt_pathway, cr_pathway, as_pathway,
#          dt_stacking,
#          cw_zones, dt_zones, cr_zones, as_zones,
#          special_use_cw, special_use_dt, special_use_cr, special_use_as,
#          zoning_map_url, notes)
#
# Collision Repair = body shops, auto collision centers
# Auto Sales = car dealerships, sales/service/delivery centers
#
# General zoning patterns:
# - Collision repair tends to be in light industrial / heavier commercial zones
# - Auto sales tends to be in highway commercial / auto-oriented commercial
# - Both face more restrictions in dense suburban/urban areas than car washes
# - IL is generally more restrictive, IN more permissive, WI moderate
# ============================================================

ENRICHED = [
    # === HIGH SCORING (85-100) ===
    # city, state, pop, cw, dt, cr, as, cw_path, dt_path, cr_path, as_path, dt_stack,
    # cw_zones, dt_zones, cr_zones, as_zones, su_cw, su_dt, su_cr, su_as, map_url, notes
    ("Aurora", "IL", 197000, 100, 100, 85, 90, "Permitted", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3, M-1", "B-2, B-3, B-4", "M-1, M-2", "B-3, B-4, M-1", False, False, True, False,
     "https://gis.aurora-il.org", "Pro-development. Collision repair conditional in manufacturing zones."),
    ("Joliet", "IL", 148000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4, B-5", "B-4, M-1, M-2", "B-3, B-4, B-5", False, False, False, False,
     "https://www.joliet.gov/departments/community-development/gis-maps", "Business-friendly across all auto uses."),
    ("Des Plaines", "IL", 58000, 100, 100, 80, 85, "Permitted", "Permitted", "Conditional Use", "Permitted", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4", False, False, True, False,
     "https://www.desplaines.org/maps", "Collision repair conditional in heavier commercial."),
    ("Bolingbrook", "IL", 73000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", "Growth-oriented suburb."),
    ("Plainfield", "IL", 41000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", "Rapidly growing. Pro-development."),
    ("Romeoville", "IL", 39000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", ""),
    ("Addison", "IL", 36000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, M-1", "B-3", "M-1, M-2", "B-3, M-1", False, False, False, False, "", ""),
    ("Carol Stream", "IL", 40000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Glendale Heights", "IL", 34000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Bloomingdale", "IL", 22000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Bensenville", "IL", 21000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Wood Dale", "IL", 14000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Itasca", "IL", 8500, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2", False, False, False, False, "", ""),
    ("Elk Grove Village", "IL", 32000, 100, 100, 90, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False,
     "https://www.elkgrove.org/gis", ""),
    ("Waukegan", "IL", 87000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Antioch", "IL", 14000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Round Lake", "IL", 18500, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", ""),
    ("Mundelein", "IL", 31000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Grayslake", "IL", 21000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Tinley Park", "IL", 57000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Homer Glen", "IL", 21500, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Blue Island", "IL", 23000, 100, 100, 90, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", ""),
    ("Alsip", "IL", 19000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", ""),
    ("Oak Forest", "IL", 28000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Berwyn", "IL", 55000, 100, 100, 80, 85, "Permitted", "Permitted", "Conditional Use", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, True, False, "", ""),
    ("Cicero", "IL", 84000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", False, False, False, False, "", ""),
    ("Melrose Park", "IL", 23000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2", False, False, False, False, "", ""),
    ("Bellwood", "IL", 19000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2", False, False, False, False, "", ""),
    ("Warrenville", "IL", 13000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2", False, False, False, False, "", ""),
    ("Winfield", "IL", 9200, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2", False, False, False, False, "", ""),
    ("Villa Park", "IL", 22000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("Lockport", "IL", 25000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Green Bay", "WI", 104000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "C-1, C-2, C-3", "C-1, C-2, C-3", "C-3, IL", "C-2, C-3, IL", False, False, False, False,
     "https://greenbaywi.gov/gis", ""),
    ("Wauwatosa", "WI", 48000, 100, 100, 75, 80, "Permitted", "Permitted", "Conditional Use", "Conditional Use", 6,
     "C-2, C-3", "C-2, C-3", "C-3, IL", "C-3", False, False, True, True,
     "https://www.wauwatosa.net/government/gis-maps", "Collision/auto sales more restricted in residential-adjacent zones."),
    ("Oak Creek", "WI", 36500, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Sun Prairie", "WI", 32000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "CC, HC", "CC, HC", "HC, LI", "CC, HC", False, False, False, False, "", ""),
    ("Menomonee Falls", "WI", 35000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", False, False, False, False, "", ""),
    ("Germantown", "WI", 20000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", False, False, False, False, "", ""),
    ("West Bend", "WI", 32000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-3", "B-3", "B-3, M-1", "B-3", False, False, False, False, "", ""),
    ("De Pere", "WI", 24000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, IL", "C-1, C-2", False, False, False, False, "", ""),
    ("Ashwaubenon", "WI", 17000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, IL", "C-1, C-2", False, False, False, False, "", ""),
    ("Grafton", "WI", 11600, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2", False, False, False, False, "", ""),
    ("Port Washington", "WI", 11600, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-2", "B-2", "B-2, M-1", "B-2", False, False, False, False, "", ""),
    ("Fitchburg", "WI", 28000, 100, 100, 90, 95, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "CG, CH", "CG, CH", "CH, LI", "CG, CH", False, False, False, False, "", ""),
    ("Middleton", "WI", 19000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-2", "C-2", "C-2, M-1", "C-2", False, False, False, False, "", ""),
    ("Glendale", "WI", 13000, 100, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "B-3", "B-3", "B-3, M-1", "B-3", False, False, False, False, "", ""),

    # === PERMITTED WITH NOTES (85-99) ===
    ("Madison", "WI", 269000, 95, 100, 70, 75, "Permitted", "Permitted", "Conditional Use", "Conditional Use", 8,
     "CC, CC-T", "CC, NMX, TSS", "IL, IG", "CC-T, SE", False, False, True, True,
     "https://cityofmadison.maps.arcgis.com", "Collision/auto sales face more scrutiny in urban core."),
    ("Waukesha", "WI", 72000, 95, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 6,
     "B-3, B-4", "B-3, B-4, B-5", "B-4, M-1", "B-3, B-4, B-5", False, False, False, False,
     "https://www.ci.waukesha.wi.us/gis", ""),
    ("Verona", "WI", 13800, 95, 100, 85, 90, "Permitted", "Permitted", "Permitted", "Permitted", 5,
     "C-1, C-2", "C-1, C-2", "C-2, M-1", "C-1, C-2", False, False, False, False, "", ""),
    ("Chicago", "IL", 2700000, 95, 85, 60, 65, "Conditional Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B3-2, C1-2, C1-3", "B3-2, C1-2, C1-3", "C2-3, M1-2", "C2-2, C2-3, M1-2", False, False, True, True,
     "https://gisapps.chicago.gov/ZoningMapWeb/", "Collision/auto sales require special use. Aldermanic approval key."),

    # === LIKELY PERMITTED (67-84) ===
    ("Milwaukee", "WI", 577000, 80, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "LB2, CS", "LB2, CS, IL", "CS, IL, IG", "CS, IL", True, False, True, True,
     "https://city.milwaukee.gov/maps", "Auto-intensive uses need CU in most zones."),
    ("Wheaton", "IL", 53000, 75, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4", True, False, True, True, "", ""),
    ("Skokie", "IL", 65000, 75, 100, 65, 70, "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B2, B3", "B2, B3", "B3, M-1", "B2, B3", True, False, True, True,
     "https://www.skokie.org/maps", "Collision repair special use in commercial."),
    ("Arlington Heights", "IL", 76000, 75, 85, 60, 65, "Conditional Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", True, True, True, True,
     "https://www.vah.com/maps", "All auto uses face scrutiny."),
    ("Downers Grove", "IL", 49000, 75, 85, 65, 70, "Conditional Use", "Conditional Use", "Conditional Use", "Conditional Use", 8,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", True, True, True, True,
     "https://www.downers.us/maps", ""),
    ("New Berlin", "WI", 39000, 75, 100, 80, 85, "Conditional Use", "Permitted", "Permitted", "Permitted", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3", True, False, False, False, "", ""),
    ("Palatine", "IL", 68000, 75, 100, 65, 70, "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", True, False, True, True, "", ""),
    ("Rolling Meadows", "IL", 24000, 75, 100, 75, 80, "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "C-3", "C-3, C-4", "C-4, M-1", "C-3, C-4", True, False, True, False, "", ""),
    ("Mount Prospect", "IL", 54000, 75, 100, 65, 70, "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", True, False, True, True, "", ""),
    ("Hoffman Estates", "IL", 52000, 75, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3", True, False, True, True, "", ""),
    ("Northbrook", "IL", 33000, 75, 100, 60, 65, "Conditional Use", "Permitted", "Special Use", "Special Use", 8,
     "C-3", "C-2, C-3", "C-4, M-1", "C-3, C-4", True, False, True, True,
     "https://www.northbrook.il.us/maps", "Affluent. Auto-intensive uses face resistance."),
    ("Glenview", "IL", 47000, 75, 100, 60, 65, "Conditional Use", "Permitted", "Special Use", "Special Use", 8,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3", True, False, True, True, "", ""),
    ("Elmhurst", "IL", 46000, 75, 100, 65, 70, "Conditional Use", "Permitted", "Special Use", "Conditional Use", 8,
     "C-3, C-4", "C-3, C-4", "C-4, M-1", "C-3, C-4", True, False, True, True, "", ""),
    ("Lombard", "IL", 44000, 75, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3", True, False, True, True, "", ""),
    ("Orland Park", "IL", 58000, 75, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 8,
     "B-3, B-4", "B-3, B-4", "B-4, M-1", "B-3, B-4", True, False, True, True,
     "https://www.orlandpark.org/maps", ""),
    ("Brookfield", "WI", 38000, 75, 65, 70, 75, "Conditional Use", "Special Use", "Conditional Use", "Conditional Use", 10,
     "B-3", "B-3", "B-3, M-1", "B-3", True, True, True, True,
     "https://www.ci.brookfield.wi.us/maps", "Stacking issues for DT. Auto uses face scrutiny."),

    # === CONDITIONAL USE (50-66) ===
    ("Evanston", "IL", 74000, 65, 100, 50, 55, "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C1a, C2", "C1, C1a, C2", "C2, I1", "C2", True, False, True, True,
     "https://www.cityofevanston.org/maps", "Dense urban. Auto-intensive uses very restricted."),
    ("Oak Park", "IL", 52000, 65, 100, 45, 50, "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "B (Business)", "B (Business)", "B, I (Industrial)", "B (Business)", True, False, True, True,
     "", "Progressive suburb. Anti-auto sprawl sentiment."),
    ("Mequon", "WI", 24000, 65, 100, 60, 65, "Special Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-2", "B-2", "B-2, M-1", "B-2", True, False, True, True, "", "Affluent suburb."),
    ("Shorewood", "WI", 13000, 65, 100, 40, 45, "Special Use", "Conditional Use", "Prohibited", "Prohibited", 6,
     "B-4", "B-4", "None", "None", True, True, False, False,
     "", "Dense, walkable. No auto-intensive uses allowed."),
    ("Park Ridge", "IL", 37000, 65, 100, 55, 60, "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C-3", "C-2, C-3", "C-4, M-1", "C-3", True, False, True, True, "", ""),
    ("Wilmette", "IL", 28000, 65, 100, 45, 50, "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "GC-1", "GC-1, NR", "GC-1", "GC-1", True, True, True, True, "", "North Shore. Very restrictive for auto uses."),
    ("Highland Park", "IL", 30000, 65, 100, 45, 50, "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-5", "B-3, B-5", "B-5, M-1", "B-5", True, True, True, True, "", ""),
    ("Deerfield", "IL", 19000, 65, 100, 55, 60, "Special Use", "Permitted", "Special Use", "Special Use", 8,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-3", True, False, True, True, "", ""),
    ("Lake Forest", "IL", 19000, 65, 100, 40, 45, "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "GC-1", "GC-1", "GC-1, LI", "GC-1", True, True, True, True, "", "Very affluent. Strict design standards."),
    ("Libertyville", "IL", 20000, 65, 100, 65, 70, "Conditional Use", "Permitted", "Conditional Use", "Conditional Use", 6,
     "B-3", "B-2, B-3", "B-3, M-1", "B-3", True, False, True, True, "", ""),
    ("Palos Hills", "IL", 18000, 65, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "C-2, C-3", "C-2, C-3", "C-3, M-1", "C-2, C-3", True, False, True, False, "", ""),
    ("Darien", "IL", 22000, 65, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", True, False, True, False, "", ""),
    ("Hinsdale", "IL", 17000, 65, 100, 35, 40, "Special Use", "Conditional Use", "Prohibited", "Special Use", 10,
     "B-1, B-2", "B-1, B-2", "None", "B-2", True, True, False, True,
     "", "Very affluent. No collision repair allowed. 10-car stacking."),
    ("Westmont", "IL", 24000, 65, 100, 70, 75, "Conditional Use", "Permitted", "Conditional Use", "Permitted", 6,
     "B-2, B-3", "B-2, B-3", "B-3, M-1", "B-2, B-3", True, False, True, False, "", ""),
    ("Cedarburg", "WI", 12000, 65, 95, 70, 75, "Special Use", "Conditional Use", "Conditional Use", "Conditional Use", 6,
     "B-2", "B-2", "B-2, M-1", "B-2", True, True, True, True, "", "Historic downtown. Aesthetic concerns."),
    ("Barrington", "IL", 10000, 65, 75, 55, 60, "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-3", "B-3", "B-3, M-1", "B-3", True, True, True, True, "", "Affluent. Community character concerns."),
    ("Glencoe", "IL", 9000, 65, 75, 35, 40, "Special Use", "Special Use", "Prohibited", "Prohibited", 8,
     "C-Comm", "C-Comm", "None", "None", True, True, False, False, "", "Very affluent North Shore. Auto uses restricted."),
    ("Winnetka", "IL", 12000, 65, 75, 35, 40, "Special Use", "Special Use", "Prohibited", "Prohibited", 8,
     "C-Comm", "C-Comm", "None", "None", True, True, False, False, "", "Extremely affluent. Auto uses restricted."),
    ("Clarendon Hills", "IL", 9000, 65, 75, 55, 60, "Special Use", "Conditional Use", "Special Use", "Special Use", 8,
     "B-1", "B-1", "B-1, M-1", "B-1", True, True, True, True, "", ""),

    # === NAPERVILLE (GROUND TRUTH) ===
    ("Naperville", "IL", 149000, 55, 38, 50, 55, "Conditional Use", "Special Use", "Special Use", "Conditional Use", 10,
     "B-3 only", "B-3 only (B-2 = Special Use)", "B-3, M-1", "B-3, B-4",  True, True, True, True,
     "https://www.naperville.il.us/maps", "Ground truth: Dutch Bros DENIED on Napier Blvd. 7 Brew at 1203 Iroquois only approved w/ extensive conditions."),
    ("Schaumburg", "IL", 74000, 75, 65, 60, 65, "Conditional Use", "Special Use", "Special Use", "Conditional Use", 10,
     "B-2, B-3", "B-3 only", "B-3, M-1", "B-2, B-3", True, True, True, True,
     "https://www.schaumburg.com/maps", "Stacking issues. Auto-intensive uses face extra scrutiny."),

    # === PROHIBITED ===
    ("Kenilworth", "IL", 2500, 20, 20, 10, 10, "Prohibited", "Prohibited", "Prohibited", "Prohibited", 0,
     "None", "None", "None", "None", False, False, False, False,
     "", "Exclusively residential village. No commercial zones."),
]


def build():
    data = {}
    for row in ENRICHED:
        (city, state, pop,
         cw_score, dt_score, cr_score, as_score,
         cw_path, dt_path, cr_path, as_path,
         dt_stack,
         cw_zones, dt_zones, cr_zones, as_zones,
         su_cw, su_dt, su_cr, su_as,
         zoning_url, notes) = row

        key = f"{city}, {state}"

        # Build 5-factor estimates from scores
        avg = (cw_score + dt_score + cr_score + as_score) / 4
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
    su_cr = sum(1 for v in data.values() if v['collision'].get('special_use'))
    su_as = sum(1 for v in data.values() if v['autosales'].get('special_use'))
    has_map = sum(1 for v in data.values() if v.get('zoning_map_url'))

    print(f'Output: {out_path}')
    print(f'  Total: {len(data)}')
    print(f'  With zoning map link: {has_map}')
    print(f'  CW special use: {su_cw}')
    print(f'  DT special use: {su_dt}')
    print(f'  Collision special use: {su_cr}')
    print(f'  Auto Sales special use: {su_as}')
    print(f'  Stacking issues: {stacking}')

    nap = data.get('Naperville, IL', {})
    sep = ', '
    print(f'\n  Naperville: CW={nap["carwash"]["score"]}{sep}DT={nap["drivethru"]["score"]}{sep}CR={nap["collision"]["score"]}{sep}AS={nap["autosales"]["score"]}')

if __name__ == '__main__':
    main()
