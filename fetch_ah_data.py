import tushare as ts
import pandas as pd
import json
from datetime import datetime, timedelta

# Initialize with user's token
ts.set_token('f67c3daa067442fd4f79989f010d9ea2f40b0c3aa3ea0128600cd647')
pro = ts.pro_api()

end_date = datetime.now().strftime('%Y%m%d')
# Start from a year ago
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

print(f"=== Fetching 澜起科技 A股 (688008.SH) ===")
df_a = pro.daily(ts_code='688008.SH', start_date=start_date, end_date=end_date)
if df_a is not None and not df_a.empty:
    df_a = df_a.sort_values('trade_date', ascending=True).reset_index(drop=True)
    df_a.to_csv('/Users/daydayup/Desktop/Agent/澜起科技_A股_交易数据.csv', index=False)
    print(f"A股: {len(df_a)} records, {df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}")
    print(f"A股 columns: {df_a.columns.tolist()}")
else:
    print("A股: No data!")

# HK stock: 澜起科技 06809.HK (listed Feb 2026, so data will be limited)
print(f"\n=== Fetching 澜起科技 港股 (06809.HK) ===")

# Try hk_daily first
try:
    df_hk = pro.hk_daily(ts_code='06809.HK', start_date=start_date, end_date=end_date)
    if df_hk is not None and not df_hk.empty:
        df_hk = df_hk.sort_values('trade_date', ascending=True).reset_index(drop=True)
        print(f"港股 (hk_daily): {len(df_hk)} records")
        print(f"港股 columns: {df_hk.columns.tolist()}")
        print(df_hk.head())
    else:
        print("hk_daily returned empty, trying daily...")
        raise Exception("empty")
except Exception as e:
    print(f"hk_daily failed ({e}), trying daily API with HK code...")
    try:
        df_hk = pro.daily(ts_code='06809.HK', start_date=start_date, end_date=end_date)
        if df_hk is not None and not df_hk.empty:
            df_hk = df_hk.sort_values('trade_date', ascending=True).reset_index(drop=True)
            print(f"港股 (daily): {len(df_hk)} records")
            print(f"港股 columns: {df_hk.columns.tolist()}")
        else:
            print("港股: No data from daily API either!")
            df_hk = None
    except Exception as e2:
        print(f"daily API also failed: {e2}")
        df_hk = None

if df_hk is not None and not df_hk.empty:
    df_hk.to_csv('/Users/daydayup/Desktop/Agent/澜起科技_港股_交易数据.csv', index=False)
    print(f"港股 saved: {df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}")

    # Also save as JSON for comparison chart
    def df_to_chart_json(df, label):
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['trade_date'],
                'label': label,
                'open': float(row['open']),
                'close': float(row['close']),
                'low': float(row['low']),
                'high': float(row['high']),
                'vol': float(row.get('vol', 0)),
                'amount': float(row.get('amount', 0)),
                'pre_close': float(row['pre_close']) if pd.notna(row.get('pre_close', 0)) else float(row['open']),
                'pct_chg': float(row.get('pct_chg', 0)) if pd.notna(row.get('pct_chg', 0)) else 0.0,
            }
            result.append(item)
        return result

    a_data = df_to_chart_json(df_a, 'A')
    hk_data = df_to_chart_json(df_hk, 'HK')

    # Also compute AH premium ratio for overlapping dates
    # Premium = (A_price / HK_price / exchange_rate - 1) * 100
    # We need CNY/HKD exchange rate. Let's fetch it
    print("\n=== Fetching CNY/HKD exchange rate ===")
    try:
        df_fx = pro.fx_daily(ts_code='USDCNY.FX', start_date=start_date, end_date=end_date)
        # Actually, let's try HKDCNY or find the right code
    except:
        pass

    # Save comparison data
    comparison_data = {
        'a_share': a_data,
        'hk_share': hk_data,
        'a_stock_code': '688008.SH',
        'hk_stock_code': '06809.HK',
        'a_range': f"{df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}",
        'hk_range': f"{df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}",
        'a_count': len(df_a),
        'hk_count': len(df_hk),
    }

    json_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False)
    print(f"\nComparison JSON saved to {json_path}")
else:
    print("\nWARNING: No HK data available. Will create dashboard with A-share data only.")
