# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python-based logistics data processing system for managing delivery distance calculations and billing data (对账单) from Hefei (合肥) and Jiangxi (江西) warehouses. Processes Excel billing files, extracts/fills store names and distances, and maintains a JSON distance cache for reuse.

## Tech Stack & Dependencies

- Python 3 with pandas, openpyxl, numpy
- Virtual environment at `.venv/`
- No formal test framework; verification via dedicated scripts

```bash
source .venv/bin/activate
pip install pandas openpyxl numpy
```

## Running Scripts

Core scripts are run as modules from the project root:

```bash
python -m scripts.core.extract_distances --region hefei --input <billing.xlsx>
python -m scripts.core.extract_stores --region hefei --dates 1.9-1.12 --input-dir data/hefei/details
python -m scripts.core.fill_stores --region hefei --input <stores.txt> --excel <billing.xlsx>
python -m scripts.core.fill_distances --region hefei --input <billing.xlsx>
python convert_format.py <source.xlsx>
```

Verification:
```bash
python scripts/verification/verify_billing.py
python scripts/analysis/analyze_excel.py
```

## Architecture

### Data Processing Pipeline

```
Daily logistics files (临努1.x.xlsx)
  -> [extract_stores] -> Structured txt (by date/vehicle)
  -> [fill_stores] -> Billing Excel with store names populated
  -> [fill_distances] -> Billing Excel with distances filled (店名-XXkm format)
  -> Manual verification (check -?km entries)
  -> [extract_distances] -> Updated reusable_distances.json cache
```

### Key Modules

- **scripts/core/** - Four core processing scripts (extract_distances, extract_stores, fill_distances, fill_stores)
- **scripts/utils/common.py** - Shared utilities: region config, store name normalization, distance lookup (exact + fuzzy matching), route parsing, cache I/O
- **scripts/verification/** - Data validation scripts
- **scripts/archive/** - Legacy scripts (do not modify)
- **convert_format.py** - Billing format conversion (临努格式 -> 江西仓对账单模板)

### Data Layout

Each region (hefei/jiangxi) follows the same structure:
- `data/<region>/cache/` - JSON distance cache (`reusable_distances.json`, `large_distance_differences.json`)
- `data/<region>/details/` - Daily input files; `resolved/` for processed ones
- `data/<region>/summary/2026/` - Monthly billing summaries
- `data/<region>/final/` - Final processed output

### Region Configuration (in common.py)

| Region   | Start Point              | Cache Dir            |
|----------|--------------------------|----------------------|
| hefei    | 丰树合肥现代综合产业园      | data/hefei/cache     |
| jiangxi  | 惠宜选南昌仓              | data/jiangxi/cache   |

## Domain Rules

### Distance Calculation
- First stop distance = warehouse start point -> first stop
- Subsequent distances = previous stop -> current stop (NOT from start point)
- Each merged cell in Excel represents one vehicle's complete route
- Distances reusable when start/end points match exactly

### Distance Cache Format
```json
{"起点 -> 终点": distance_km}
```

### Conflict Handling
- Threshold: 5.0 km (CONFLICT_THRESHOLD in common.py)
- Small differences (<=5km): update to new value
- Large differences (>5km): preserve old value, log to `large_distance_differences.json`

### Store Name Matching
`find_distance()` in common.py uses a 4-level matching strategy:
1. Exact match
2. Bracket normalization (（）vs ()）
3. Aggressive normalization (common character substitutions)
4. Fuzzy matching across all cache entries

### Output Format
- Found: `店名-距离km`
- Not found: `店名-?km`
- Address names must be preserved exactly as provided

## Claude Code Skills

Pre-configured skills in `.claude/skills/`:
- **extract-hefei-stores** - Extract store names from Hefei daily files
- **fill-stores** - Fill store names into billing Excel
- **fill-distances** - Fill distances from cache into billing Excel
- **update-distance-cache** - Extract distances and update regional cache
- **convert-billing-format** - Convert billing format to template

## Code Style

- snake_case for files, functions, variables; UPPER_SNAKE for constants
- Chinese acceptable in output messages and domain terms
- No emojis in code or documentation
- Import order: stdlib -> third-party -> local (blank line between groups)
- Prefer `if` checks over `try/except`; use `pd.isna()`/`pd.notna()` for NaN
- See AGENTS.md for detailed coding guidelines
