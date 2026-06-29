#!/usr/bin/env python3
"""Build self-contained AH comparison dashboard with embedded JSON data."""

import json

# Load data
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r') as f:
    data = json.load(f)

# Pretty-print the JSON data (multi-line, readable)
data_json_str = json.dumps(data, ensure_ascii=False, indent=2)

# Read the HTML template
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_template_v3.html', 'r') as f:
    template = f.read()

# Replace the fetch section with embedded data + JSON.parse
# The template has a <script> block that starts with fetch(...)
# We'll replace the entire script block

old_script = """<script>
function fmtDate(s) { return s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8); }
function calcMA(data, period) {
  return data.map(function(d, i) {
    if (i < period - 1) return null;
    var sum = 0;
    for (var j = 0; j < period; j++) sum += data[i - j].close;
    return +(sum / period).toFixed(2);
  });
}

var upC = '#e74c3c', downC = '#2ecc71', upB = '#c0392b', downB = '#27ae60';

// Load data from external JSON file
fetch('澜起科技_AH对比_图表数据.json')
  .then(function(r) { return r.json(); })
  .then(function(DATA) {"""

new_script = """<script type="application/json" id="chart-data">
""" + data_json_str + """
</script>
<script>
function fmtDate(s) { return s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8); }
function calcMA(data, period) {
  return data.map(function(d, i) {
    if (i < period - 1) return null;
    var sum = 0;
    for (var j = 0; j < period; j++) sum += data[i - j].close;
    return +(sum / period).toFixed(2);
  });
}

var upC = '#e74c3c', downC = '#2ecc71', upB = '#c0392b', downB = '#27ae60';

// Load embedded data
var DATA = JSON.parse(document.getElementById('chart-data').textContent);
(function() {"""

# Also remove the .catch block at the end
old_catch = """  })
  .catch(function(err) {
    document.getElementById('summary-row').innerHTML = '<div class="loading">数据加载失败: ' + err.message + '</div>';
    console.error('Data load error:', err);
  });"""

new_catch = """  })();
})();

window.addEventListener('resize', function() {
  ['chart-a-kline','chart-hk-kline','chart-compare-price','chart-premium','chart-compare-vol','chart-compare-pct'].forEach(function(id) {
    var i = echarts.getInstanceByDom(document.getElementById(id));
    if (i) i.resize();
  });
});"""

html = template.replace(old_script, new_script).replace(old_catch, new_catch)

# Also remove the duplicate resize listener inside the fetch block
# The template has window.addEventListener inside the .then block, let's check
# Actually the old template has resize inside the .then block which we already
# wrapped with (function(){...})(). We need to remove it from inside.

# Let me just rebuild the entire script section cleanly
# First, remove the old resize block from inside the callback
old_resize_inside = """    // Resize
    window.addEventListener('resize', function() {
      ['chart-a-kline','chart-hk-kline','chart-compare-price','chart-premium','chart-compare-vol','chart-compare-pct'].forEach(function(id) {
        var i = echarts.getInstanceByDom(document.getElementById(id));
        if (i) i.resize();
      });
    });"""

html = html.replace(old_resize_inside, "")

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html', 'w') as f:
    f.write(html)

import os
size = os.path.getsize('/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html')
print(f"HTML file built: {size/1024:.1f} KB")

# Verify the JSON block is properly embedded
lines = html.split('\n')
data_tag_start = None
data_tag_end = None
for i, line in enumerate(lines):
    if '<script type="application/json" id="chart-data">' in line:
        data_tag_start = i
    if '</script>' in line and data_tag_start is not None and data_tag_end is None and i > data_tag_start:
        data_tag_end = i
        break

if data_tag_start and data_tag_end:
    print(f"JSON data block: lines {data_tag_start+1} to {data_tag_end+1} ({data_tag_end - data_tag_start} lines)")
else:
    print("WARNING: Could not find JSON data block!")
