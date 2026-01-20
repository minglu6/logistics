#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从对账单Excel中提取距离数据并更新缓存
支持合肥和江西两个区域

用法:
    python -m scripts.core.extract_distances --region hefei --input 对账单0112.xlsx
    python -m scripts.core.extract_distances --region jiangxi --input 对账单0113.xlsx
"""

import argparse
import json
import os
import sys
from collections import defaultdict

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.common import (
    get_region_config, extract_routes_from_excel, build_segments,
    load_distance_cache, save_distance_cache, CONFLICT_THRESHOLD
)


def extract_and_update_cache(region, input_file, source_name=None):
    """
    从Excel提取距离并更新缓存

    Args:
        region: 区域 ('hefei' 或 'jiangxi')
        input_file: 输入Excel文件路径
        source_name: 数据来源名称（用于记录）
    """
    config = get_region_config(region)
    start_point = config['start_point']
    cache_file = os.path.join(config['cache_dir'], 'reusable_distances.json')
    large_diff_file = os.path.join(config['cache_dir'], 'large_distance_differences.json')

    if source_name is None:
        source_name = os.path.basename(input_file)

    print("=" * 80)
    print(f"从{region.upper()}对账单提取距离数据并更新缓存")
    print("=" * 80)

    # 读取现有缓存
    print(f"\n读取现有缓存: {cache_file}")
    existing_distances = load_distance_cache(cache_file)
    print(f"  现有缓存包含 {len(existing_distances)} 个路段")

    # 提取新数据
    print(f"\n处理Excel文件: {input_file}")
    routes = extract_routes_from_excel(input_file, start_point)
    print(f"  提取到 {len(routes)} 条路线")

    # 构建新数据的距离字典（每个路段取平均值）
    new_distance_map = defaultdict(list)
    for route in routes:
        segments = build_segments(route, start_point)
        for seg in segments:
            key = (seg[0], seg[1])
            distance = seg[2]
            if distance is not None:
                new_distance_map[key].append(distance)

    # 计算平均距离
    new_avg_distances = {}
    for key, distances in new_distance_map.items():
        avg_distance = sum(distances) / len(distances)
        new_avg_distances[key] = round(avg_distance, 2)

    print(f"  新数据包含 {len(new_avg_distances)} 个路段")

    # 合并数据
    conflicts = []
    large_differences = []
    new_additions = 0
    updates = 0

    for key, new_distance in new_avg_distances.items():
        segment_key = f"{key[0]} -> {key[1]}"

        if segment_key in existing_distances:
            old_distance = existing_distances[segment_key]
            diff = abs(new_distance - old_distance)

            if diff <= CONFLICT_THRESHOLD:
                if diff > 0.1:
                    conflicts.append({
                        'segment': segment_key,
                        'old_distance': old_distance,
                        'new_distance': new_distance,
                        'difference': diff
                    })
                existing_distances[segment_key] = new_distance
                updates += 1
            else:
                large_differences.append({
                    'segment': segment_key,
                    'old_distance': old_distance,
                    'new_distance': new_distance,
                    'difference': diff,
                    'used_distance': old_distance
                })
        else:
            existing_distances[segment_key] = new_distance
            new_additions += 1

    # 保存更新后的缓存
    save_distance_cache(cache_file, existing_distances)

    print(f"\n✓ 缓存已更新: {cache_file}")
    print(f"  总路段数: {len(existing_distances)}")
    print(f"  新增路段: {new_additions}")
    print(f"  更新路段: {updates}")

    # 保存大差异数据
    if large_differences:
        existing_large_diffs = []
        try:
            with open(large_diff_file, 'r', encoding='utf-8') as f:
                existing_large_diffs = json.load(f)
        except FileNotFoundError:
            pass

        for d in large_differences:
            existing_large_diffs.append({
                'segment': d['segment'],
                'old_distance_km': d['old_distance'],
                'new_distance_km': d['new_distance'],
                'difference_km': round(d['difference'], 2),
                'used_distance_km': d['used_distance'],
                'source': source_name,
                'warning': '距离差异超过5km，已保留旧数据，请人工检查'
            })

        with open(large_diff_file, 'w', encoding='utf-8') as f:
            json.dump(existing_large_diffs, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 大差异数据已保存: {large_diff_file}")
        print(f"  包含 {len(existing_large_diffs)} 个需要检查的路段")

    # 冲突报告
    if conflicts:
        print("\n" + "=" * 80)
        print(f"发现 {len(conflicts)} 个冲突路段（距离相差5km内，已使用新数据）")
        print("=" * 80)
        for c in conflicts[:10]:
            print(f"\n路段: {c['segment']}")
            print(f"  旧数据: {c['old_distance']} km")
            print(f"  新数据: {c['new_distance']} km (已更新)")
            print(f"  差值: {c['difference']:.2f} km")
        if len(conflicts) > 10:
            print(f"\n... 还有 {len(conflicts) - 10} 个冲突路段未显示")

    # 大差异报告
    if large_differences:
        print("\n" + "=" * 80)
        print(f"警告：发现 {len(large_differences)} 个路段距离相差超过5km，已保留旧数据")
        print("=" * 80)
        for d in large_differences[:10]:
            print(f"\n路段: {d['segment']}")
            print(f"  旧数据: {d['old_distance']} km (保留)")
            print(f"  新数据: {d['new_distance']} km")
            print(f"  差值: {d['difference']:.2f} km")
        if len(large_differences) > 10:
            print(f"\n... 还有 {len(large_differences) - 10} 个大差异路段未显示")
        print("\n这些路段已保留旧数据，请人工检查后决定使用哪个数据！")

    print("\n" + "=" * 80)
    print("提取完成！")
    print("=" * 80)

    return {
        'total': len(existing_distances),
        'new': new_additions,
        'updated': updates,
        'large_diff': len(large_differences)
    }


def main():
    parser = argparse.ArgumentParser(description='从对账单提取距离数据并更新缓存')
    parser.add_argument('--region', '-r', required=True, choices=['hefei', 'jiangxi'],
                        help='区域: hefei 或 jiangxi')
    parser.add_argument('--input', '-i', required=True,
                        help='输入Excel文件路径')
    parser.add_argument('--source', '-s',
                        help='数据来源名称（可选）')

    args = parser.parse_args()
    extract_and_update_cache(args.region, args.input, args.source)


if __name__ == '__main__':
    main()
