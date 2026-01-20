---
name: extract-hefei-stores
description: Extract logistics store names from Hefei Excel files in the unresolved directory. Use when the user asks to extract, process, or get store names from Hefei logistics data.
allowed-tools: Bash(python:*), Bash(.venv/bin/python:*), Read
---

# Extract Hefei Logistics Store Names

This skill extracts store names from Hefei logistics Excel files and outputs them to a formatted text file.

## Usage

When the user asks to extract Hefei logistics store names, use the extraction script:

```bash
.venv/bin/python .claude/skills/extract-hefei-stores/scripts/extract_stores.py <input_directory> [output_file]
```

### Parameters

- `input_directory`: Path to the directory containing Excel files (e.g., `data/hefei/details/unresolved`)
- `output_file` (optional): Output file path. If not provided, generates a default name based on date range

### Default Output Format

If no output file is specified, the script automatically generates:
- File name: `物流店名数据_<start_date>_<end_date>.txt`
- Location: Same as input directory
- Example: `物流店名数据_1.13_1.19.txt`

### Output File Structure

The output text file contains:
1. Date headers (e.g., `1.13`, `1.15`)
2. Store names for each vehicle (one per line)
3. Empty lines separating different vehicles
4. Empty line after each date section

### Example

Extract stores from unresolved directory:

```bash
.venv/bin/python .claude/skills/extract-hefei-stores/scripts/extract_stores.py data/hefei/details/unresolved
```

This will:
1. Scan all Excel files matching `临努*.xlsx` pattern
2. Extract date from filename (e.g., `临努1.13.xlsx` → `1.13`)
3. Extract store names from column 4 (店名列)
4. Group stores by vehicle (empty rows = vehicle separator)
5. Generate output file: `data/hefei/details/unresolved/物流店名数据_1.13_1.19.txt`

### Script Logic

- Reads Excel files from the input directory
- Identifies vehicles by empty rows in the Excel sheet
- Extracts store names from column 4 (店名列)
- Sorts output by date
- Each vehicle's stores are separated by blank lines
- Automatically detects date range from filenames

## Notes

- Excel files must follow the standard Hefei logistics format
- Store names are in column 4 (店名列)
- Empty rows in Excel indicate vehicle boundaries
- Files are processed in date order
- Output uses UTF-8 encoding
