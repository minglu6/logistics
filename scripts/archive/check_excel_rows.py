# -*- coding: utf-8 -*-
import pandas as pd
df = pd.read_excel('data/jiangxi/summary/惠宜选江西仓1月份对账单.xlsx', header=None)
print('总行数:', len(df))
print('\n检查第25-60行的店名列:')
for i in range(24, min(60, len(df))):
    store_name = df.iloc[i, 2]
    if pd.notna(store_name) and str(store_name).strip():
        stops = str(store_name).split('\n')
        print(f'行{i+1}: {len(stops)}个站点 - {stops[0][:40]}...')
    else:
        km = df.iloc[i, 4]
        if pd.notna(km):
            print(f'行{i+1}: 无店名, 公里数={km}')
