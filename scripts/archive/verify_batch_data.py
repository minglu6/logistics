import pandas as pd
from datetime import datetime

# 读取填充后的文件
target_file = r'D:\Work\logistics\惠宜选合肥仓1月份对账单.xlsx'
df = pd.read_excel(target_file, header=None)

# Excel日期序列号到日期的映射
date_map = {
    46023: '1月1日',
    46024: '1月2日',
    46025: '1月3日',
    46026: '1月4日',
    46027: '1月5日',
    46028: '1月6日',
    46030: '1月8日'
}

print("数据填充验证报告")
print("="*100)

# 统计每天的车次数
date_stats = {}
for i in range(1, 32):  # 检查前31行
    row = df.iloc[i]
    if pd.notna(row[1]) and isinstance(row[1], (int, float)):
        date_serial = int(row[1])
        if date_serial in date_map:
            date_label = date_map[date_serial]
            if date_label not in date_stats:
                date_stats[date_label] = []

            # 统计店名数量
            if pd.notna(row[2]):
                shops = str(row[2]).split('\n')
                date_stats[date_label].append({
                    '行号': i + 1,
                    '序号': row[0],
                    '店数': len(shops),
                    '店名': shops
                })

# 打印统计结果
print("\n各日期数据汇总：")
print("-"*100)
for date in ['1月1日', '1月2日', '1月3日', '1月4日', '1月5日', '1月6日', '1月8日']:
    if date in date_stats:
        vehicles = date_stats[date]
        print(f"\n{date}：{len(vehicles)} 车")
        total_shops = sum(v['店数'] for v in vehicles)
        print(f"  总店数: {total_shops}")
        for v in vehicles:
            print(f"    第{v['序号']}车 (行{v['行号']}): {v['店数']}个店")
            for shop in v['店名'][:3]:  # 只显示前3个店名
                print(f"      - {shop}")
            if v['店数'] > 3:
                print(f"      ... 还有{v['店数'] - 3}个店")

print("\n" + "="*100)
print(f"\n总计：")
total_vehicles = sum(len(vehicles) for vehicles in date_stats.values())
total_shops = sum(sum(v['店数'] for v in vehicles) for vehicles in date_stats.values())
print(f"  处理日期数: {len(date_stats)}")
print(f"  总车次数: {total_vehicles}")
print(f"  总店铺数: {total_shops}")
