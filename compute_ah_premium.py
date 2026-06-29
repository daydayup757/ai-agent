import tushare as ts
import pandas as pd
import json
from datetime import datetime, timedelta

ts.set_token('f67c3daa067442fd4f79989f010d9ea2f40b0c3aa3ea3ea0128600cd647')
pro = ts.pro_api()

end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

# Try to get CNY/HKD exchange rate from Tushare
# Tushare FX codes: HKDCNY.FX might be available
print("=== Trying FX rate APIs ===")

# Try various FX code formats
fx_codes = ['HKDCNY.FX', 'USDCNY.FX', 'CNYHKD.FX']
df_fx = None

for code in fx_codes:
    try:
        print(f"Trying {code}...")
        df_fx = pro.fx_daily(ts_code=code, start_date=start_date, end_date=end_date)
        if df_fx is not None and not df_fx.empty:
            print(f"Found FX data with {code}: {len(df_fx)} records")
            print(f"Columns: {df_fx.columns.tolist()}")
            print(df_fx.head())
            break
        else:
            print(f"{code}: empty")
    except Exception as e:
        print(f"{code}: error - {e}")

if df_fx is None or df_fx.empty:
    print("No FX data from Tushare. Using approximate rate.")
    # We'll use a hardcoded approximate rate for HKD/CNY
    # 1 HKD ≈ 0.91 CNY (typical rate)
    rate = 0.91
    print(f"Using approximate rate: 1 HKD = {rate} CNY")
else:
    df_fx = df_fx.sort_values('trade_date', ascending=True).reset_index(drop=True)
    # Save FX data
    df_fx.to_csv('/Users/daydayup/Desktop/Agent/汇率_HKDCNY.csv', index=False)
    print(f"FX data saved")

# Now compute AH premium for overlapping dates
# Load the saved comparison data
with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r', encoding='utf-8') as f:
    comparison = json.load(f)

a_data = comparison['a_share']
hk_data = comparison['hk_share']

# Create date-indexed maps
a_map = {d['date']: d for d in a_data}
hk_map = {d['date']: d for d in hk_data}

# Find overlapping dates
a_dates = set(d['date'] for d in a_data)
hk_dates = set(d['date'] for d in hk_data)
overlap_dates = sorted(a_dates & hk_dates)

print(f"\nOverlapping dates: {len(overlap_dates)}")
if overlap_dates:
    print(f"Range: {overlap_dates[0]} ~ {overlap_dates[-1]}")

# Compute AH premium ratio
# AH Premium = (A_close_in_HKD / HK_close - 1) * 100
# A_close_in_HKD = A_close / HKD_CNY_rate
# Or equivalently: Premium = (A_close / rate / HK_close - 1) * 100

premium_data = []
rate_hkd_cny = 0.91  # approximate 1 HKD = 0.91 CNY

for date in overlap_dates:
    a = a_map[date]
    hk = hk_map[date]
    # A股价格是CNY, 港股价格是HKD
    # 把A股价格换算成HKD: a_close_HKD = a_close / rate_hkd_cny
    # AH溢价率 = (a_close / rate / hk_close - 1) * 100
    a_close_hkd = a['close'] / rate_hkd_cny
    premium_pct = (a_close_hkd / hk['close'] - 1) * 100
    premium_data.append({
        'date': date,
        'a_close_cny': a['close'],
        'hk_close_hkd': hk['close'],
        'a_close_hkd': round(a_close_hkd, 2),
        'premium_pct': round(premium_pct, 2),
        'a_pct_chg': a['pct_chg'],
        'hk_pct_chg': hk['pct_chg'],
        'a_vol': a['vol'],
        'hk_vol': hk['vol'],
    })

# Update the comparison JSON with premium data
comparison['premium'] = premium_data
comparison['rate_hkd_cny'] = rate_hkd_cny
comparison['overlap_count'] = len(overlap_dates)
comparison['overlap_range'] = f"{overlap_dates[0]} ~ {overlap_dates[-1]}" if overlap_dates else "N/A"

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'w', encoding='utf-8') as f:
    json.dump(comparison, f, ensure_ascii=False)

print(f"\nPremium data computed and saved. {len(premium_data)} overlapping records.")
if premium_data:
    print(f"Premium range: {min(d['premium_pct'] for d in premium_data):.2f}% ~ {max(d['premium_pct'] for d in premium_data):.2f}%")
    print(f"Latest premium: {premium_data[-1]['premium_pct']}%")
