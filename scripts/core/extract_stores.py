#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从物流Excel文件中提取店名数据
支持合肥和江西两个区域

用法:
    python -m scripts.core.extract_stores --region hefei --dates 1.9-1.12 --input-dir data/hefei/details
    python -m scripts.core.extract_stores --region hefei --files "临努1.13.xlsx,临努1.15.xlsx"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.common import extract_stores_from_excel, get_region_config


def parse_date_range(date_range):
    """
    解析日期范围字符串

    Args:
        date_range: 如 "1.9-1.12" 或 "1.13,1.15,1.16"

    Returns:
        日期列表 ["1.9", "1.10", "1.11", "1.12"]
    """
    dates = []
    if '-' in date_range and ',' not in date_range:
        # 范围格式: 1.9-1.12
        start, end = date_range.split('-')
        start_parts = start.split('.')
        end_parts = end.split('.')
        month = int(start_parts[0])
        start_day = int(start_parts[1])
        end_day = int(end_parts[1])
        for day in range(start_day, end_day + 1):
            dates.append(f"{month}.{day}")
    else:
        # 逗号分隔: 1.13,1.15,1.16
        dates = [d.strip() for d in date_range.split(',')]
    return dates


def extract_stores(region, input_dir, dates, output_file, file_pattern="临努{date}.xlsx", store_column=4):
    """
    从Excel文件中提取店名数据

    Args:
        region: 区域
        input_dir: 输入目录
        dates: 日期列表
        output_file: 输出文件路径
        file_pattern: 文件名模式，{date}会被替换为日期
        store_column: 店名所在列
    """
    print("=" * 60)
    print(f"提取{region.upper()}物流店名数据")
    print("=" * 60)

    all_data = {}

    for date_str in dates:
        file_name = file_pattern.format(date=date_str)
        file_path = os.path.join(input_dir, file_name)

        if not os.path.exists(file_path):
            print(f"\n警告: 文件不存在 - {file_path}")
            continue

        print(f"\n处理 {date_str}: {file_path}")
        vehicles = extract_stores_from_excel(file_path, store_column)
        all_data[date_str] = vehicles
        print(f"  提取到 {len(vehicles)} 辆车")
        for i, vehicle in enumerate(vehicles, 1):
            if vehicle:
                print(f"    第{i}车: {len(vehicle)}个店铺, 首店: {vehicle[0][:30]}...")

    # 写入输出文件
    print(f"\n写入输出文件: {output_file}")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for date_str in dates:
            if date_str not in all_data:
                continue

            # 写入日期标题
            f.write(f"{date_str}\n")
            f.write("\n")

            # 写入该日期的所有车辆
            vehicles = all_data[date_str]
            for vehicle_stores in vehicles:
                for store in vehicle_stores:
                    f.write(f"{store}\n")
                f.write("\n")  # 车辆之间用空行分隔

    total_vehicles = sum(len(v) for v in all_data.values())
    total_stores = sum(sum(len(stores) for stores in v) for v in all_data.values())

    print("=" * 60)
    print("提取完成!")
    print(f"  处理日期: {len(all_data)} 天")
    print(f"  总车次: {total_vehicles}")
    print(f"  总店铺: {total_stores}")
    print(f"输出文件: {output_file}")
    print("=" * 60)

    return all_data


def main():
    parser = argparse.ArgumentParser(description='从物流Excel文件提取店名数据')
    parser.add_argument('--region', '-r', required=True, choices=['hefei', 'jiangxi'],
                        help='区域: hefei 或 jiangxi')
    parser.add_argument('--dates', '-d',
                        help='日期范围，如 "1.9-1.12" 或 "1.13,1.15,1.16"')
    parser.add_argument('--input-dir', '-i',
                        help='输入目录路径')
    parser.add_argument('--output', '-o',
                        help='输出txt文件路径')
    parser.add_argument('--pattern', '-p', default='临努{date}.xlsx',
                        help='文件名模式，默认 "临努{date}.xlsx"')
    parser.add_argument('--column', '-c', type=int, default=4,
                        help='店名所在列，默认4')

    args = parser.parse_args()

    config = get_region_config(args.region)

    # 设置默认值
    input_dir = args.input_dir or config['details_dir']
    output_file = args.output or os.path.join(input_dir, f'物流店名数据_{args.dates}.txt')

    if not args.dates:
        parser.error("--dates 参数是必需的")

    dates = parse_date_range(args.dates)
    extract_stores(args.region, input_dir, dates, output_file, args.pattern, args.column)


if __name__ == '__main__':
    main()
