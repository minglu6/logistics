---
name: convert-billing-format
description: Convert billing Excel files from simplified format (临努格式) to standard template format (江西仓对账单模板格式). Handles date formatting and store name formatting.
allowed-tools: Bash(python:*), Bash(source .venv/bin/activate*), Bash(.venv/bin/python:*), Read
---

# Convert Billing Format

This skill converts logistics billing Excel files from simplified format to the standard template format used for Jiangxi warehouse billing.

## Usage

When the user asks to convert billing format, transform Excel format, or convert to template format:

```bash
.venv/bin/python .claude/skills/convert-billing-format/scripts/convert_format.py <source_excel> [output_excel]
```

### Parameters

- `source_excel`: Source billing Excel file in simplified format
- `output_excel` (optional): Output file path. If not specified, adds `_转换后` suffix to source filename

### Input Format (Simplified/临努格式)

| 日期 | 区域 | 门店 | 公里数 | 单价 | 运费 | 备注 |
|------|------|------|--------|------|------|------|
| 46023 | 外阜 | 店名1：公里数1，店名2：公里数2 | 总公里数 | 4 | 公式 | 备注 |

Store format: `店名1：30，店名2：50，店名3：20`（用中文逗号分隔，冒号后为公里数）

### Output Format (Template/模板格式)

| 序号 | 日期 | 店名 | 公里数 | 公里数 | 不含税单价 | 含税单价 | 不含税合价 | 含税合价 | 司机价格 | 司机价格 | 司机姓名 | 照片 | 备注 |
|------|------|------|--------|--------|------------|----------|------------|----------|----------|----------|----------|------|------|

Store format:
```
店名1-30km
店名2-50km
店名3-20km
```
(换行分隔，带公里数后缀km)

## Examples

### Basic Usage

```bash
.venv/bin/python .claude/skills/convert-billing-format/scripts/convert_format.py \
  "data/jiangxi/summary/2026/惠宜选物流对账单--临努--1月(2).xlsx"
```

Output: `惠宜选物流对账单--临努--1月(2)_转换后.xlsx`

### Specify Output File

```bash
.venv/bin/python .claude/skills/convert-billing-format/scripts/convert_format.py \
  "data/jiangxi/summary/2026/惠宜选物流对账单--临努--1月(2).xlsx" \
  "data/jiangxi/summary/2026/惠宜选江西仓1月份对账单_临努.xlsx"
```

## Conversion Details

### Date Formatting

- Input: Excel serial number (e.g., 46023)
- Output: Displayed as "1月1日" format
- Format code: `M"月"D"日"`

### Store Name Transformation

Input:
```
共橙一站式超市（南昌小洲路店）：30，共橙一站式超市（兴国县将军大道店）：306
```

Output:
```
共橙一站式超市（南昌小洲路店）-30km
共橙一站式超市（兴国县将军大道店）-306km
```

### Formula Columns

The script adds the following formulas (same as template):

| Column | Formula | Description |
|--------|---------|-------------|
| F (不含税单价) | `=G{r}/1.09` | 含税单价除以1.09 |
| G (含税单价) | `=IF(D{r}<=100,440,IF(D{r}<=200,4.2,IF(D{r}<=300,4,3.9)))` | 根据公里数计算 |
| H (不含税合价) | `=D{r}*F{r}` | 公里数乘以不含税单价 |
| I (含税合价) | `=D{r}*G{r}` | 公里数乘以含税单价 |
| J (司机价格) | `=IF(D{r}<=100,400,IF(D{r}<=300,3.2,3))` | 根据公里数计算 |
| K (司机合价) | `=D{r}*J{r}` | 公里数乘以司机价格 |

## Cell Styling

- Date column: Center aligned, wrap text, format "1月1日"
- Store column: Left aligned, wrap text (for multi-line display)
- Other columns: Center aligned

## Notes

- Supports Chinese colons (：) and English colons (:) in store parsing
- Supports Chinese commas (，) as store separator
- Preserves remarks from source file
- Automatically adjusts column width for store names
