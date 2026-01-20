# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('data/jiangxi/summary/惠宜选江西仓1月份对账单.xlsx', header=None)

print('检查有店名内容的行:')
routes_count = 0
for i in range(1, len(df)):
    store_name = df.iloc[i, 2]  # C列
    if pd.notna(store_name) and str(store_name).strip():
        routes_count += 1
        stops = str(store_name).split('\n')
        km = df.iloc[i, 4]  # E列
        print(f'行{i+1}: {len(stops)}个站点, 公里数列={km}')
        for j, s in enumerate(stops[:3]):  # 只显示前3个站点
            print(f'    站点{j+1}: {s[:40]}')
        if len(stops) > 3:
            print(f'    ... 还有{len(stops)-3}个站点')

print(f'\n共有 {routes_count} 条路线')
