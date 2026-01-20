---
name: update-distance-cache
description: Extract distance data from billing Excel files and update the regional distance cache (Hefei or Jiangxi). Automatically detects region and updates the appropriate cache file.
allowed-tools: Bash(python:*), Bash(source .venv/bin/activate*), Bash(.venv/bin/python:*), Read
---

# Update Distance Cache

This skill extracts distance information from billing Excel files (that already contain distance data) and updates the regional distance cache. It supports both Hefei and Jiangxi warehouses and automatically detects the region from the file path.

## Usage

When the user asks to update the distance cache or add distances from a billing file to the cache:

```bash
.venv/bin/python .claude/skills/update-distance-cache/scripts/update_cache.py <excel_file> [region]
```

### Parameters

- `excel_file`: Billing Excel file with distance information (required)
- `region`: Region identifier - `hefei` or `jiangxi` (optional, auto-detected from path)

### Auto-Detection

The script automatically detects the region from the file path:
- Paths containing `hefei` or `合肥` → Updates `data/hefei/cache/reusable_distances.json`
- Paths containing `jiangxi` or `江西` → Updates `data/jiangxi/cache/reusable_distances.json`

## How It Works

1. **Load Existing Cache**: Reads the current regional distance cache
2. **Detect Region**: Automatically determines warehouse from file path
3. **Extract Distances**: Parses all routes in the Excel file to extract distance pairs
4. **Identify New Data**: Compares extracted distances with existing cache
5. **Update Cache**: Adds only new distance pairs to the cache
6. **Report**: Shows statistics and details of added distances

### Distance Extraction

The script extracts distances from store name format:
- Format: `店名-XXkm` (e.g., `惠宜选-合肥庐江店-120km`)
- Creates pairs: `店A -> 店B: distance`
- Includes warehouse-to-first-store distances

### Conflict Handling

If a distance pair exists in cache with a different value:
- **Preserves** the existing cache value
- **Reports** the conflict
- User can manually update if needed

## Examples

### Example 1: Hefei - Auto-detect and update

```bash
.venv/bin/python .claude/skills/update-distance-cache/scripts/update_cache.py \
  data/hefei/summary/2026/惠宜选合肥仓1月份对账单0119.xlsx
```

This will:
- Auto-detect region as `hefei`
- Extract all distances from the billing file
- Add new distances to `data/hefei/cache/reusable_distances.json`
- Report how many distances were added

### Example 2: Jiangxi - Auto-detect

```bash
.venv/bin/python .claude/skills/update-distance-cache/scripts/update_cache.py \
  data/jiangxi/summary/2026/江西对账单0113.xlsx
```

### Example 3: Manual region specification

```bash
.venv/bin/python .claude/skills/update-distance-cache/scripts/update_cache.py \
  /tmp/对账单.xlsx \
  hefei
```

## Output Example

```
======================================================================
距离缓存更新工具
======================================================================

区域: HEFEI
起点: 丰树合肥现代综合产业园
Excel文件: data/hefei/summary/2026/惠宜选合肥仓1月份对账单0119.xlsx
缓存文件: data/hefei/cache/reusable_distances.json

读取现有缓存...
当前缓存中有 430 条距离记录

从Excel提取距离数据...
从 42 条路线中提取到 245 条距离配对

======================================================================
分析结果:
  Excel中的距离配对: 245
  缓存中已存在: 243
  需要新增: 2
  需要更新: 0

新增的距离数据:
----------------------------------------------------------------------
  "共橙一站式超市（枞阳渡江路店） -> 共橙一站式超市（池州双溪路店）": 40.0
  "厉臣便利（舒城杭埠镇店） -> 共橙一站式超市（铜陵北湖街店）": 127.0

======================================================================
缓存更新完成!
  原有记录: 430
  新增记录: 2
  更新后总数: 432
  缓存文件: data/hefei/cache/reusable_distances.json
======================================================================
```

## Use Cases

### Use Case 1: After Manual Distance Correction

When you manually correct unknown distances (marked as `-?km`) in a billing file, use this skill to add those corrected distances to the cache:

1. Fill billing with distances (some may be `-?km`)
2. Manually correct the `-?km` entries in Excel
3. Run this skill to extract and cache the corrected distances
4. Future billing files will now have these distances

### Use Case 2: Building Initial Cache

When starting with a new region or rebuilding cache:

1. Create a billing file with all distances filled
2. Run this skill to extract all distances
3. Creates/updates the regional cache file

### Use Case 3: Regular Cache Maintenance

After processing each billing period:

1. Process and fill distances in billing file
2. Run this skill to add any new routes to cache
3. Keeps cache growing with new store combinations

## Important Notes

- **Requires Distance Data**: Excel file must already contain distance information (format: `店名-XXkm`)
- **Non-Destructive**: Only adds new distances, never removes or overwrites existing ones
- **Conflict Resolution**: If distance values differ, preserves existing cache value
- **Auto-Creates**: If cache file doesn't exist, creates it automatically
- **Idempotent**: Can run multiple times safely on the same file

## Regional Cache Paths

- **Hefei**: `data/hefei/cache/reusable_distances.json`
- **Jiangxi**: `data/jiangxi/cache/reusable_distances.json`

## Warehouse Start Points

- **Hefei**: 丰树合肥现代综合产业园
- **Jiangxi**: 南昌红谷滩区

## Expected Excel Structure

- Column C (column 3): Store names with distances in format `店名-XXkm`
- Stores separated by newlines within cells
- Row 2+: Data rows (row 1 is header)

## Statistics Reported

- Total distance pairs extracted from Excel
- How many already exist in cache
- How many new pairs will be added
- How many conflicts detected (different values)
- Details of new distances (up to 20 entries shown)
