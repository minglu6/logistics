import pandas as pd
import openpyxl

# 读取临努1.1.xlsx
source_file = r'D:\Work\logistics\临努1.1.xlsx'
df_source = pd.read_excel(source_file, header=None)

print("临努1.1.xlsx 数据预览：")
print(df_source.head(50))
print("\n数据形状：", df_source.shape)
print("\n" + "="*50)

# 读取惠宜选合肥仓1月份对账单.xlsx
target_file = r'D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx'
df_target = pd.read_excel(target_file, header=None)

print("\n惠宜选合肥仓1月份对账单.xlsx 数据预览：")
print(df_target.head(30))
print("\n数据形状：", df_target.shape)
