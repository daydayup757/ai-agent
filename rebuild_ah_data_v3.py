import pandas as pd
import json
from datetime import datetime

# Read existing CSV data (no need to re-fetch from Tushare)
df_a = pd.read_csv('/Users/daydayup/Desktop/Agent/澜起科技_A股_交易数据.csv')
df_hk = pd.read_csv('/Users/daydayup/Desktop/Agent/澜起科技_港股_交易数据.csv')

df_a = df_a.sort_values('trade_date', ascending=True).reset_index(drop=True)
df_hk = df_hk.sort_values('trade_date', ascending=True).reset_index(drop=True)

print(f"A: {len(df_a)} records, {df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}")
print(f"HK: {len(df_hk)} records, {df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}")

# Unit conversions:
# A股: vol=手(1手=100股), amount=千元(CNY)
# 港股: vol=股, amount=港元(HKD)
RATE_HKD_CNY = 0.91

def a_vol_to_wan(vol):
    """A股 vol(手) → 万股: 1手=100股=0.01万股, so vol/100"""
    return round(vol / 100, 2)

def hk_vol_to_wan(vol):
    """港股 vol(股) → 万股: 1万股=10000股, so vol/10000"""
    return round(vol / 10000, 2)

def a_amount_to_wan_cny(amount):
    """A股 amount(千元CNY) → 万元CNY: amount/10"""
    return round(amount / 10, 2)

def hk_amount_to_wan_cny(amount):
    """港股 amount(港元HKD) → 万元CNY: amount*rate/10000"""
    return round(amount * RATE_HKD_CNY / 10000, 2)

# Build date-indexed dictionaries
a_dict = {}
for _, row in df_a.iterrows():
    a_dict[str(row['trade_date'])] = {
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
    hk_dict[str(row['trade_date'])] = {
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    }

hk_start = '20260209'

# Carry-forward logic for premium full
all_dates_in_range = sorted(set(list(a_dict.keys()) + list(hk_dict.keys())))
all_dates_in_range = [d for d in all_dates_in_range if d >= hk_start]

last_a_close = None
for d in sorted(a_dict.keys()):
    if d < hk_start:
        last_a_close = a_dict[d]['close']
    else:
        break

last_hk_close = None

premium_full = []
for date in all_dates_in_range:
    if date in a_dict:
        a_close = a_dict[date]['close']
        last_a_close = a_close
        a_actual = True
    else:
        a_close = last_a_close
        a_actual = False

    if date in hk_dict:
        hk_close = hk_dict[date]['close']
        last_hk_close = hk_close
        hk_actual = True
    else:
        hk_close = last_hk_close
        hk_actual = False

    if a_close is not None and hk_close is not None:
        a_close_hkd = a_close / RATE_HKD_CNY
        premium_pct = (a_close_hkd / hk_close - 1) * 100
        premium_full.append({
            'date': date,
            'a_close_cny': round(a_close, 2),
            'hk_close_hkd': round(hk_close, 2),
            'a_close_hkd': round(a_close_hkd, 2),
            'hk_close_cny': round(hk_close * RATE_HKD_CNY, 2),
            'premium_pct': round(premium_pct, 2),
            'a_actual': a_actual,
            'hk_actual': hk_actual,
        })

# Overlap-only premium for vol/amount/pct comparison charts
overlap_dates = sorted(set(d for d in a_dict.keys() if d in hk_dict and d >= hk_start))
premium_overlap = []
for date in overlap_dates:
    a = a_dict[date]
    hk = hk_dict[date]
    a_close_hkd = a['close'] / RATE_HKD_CNY
    premium_pct = (a_close_hkd / hk['close'] - 1) * 100
    premium_overlap.append({
        'date': date,
        'a_close_cny': round(a['close'], 2),
        'hk_close_hkd': round(hk['close'], 2),
        'premium_pct': round(premium_pct, 2),
        'a_pct_chg': round(a['pct_chg'], 2),
        'hk_pct_chg': round(hk['pct_chg'], 2),
        # Volume in 万股 (same unit for both)
        'a_vol_wan': a_vol_to_wan(a['vol']),
        'hk_vol_wan': hk_vol_to_wan(hk['vol']),
        # Amount in 万元CNY (same unit for both)
        'a_amount_wan_cny': a_amount_to_wan_cny(a['amount']),
        'hk_amount_wan_cny': hk_amount_to_wan_cny(hk['amount']),
    })

# Chart data for K-line charts (keep original vol for individual K-line vol bars)
a_chart_data = []
for _, row in df_a.iterrows():
    a_chart_data.append({
        'date': str(row['trade_date']),
        'label': 'A',
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),  # 手, used in individual K-line volume bar
        'vol_wan': a_vol_to_wan(float(row['vol'])),  # 万股, for unit label
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    })

hk_chart_data = []
for _, row in df_hk.iterrows():
    hk_chart_data.append({
        'date': str(row['trade_date']),
        'label': 'HK',
        'open': float(row['open']),
        'close': float(row['close']),
        'low': float(row['low']),
        'high': float(row['high']),
        'vol': float(row['vol']),  # 股, used in individual K-line volume bar
        'vol_wan': hk_vol_to_wan(float(row['vol'])),  # 万股, for unit label
        'amount': float(row['amount']),
        'pre_close': float(row['pre_close']),
        'pct_chg': float(row['pct_chg']),
    })

comparison_data = {
    'a_share': a_chart_data,
    'hk_share': hk_chart_data,
    'premium': premium_overlap,
    'premium_full': premium_full,
    'a_stock_code': '688008.SH',
    'hk_stock_code': '06809.HK',
    'a_range': f"{df_a['trade_date'].iloc[0]} ~ {df_a['trade_date'].iloc[-1]}",
    'hk_range': f"{df_hk['trade_date'].iloc[0]} ~ {df_hk['trade_date'].iloc[-1]}",
    'a_count': len(df_a),
    'hk_count': len(df_hk),
    'rate_hkd_cny': RATE_HKD_CNY,
    'overlap_count': len(overlap_dates),
    'overlap_range': f"{overlap_dates[0]} ~ {overlap_dates[-1]}" if overlap_dates else "N/A",
}

json_path = '/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(comparison_data, f, ensure_ascii=False)

print(f"\nUpdated JSON saved to {json_path}")
print(f"premium_full: {len(premium_full)} points")
print(f"premium_overlap: {len(premium_overlap)} points")
print(f"\nSample overlap data (vol & amount in same units):")
p = premium_overlap[0]
print(f"  Date: {p['date']}")
print(f"  A股成交量: {p['a_vol_wan']} 万股, 成交额: {p['a_amount_wan_cny']} 万元CNY")
print(f"  港股成交量: {p['hk_vol_wan']} 万股, 成交额: {p['hk_amount_wan_cny']} 万元CNY")
