#!/usr/bin/env python3
"""
Assembles the final HTML map by embedding zoning data into the template.
Supports both first-time builds (replacing ZONING_PLACEHOLDER) and
re-builds (replacing previously embedded data between markers).
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Markers used to find and replace the zoning data in the HTML
DATA_START = '/*ZONING_DATA_START*/'
DATA_END = '/*ZONING_DATA_END*/'

def main():
    # Load zoning data
    zoning_path = os.path.join(BASE_DIR, 'data', 'zoning_data.json')
    with open(zoning_path) as f:
        zoning = json.load(f)

    # Minify
    zoning_js = json.dumps(zoning, separators=(',', ':'))
    new_data_block = f'{DATA_START}{zoning_js}{DATA_END}'

    # Read HTML
    html_path = os.path.join(BASE_DIR, 'index.html')
    with open(html_path) as f:
        html = f.read()

    replaced = False

    # Method 1: Replace between existing markers (re-build)
    if DATA_START in html and DATA_END in html:
        pattern = re.escape(DATA_START) + r'.*?' + re.escape(DATA_END)
        html = re.sub(pattern, lambda m: new_data_block, html, count=1, flags=re.DOTALL)
        replaced = True

    # Method 2: Replace ZONING_PLACEHOLDER (first build)
    elif 'ZONING_PLACEHOLDER' in html:
        html = html.replace('ZONING_PLACEHOLDER', new_data_block)
        replaced = True

    # Method 3: Find "const ZONING_DATA = " and replace the JSON object
    elif 'const ZONING_DATA = ' in html:
        # Match from "const ZONING_DATA = " to the next semicolon
        pattern = r'(const ZONING_DATA = )(\{.*?\});'
        replacement = f'\\1{new_data_block};'
        html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
        replaced = count > 0

    if not replaced:
        print("ERROR: Could not find zoning data location in HTML file.")
        print("  Looked for: ZONING_DATA_START markers, ZONING_PLACEHOLDER, or const ZONING_DATA")
        return

    # Write back
    with open(html_path, 'w') as f:
        f.write(html)

    print(f"HTML map built: {html_path}")
    print(f"  Zoning data: {len(zoning)} municipalities ({len(zoning_js)} bytes)")
    print(f"  HTML size: {len(html)} bytes ({len(html)//1024} KB)")

if __name__ == '__main__':
    main()
