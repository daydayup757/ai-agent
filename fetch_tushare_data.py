import tushare as ts
import pandas as pd
import json
from datetime import datetime, timedelta

# Initialize with user's token
ts.set_token('f67c3daa067442fd4f79989f010d9ea2f40b0c3aa3ea0128600cd647')
pro = ts.pro_api()

# 澜起科技 stock code: 688008.SH
# Calculate date range: past year
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

print(f"Fetching data for 688008.SH from {start_date} to {end_date}...")

# Fetch daily data
df = pro.daily(ts_code='688008.SH', start_date=start_date, end_date=end_date)

if df is None or df.empty:
    print("No data returned!")
else:
    # Sort by trade_date ascending for chart display
    df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)

    # Save to CSV
    csv_path = '/Users/daydayup/Desktop/Agent/澜起科技_交易数据.csv'
    df.to_csv(csv_path, index=False)
    print(f"CSV saved to {csv_path}")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['trade_date'].iloc[0]} ~ {df['trade_date'].iloc[-1]}")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head())

    # Also save as JSON for HTML chart
    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'date': row['trade_date'],
            'open': float(row['open']),
            'close': float(row['close']),
            'low': float(row['low']),
            'high': float(row['high']),
            'vol': float(row['vol']),       # 成交量（手）
            'amount': float(row['amount']),  # 成交额（千元）
            'pct_chg': float(row.get('pct_chg', 0)) if pd.notna(row.get('pct_chg', 0)) else 0,
            'pre_close': float(row['pre_close']) if pd.notna(row['pre_close']) else float(row['open'])
        })

    json_path = '/Users/daydayup/Desktop/Agent/澜起科技_图表数据.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, ensure_ascii=False)
    print(f"JSON saved to {json_path}")
