import json

with open('/Users/daydayup/Desktop/Agent/澜起科技_AH对比_图表数据.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

a_dates = [d['date'] for d in data['a_share']]
hk_dates = [d['date'] for d in data['hk_share']]
premium_dates = [d['date'] for d in data['premium']]

print(f"A-share dates: {len(a_dates)}, range: {a_dates[0]} ~ {a_dates[-1]}")
print(f"HK dates: {len(hk_dates)}, range: {hk_dates[0]} ~ {hk_dates[-1]}")
print(f"Premium dates: {len(premium_dates)}, range: {premium_dates[0]} ~ {premium_dates[-1]}")

# Check if there are gaps in HK data
a_set = set(a_dates)
hk_set = set(hk_dates)
overlap = sorted(a_set & hk_set)
print(f"Overlap between A and HK dates: {len(overlap)}")

# Check HK dates that are NOT in A dates (HK holidays differ from A holidays)
hk_only = sorted(hk_set - a_set)
print(f"HK-only dates (not in A): {len(hk_only)}")
if hk_only:
    print(f"  First few: {hk_only[:10]}")
    print(f"  Last few: {hk_only[-10:]}")

# Check A dates in HK range that are NOT in HK dates
hk_start = hk_dates[0]
hk_end = hk_dates[-1]
a_in_range = [d for d in a_dates if d >= hk_start and d <= hk_end]
a_not_in_hk = [d for d in a_in_range if d not in hk_set]
print(f"A dates in HK range: {len(a_in_range)}")
print(f"A dates NOT in HK (within HK range): {len(a_not_in_hk)}")
if a_not_in_hk:
    print(f"  First few: {a_not_in_hk[:10]}")
    print(f"  Last few: {a_not_in_hk[-10:]}")

# Check last 10 premium entries
print("\nLast 10 premium entries:")
for p in data['premium'][-10:]:
    print(f"  {p['date']}: premium={p['premium_pct']}%, a_close={p['a_close_cny']}, hk_close={p['hk_close_hkd']}")

# Check last 20 HK dates
print("\nLast 20 HK dates and close:")
for d in data['hk_share'][-20:]:
    print(f"  {d['date']}: close={d['close']}, vol={d['vol']}")

# Check last 20 A dates
print("\nLast 20 A dates and close:")
for d in data['a_share'][-20:]:
    print(f"  {d['date']}: close={d['close']}, vol={d['vol']}")
