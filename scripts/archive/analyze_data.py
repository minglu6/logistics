import pandas as pd
import numpy as np

# 读取目标文件
target_file = r'D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx'
df_target = pd.read_excel(target_file, header=None)

print("目标文件完整列结构：")
print(df_target.iloc[0])  # 表头
print("\n示例数据（前几行）：")
print(df_target.iloc[0:5])

print("\n" + "="*80)

# 读取源文件
source_file = r'D:\Work\logistics\临努1.1.xlsx'
df_source = pd.read_excel(source_file, header=None)

# 分析源文件中的车次（通过空行分隔）
print("\n源文件完整数据：")
for idx, row in df_source.iterrows():
    if pd.isna(row[0]):
        print(f"行{idx}: [空行]")
    else:
        print(f"行{idx}: {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
