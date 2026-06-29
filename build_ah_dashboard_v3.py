import json

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r', encoding='utf-8') as f:
    comparison = json.load(f)

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_template_v3.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Embed data in the <script type="application/json"> block
# JSON is properly formatted, not a 94KB single-line JS expression
html_final = html_template.replace('JSON_DATA_PLACEHOLDER', json.dumps(comparison))

output_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"Saved to {output_path}")
print(f"File size: {len(html_final)} bytes")

# Verify: check that the DATA script block exists
data_start = html_final.find('<script type="application/json" id="chart-data">')
data_end = html_final.find('</script>', data_start)
print(f"JSON script block: from char {data_start} to {data_end}")
print(f"JSON block length: {data_end - data_start - len('<script type=\"application/json\" id=\"chart-data\">')} chars")
