#!/usr/bin/env python3
"""Build self-contained AH dashboard: embed JSON data in <script type="application/json"> tag."""

import json

# Load data
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r') as f:
    data = json.load(f)

# Format as multi-line JSON (indent=2) so the browser can parse it reliably
# This avoids the "single-line too long" issue that caused chart failures before
data_json_str = json.dumps(data, ensure_ascii=False, indent=2)

# Read template
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_template_v3.html', 'r') as f:
    template = f.read()

# Replace placeholder with actual data
html = template.replace('JSON_DATA_PLACEHOLDER', data_json_str)

# Write final HTML
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html', 'w') as f:
    f.write(html)

import os
size = os.path.getsize('/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html')
print(f"HTML file size: {size/1024:.1f} KB")

# Verify: count lines in the JSON data block
lines = html.split('\n')
start_line = None
end_line = None
for i, line in enumerate(lines):
    if '<script type="application/json" id="chart-data">' in line:
        start_line = i
    if start_line is not None and '</script>' in line and i > start_line:
        end_line = i
        break

if start_line and end_line:
    json_lines = end_line - start_line - 1
    print(f"JSON data block: {json_lines} lines (from line {start_line+1} to {end_line+1})")
    # Check it's truly multi-line
    if json_lines > 10:
        print("✅ Data is properly multi-line - should parse correctly in browser")
    else:
        print("⚠️ Data may still be on too few lines")
else:
    print("ERROR: Could not find JSON data block!")
