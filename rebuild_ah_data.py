import tushare as ts
import pandas as pd
import json
from datetime import datetime, timedelta

ts.set_token('f67c3daa067442fd4f79989f010d9ea2f40b0c3aa3ea0128600cd647')
pro = ts.pro_api()

end_date = datetime.now().strftime('%Y%m%d')
start_date_1y = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
hk_start = '20260209'  # HK IPO date

print("=== Re-fetching A-share data ===")
df_a = pro.daily(ts_code='688008.SH', start_date=start_date_1y, end_date=end_date)
df_a = df_a.sort_values('trade_date', ascending=True).reset_index(drop=True)
print(f"A: {len(df_a)} records, {df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}")

print("=== Re-fetching HK data ===")
df_hk = pro.hk_daily(ts_code='06809.HK', start_date=hk_start, end_date=end_date)
df_hk = df_hk.sort_values('trade_date', ascending=True).reset_index(drop=True)
print(f"HK: {len(df_hk)} records, {df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}")

# Save CSVs
df_a.to_csv('/Users/daydayup/Desktop/Agent/澜起科技_A股_交易数据.csv', index=False)
df_hk.to_csv('/Users/daydayup/Desktop/Agent/澜起科技_港股_交易数据.csv', index=False)

# Build date-indexed dictionaries for lookups
a_dict = {}
for _, row in df_a.iterrows():
    a_dict[row['trade_date']] = {
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    }

hk_dict = {}
for _, row in df_hk.iterrows():
    hk_dict[row['trade_date']] = {
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    }

# Build UNION of all dates in the HK trading range
# For each date, if one market is closed, use the last available close
all_dates_in_range = sorted(set(list(a_dict.keys()) + list(hk_dict.keys())))
all_dates_in_range = [d for d in all_dates_in_range if d >= hk_start]

print(f"\nAll dates in HK range (union): {len(all_dates_in_range)}")

# For dates where one market is closed, carry forward the last close
last_a_close = None
last_hk_close = None

# First, find the A close right before HK IPO
for d in sorted(a_dict.keys()):
    if d < hk_start:
        last_a_close = a_dict[d]['close']
    else:
        break

rate_hkd_cny = 0.91  # 1 HKD ≈ 0.91 CNY

premium_full = []
a_close_series = []  # For comparison chart
hk_close_cny_series = []  # HK close converted to CNY, for comparison chart
compare_dates = []

for date in all_dates_in_range:
    # Get A close (actual or carry-forward)
    if date in a_dict:
        a_close = a_dict[date]['close']
        last_a_close = a_close
        a_has_data = True
    else:
        a_close = last_a_close  # carry forward
        a_has_data = False

    # Get HK close (actual or carry-forward)
    if date in hk_dict:
        hk_close = hk_dict[date]['close']
        last_hk_close = hk_close
        hk_has_data = True
    else:
        hk_close = last_hk_close  # carry forward
        hk_has_data = False

    # Compute premium only when both have valid prices
    if a_close is not None and hk_close is not None:
        a_close_hkd = a_close / rate_hkd_cny
        premium_pct = (a_close_hkd / hk_close - 1) * 100
        premium_full.append({
            'date': date,
            'a_close_cny': round(a_close, 2),
            'hk_close_hkd': round(hk_close, 2),
            'a_close_hkd': round(a_close_hkd, 2),
            'hk_close_cny': round(hk_close * rate_hkd_cny, 2),
            'premium_pct': round(premium_pct, 2),
            'a_actual': a_has_data,
            'hk_actual': hk_has_data,
        })

    # For comparison chart: use union dates, with nulls for missing
    compare_dates.append(date)
    a_close_series.append(a_dict.get(date, {}).get('close') if date in a_dict else None)
    hk_close_cny_series.append(hk_dict.get(date, {}).get('close') * rate_hkd_cny if date in hk_dict else None)

print(f"Premium data points: {len(premium_full)}")
print(f"Premium range: {premium_full[0]['date']} ~ {premium_full[-1]['date']}")
print(f"Premium value range: {min(p['premium_pct'] for p in premium_full)}% ~ {max(p['premium_pct'] for p in premium_full)}%")
print(f"Latest premium: {premium_full[-1]['premium_pct']}%")

# Also prepare overlap-only premium for accuracy
overlap_dates = sorted(set(d for d in a_dict.keys() if d in hk_dict and d >= hk_start))
premium_overlap = []
for date in overlap_dates:
    a = a_dict[date]
    hk = hk_dict[date]
    a_close_hkd = a['close'] / rate_hkd_cny
    premium_pct = (a_close_hkd / hk['close'] - 1) * 100
    premium_overlap.append({
        'date': date,
        'a_close_cny': round(a['close'], 2),
        'hk_close_hkd': round(hk['close'], 2),
        'premium_pct': round(premium_pct, 2),
        'a_pct_chg': a['pct_chg'],
        'hk_pct_chg': hk['pct_chg'],
        'a_vol': a['vol'],
        'hk_vol': hk['vol'],
    })

print(f"Overlap-only premium points: {len(premium_overlap)}")

# Build final comparison data structure
a_chart_data = []
for _, row in df_a.iterrows():
    a_chart_data.append({
        'date': row['trade_date'],
        'label': 'A',
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    })

hk_chart_data = []
for _, row in df_hk.iterrows():
    hk_chart_data.append({
        'date': row['trade_date'],
        'label': 'HK',
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    })

comparison_data = {
    'a_share': a_chart_data,
    'hk_share': hk_chart_data,
    'premium': premium_overlap,
    'premium_full': premium_full,
    'compare_dates': compare_dates,
    'a_close_series': a_close_series,
    'hk_close_cny_series': hk_close_cny_series,
    'a_stock_code': '688008.SH',
    'hk_stock_code': '06809.HK',
    'a_range': f"{df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}",
    'hk_range': f"{df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}",
    'a_count': len(df_a),
    'hk_count': len(df_hk),
    'rate_hkd_cny': rate_hkd_cny,
    'overlap_count': len(overlap_dates),
    'overlap_range': f"{overlap_dates[0]} ~ {overlap_dates[-1]}" if overlap_dates else "N/A",
}

json_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(comparison_data, f, ensure_ascii=False)

print(f"\nUpdated JSON saved to {json_path}")
