---
name: fill-stores
description: Fill store names from txt files into billing Excel files for Hefei and Jiangxi logistics. Creates a new Excel file with the specified date suffix.
allowed-tools: Bash(python:*), Bash(source .venv/bin/activate*), Bash(.venv/bin/python:*), Read
---

# Fill Store Names to Billing

This skill fills logistics store names from txt files into billing Excel files, supporting both Hefei and Jiangxi regions. It automatically creates a new Excel file with the specified date suffix.

## Usage

When the user asks to fill store names, fill billing data, or create a new billing file with store names:

```bash
.venv/bin/python .claude/skills/fill-stores/scripts/fill_billing.py <source_excel> <stores_txt> <date_suffix> [year]
```

### Parameters

- `source_excel`: Source billing Excel file (e.g., `data/hefei/summary/2026/惠宜选合肥仓1月份对账单0112.xlsx`)
- `stores_txt`: Store names txt file (e.g., `data/hefei/details/unresolved/物流店名数据_1.13_1.19.txt`)
- `date_suffix`: New date suffix for output file (e.g., `0119`)
- `year` (optional): Year for dates, defaults to 2026

### Output

The script will:
1. Copy the source Excel file
2. Rename it with the new date suffix (e.g., `惠宜选合肥仓1月份对账单0119.xlsx`)
3. Fill in the store names from the txt file
4. Save the new file in the same directory as the source

### Input TXT Format

The input txt file should contain:
- Date headers (e.g., `1.13`, `1.15`)
- Store names for each vehicle (one per line)
- Empty lines separating different vehicles
- Empty line after each date section

Example:
```
1.13

厉臣便利（邳州青年路店）
帮帮团（邳州长江路店）
惠宜选-徐州新沂店

厉臣便利（徐州奔腾大道店）
惠宜选-徐州沛县店

1.15

惠宜选-六安幸福里店
厉臣-六安御景湾店
```

## Examples

### Hefei Example

Fill Hefei billing data from 1.13-1.19 into a new 0119 billing file:

```bash
.venv/bin/python .claude/skills/fill-stores/scripts/fill_billing.py \
  data/hefei/summary/2026/惠宜选合肥仓1月份对账单0112.xlsx \
  data/hefei/details/unresolved/物流店名数据_1.13_1.19.txt \
  0119
```

This will:
1. Copy `惠宜选合肥仓1月份对账单0112.xlsx`
2. Create `惠宜选合肥仓1月份对账单0119.xlsx`
3. Fill store names from `物流店名数据_1.13_1.19.txt`
4. Automatically continue from the last sequence number in the Excel

### Jiangxi Example

Fill Jiangxi billing data:

```bash
.venv/bin/python .claude/skills/fill-stores/scripts/fill_billing.py \
  data/jiangxi/summary/2026/江西对账单0110.xlsx \
  data/jiangxi/details/物流店名数据_1.11_1.13.txt \
  0113
```

### Specify Different Year

If working with a different year:

```bash
.venv/bin/python .claude/skills/fill-stores/scripts/fill_billing.py \
  data/hefei/summary/2025/惠宜选合肥仓12月份对账单1225.xlsx \
  data/hefei/details/物流店名数据_12.26_12.31.txt \
  1231 \
  2025
```

## How It Works

1. **Parse TXT Data**: Reads the txt file and groups stores by date and vehicle
2. **Find Starting Position**: Locates the first empty row in the Excel file
3. **Continue Sequence**: Automatically continues from the last sequence number
4. **Fill Data**: For each vehicle, adds:
   - Sequence number (auto-incremented)
   - Date (converted to Excel serial number)
   - Store names (joined with newlines)
5. **Save File**: Saves the updated Excel file with the new date suffix

## Notes

- Works for both Hefei (惠宜选合肥仓) and Jiangxi (江西) regions
- Automatically detects the last sequence number and continues from there
- Dates are converted to Excel date serial numbers
- Store names for each vehicle are joined with newline characters
- The output file is automatically named based on the date suffix
- Supports UTF-8 encoding for Chinese characters
- Default year is 2026, but can be customized

## Expected Excel Structure

The Excel file should have:
- Column A: Sequence number (序号)
- Column B: Date (日期) as Excel serial number
- Column C: Store names (店名) with newlines between stores
