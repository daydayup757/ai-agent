import json

# Read the comparison data
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r', encoding='utf-8') as f:
    comparison = json.load(f)

# Read the template HTML
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_template.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Embed the JSON data into the HTML
html_final = html_template.replace('COMPARISON_DATA_PLACEHOLDER', json.dumps(comparison))

# Write the final HTML
output_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"Final HTML saved to {output_path}")
print(f"A-share data points: {len(comparison['a_share'])}")
print(f"HK data points: {len(comparison['hk_share'])}")
print(f"Premium overlap points: {len(comparison['premium'])}")
