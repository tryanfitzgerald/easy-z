#!/usr/bin/env python3
"""
XLSX → JSON → HTML Pipeline
Reads the research workbook, generates zoning_data.json, and rebuilds the HTML map.
Run this after making edits to the research workbook.

Usage:
    python3 scripts/xlsx_to_json.py
"""
import subprocess, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, 'scripts')

print("=" * 50)
print("Easy Z: XLSX → JSON → HTML Pipeline")
print("=" * 50)

# Step 1: Build zoning data from workbook
print("\n[1/2] Reading research workbook → zoning_data.json")
r1 = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'build_zoning_data_v2.py')],
                     capture_output=True, text=True, cwd=BASE)
print(r1.stdout)
if r1.returncode != 0:
    print(f"ERROR: {r1.stderr}")
    sys.exit(1)

# Step 2: Rebuild HTML map
print("[2/2] Injecting data → municipal_zoning_heatmap.html")
r2 = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'build_html_map.py')],
                     capture_output=True, text=True, cwd=BASE)
print(r2.stdout)
if r2.returncode != 0:
    print(f"ERROR: {r2.stderr}")
    sys.exit(1)

print("\n" + "=" * 50)
print("Done! Open municipal_zoning_heatmap.html in your browser.")
print("=" * 50)
