# AGENTS.md - Coding Agent Guidelines

This document provides guidelines for AI coding agents working in this repository.

## Project Overview

A Python-based logistics data processing system for handling delivery distance calculations
and Excel billing data (对账单). The project processes logistics data from multiple
warehouses (Hefei and Jiangxi) to extract, calculate, and reuse distance information
between delivery points.

## Project Structure

```
logistics/
├── scripts/              # Python scripts for data processing
├── data/
│   ├── hefei/           # Hefei logistics data
│   │   ├── cache/       # JSON cache files (reusable_distances.json)
│   │   ├── details/     # Daily Excel files (临努1.*.xlsx)
│   │   └── summary/     # Monthly billing summaries
│   └── jiangxi/         # Jiangxi logistics data
├── docs/                # Documentation (Chinese)
└── README.md            # Project documentation
```

## Running Scripts

### Execute a Script
```bash
python scripts/<script_name>.py
```

### Common Scripts
- `analyze_data.py` - General data analysis
- `analyze_reusable_distances.py` - Distance reuse analysis
- `batch_fill_data.py` - Batch data filling
- `fill_distances_to_january.py` - Fill distances to January billing
- `verify_filled_data.py` - Verify filled data
- `verify_batch_data.py` - Verify batch processing results
- `check_excel_structure.py` - Check Excel file structure

### Testing

No formal testing framework is configured. Verification is done through dedicated
verify scripts:
```bash
python scripts/verify_data.py
python scripts/verify_batch_data.py
python scripts/verify_filled_data.py
```

## Dependencies

Required Python packages (install via pip):
- `pandas` - Data manipulation
- `openpyxl` - Excel file processing
- `numpy` - Numerical operations

Install all dependencies:
```bash
pip install pandas openpyxl numpy
```

## Code Style Guidelines

### File Structure

Scripts should follow this structure:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brief description of script purpose (Chinese is acceptable)
"""

# Standard library imports
import json
import re
import os
from datetime import datetime
from collections import defaultdict

# Third-party imports
import pandas as pd
import numpy as np
from openpyxl import load_workbook

# Constants
STARTING_POINT = "丰树合肥现代综合产业园"
CONFLICT_THRESHOLD = 5.0

# Functions
def function_name():
    """Docstring explaining function"""
    pass

# Main execution
if __name__ == '__main__':
    main()
```

### Naming Conventions

| Element      | Convention    | Example                            |
|--------------|---------------|------------------------------------|
| Files        | snake_case    | `analyze_data.py`, `fill_data.py`  |
| Functions    | snake_case    | `extract_vehicles_from_file()`     |
| Variables    | snake_case    | `vehicle_no`, `distance_map`       |
| Constants    | UPPER_SNAKE   | `STARTING_POINT`, `CONFLICT_THRESHOLD` |
| Classes      | PascalCase    | (Not commonly used in this project)|

### Import Order

1. Standard library imports
2. Third-party imports
3. Local imports (if any)

Blank line between each group.

### Type Hints

Type hints are not used in this codebase. When adding new code, you may add type
hints for clarity but they are optional.

### Docstrings

Use docstrings for all functions:
```python
def parse_shop_and_distance(shop_line):
    """Parse shop line to extract shop name and distance

    Args:
        shop_line: Line containing shop name and optional distance

    Returns:
        tuple: (shop_name, distance) where distance may be None
    """
```

### Error Handling

- Use `try/except` sparingly, primarily for parsing operations
- Prefer `if` statements for None/empty checks
- Use `pd.isna()` and `pd.notna()` for NaN checking

```python
# Good: Check before use
if vehicle_no is None:
    break

if shop_names_cell:
    shop_lines = str(shop_names_cell).split('\n')

# Parsing with fallback
try:
    distance = float(value)
except (ValueError, TypeError):
    distance = None
```

### Path Handling

Use raw strings for Windows paths:
```python
file_path = r'D:\Work\logistics\data\hefei\summary\file.xlsx'
```

### Console Output

- Use Chinese characters in output when appropriate for domain context
- Use visual separators for sections:
```python
print("="*100)
print("Section Title")
print("="*100)
```

- Provide progress feedback for long operations
- Include summary statistics at the end of processing

### Data Processing Patterns

1. Read Excel with pandas or openpyxl:
```python
df = pd.read_excel(file_path, header=None)
wb = load_workbook(file_path)
ws = wb.active
```

2. Process row by row:
```python
for row_idx in range(2, ws.max_row + 1):
    value = ws.cell(row=row_idx, column=1).value
    if value is None:
        break
```

3. Use dictionaries for grouping:
```python
from collections import defaultdict
segment_groups = defaultdict(list)
```

4. Output to JSON for caching:
```python
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## Domain-Specific Rules

### Fixed Starting Points
- Hefei: "丰树合肥现代综合产业园"
- Jiangxi: "惠宜选南昌仓"

### Distance Calculation
- First row distance = starting point to first stop
- Subsequent distances = previous stop to current stop
- Distances can be reused if start/end points match exactly

### Data Format
- Distance data stored as JSON: `{"起点 -> 终点": distance_km}`
- Shop names may contain Chinese characters and special punctuation
- Excel cells may contain newline-separated lists

## Formatting Preferences

- Do NOT use emojis in code or documentation
- Keep console output clean and structured
- Use Chinese for domain-specific terms and user-facing messages
- Use English for code comments and documentation when possible
