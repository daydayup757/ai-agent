import json

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r', encoding='utf-8') as f:
    comparison = json.load(f)

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_template_v2.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

html_final = html_template.replace('COMPARISON_DATA_PLACEHOLDER', json.dumps(comparison))

output_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比看板.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"Final HTML saved to {output_path}")
print(f"A-share: {len(comparison['a_share'])} | HK: {len(comparison['hk_share'])} | premium_full: {len(comparison['premium_full'])} | premium_overlap: {len(comparison['premium'])}")
