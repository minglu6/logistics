---
name: fill-distances
description: Fill distance information into billing Excel files using cached reusable distances. Supports both Hefei and Jiangxi warehouses. Automatically detects region and uses appropriate cache.
allowed-tools: Bash(python:*), Bash(source .venv/bin/activate*), Bash(.venv/bin/python:*), Read
---

# Fill Distances to Billing Data

This skill fills distance information into billing Excel files using cached reusable distance data. It supports both Hefei and Jiangxi logistics warehouses and can automatically detect the region from the file path.

## Usage

When the user asks to fill distances, add distance information, or complete billing data with distances:

```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py <excel_file> [distances_json] [region]
```

### Parameters

- `excel_file`: Billing Excel file path (required)
- `distances_json`: Reusable distances JSON file path (optional, defaults to region cache)
- `region`: Region identifier - `hefei` or `jiangxi` (optional, auto-detected from path)

### Auto-Detection

The script automatically detects the region from the file path:
- Paths containing `hefei` or `合肥` → Hefei warehouse
- Paths containing `jiangxi` or `江西` → Jiangxi warehouse

Default cache paths:
- Hefei: `data/hefei/cache/reusable_distances.json`
- Jiangxi: `data/jiangxi/cache/reusable_distances.json`

### Output Format

The script modifies the Excel file in-place, adding distance information to store names:
- Format: `店名-XXkm` (e.g., `惠宜选-合肥庐江店-120km`)
- Unknown distances: `店名-?km`

## How It Works

1. **Load Distance Cache**: Reads reusable distance data from JSON file
2. **Detect Region**: Automatically determines warehouse (Hefei/Jiangxi) from file path
3. **Process Routes**: For each route in the Excel file:
   - Skip rows already containing distance information
   - First stop: Calculate distance from warehouse to first store
   - Subsequent stops: Calculate distance from previous store to current store
4. **Format & Save**: Appends `-XXkm` to each store name and saves back to Excel

### Distance Matching

The script uses intelligent matching:
- **Exact matching**: Tries exact store name matches
- **Bracket normalization**: Handles `（）` vs `()` differences
- **Fuzzy matching**: Uses aggressive normalization for common variations
- **Bidirectional search**: Searches both directions (A→B and B→A)

## Examples

### Example 1: Hefei - Auto-detect with default cache

```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  data/hefei/summary/2026/惠宜选合肥仓1月份对账单0119.xlsx
```

This will:
- Auto-detect region as `hefei`
- Use default cache: `data/hefei/cache/reusable_distances.json`
- Fill distances starting from: `丰树合肥现代综合产业园`

### Example 2: Jiangxi - Auto-detect with default cache

```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  data/jiangxi/summary/2026/江西对账单0113.xlsx
```

This will:
- Auto-detect region as `jiangxi`
- Use default cache: `data/jiangxi/cache/reusable_distances.json`
- Fill distances from Jiangxi warehouse start point

### Example 3: Custom distance JSON

```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  data/hefei/summary/2026/惠宜选合肥仓1月份对账单0119.xlsx \
  data/hefei/cache/custom_distances.json
```

### Example 4: Manual region specification

```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  /tmp/对账单.xlsx \
  data/hefei/cache/reusable_distances.json \
  hefei
```

## Output Example

Before:
```
厉臣便利（邳州青年路店）
帮帮团（邳州长江路店）
惠宜选-徐州新沂店
共橙超市-徐州新沂2店
```

After:
```
厉臣便利（邳州青年路店）-340km
帮帮团（邳州长江路店）-5km
惠宜选-徐州新沂店-41km
共橙超市-徐州新沂2店-3km
```

## Statistics Reported

The script reports:
- Total routes processed
- Total stops processed
- Distances found (count and percentage)
- Distances not found (count and percentage)
- Details of missing distances (up to 20 entries)

## Important Notes

- **In-place modification**: The Excel file is modified directly
- **Idempotent**: Rows already containing distance info (e.g., `-XXkm`) are skipped
- **Smart matching**: Handles common name variations automatically
- **Region-aware**: Uses correct warehouse start point for each region
- **Cache-based**: Relies on pre-computed reusable distances for efficiency

## Warehouse Start Points

- **Hefei**: 丰树合肥现代综合产业园
- **Jiangxi**: 南昌红谷滩区 (adjust as needed)

## Excel Structure Expected

- Column C (column 3): Store names with newlines separating stops
- Row 2+: Data rows (row 1 is header)

## Error Handling

- Validates file existence
- Auto-detects region or accepts manual override
- Reports missing distances as `-?km` for manual correction
- Skips rows already processed
