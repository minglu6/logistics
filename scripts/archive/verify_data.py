import pandas as pd

# 读取填充后的文件
target_file = r'D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx'
df = pd.read_excel(target_file, header=None)

print("填充后的数据（前8行）：")
print("="*100)
for i in range(8):
    row = df.iloc[i]
    print(f"\n行{i+1}:")
    print(f"  序号: {row[0]}")
    print(f"  日期: {row[1]}")
    if pd.notna(row[2]):
        shops = str(row[2]).split('\n')
        print(f"  店名数量: {len(shops)}")
        print(f"  店名列表:")
        for shop in shops:
            print(f"    - {shop}")
