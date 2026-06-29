import json

# Read the JSON data
with open('/Users/daydayup/Desktop/Agent/澜起科技_图表数据.json', 'r', encoding='utf-8') as f:
    chart_data = json.load(f)

# Read the template HTML
with open('/Users/daydayup/Desktop/Agent/澜起科技_kline_template.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Embed the JSON data into the HTML
html_final = html_template.replace('RAW_DATA_PLACEHOLDER', json.dumps(chart_data))

# Write the final HTML
output_path = '/Users/daydayup/Desktop/Agent/澜起科技_K线图.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"Final HTML saved to {output_path}")
print(f"Data points embedded: {len(chart_data)}")
