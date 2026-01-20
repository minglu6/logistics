import os
import glob
import re
import sys

# Check for libraries
try:
    from paddleocr import PaddleOCR
except ImportError:
    print("Error: Missing libraries.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

def get_file_sort_key(filepath):
    """
    Sorts files by the version number in the filename (e.g., 江西1.2.jpg -> 1.2).
    """
    filename = os.path.basename(filepath)
    match = re.search(r'(\d+\.\d+)', filename)
    if match:
        return float(match.group(1))
    return 0

def is_header(text):
    """
    Checks if the text looks like a car header (e.g., "临努1车").
    """
    return "临努" in text and "车" in text

def is_store_name(text):
    """
    Heuristic to determine if a text string is a store name.
    1. Should contain store-related keywords.
    2. Should NOT be a header or logistics instruction.
    """
    # Keywords that strongly suggest a store name
    store_keywords = ["超市", "便利", "店", "惠宜选", "共橙", "历臣"]
    # Keywords that suggest it is metadata or other columns (to exclude)
    exclude_keywords = ["临努", "车", "到货", "回收", "带回", "全部", "市", "县", "路", "大道"] 
    # Note: Store names often contain "路" or "大道" (in the address part), so we must be careful.
    # The OCR often reads "宜春市" (City column) separate from the store name.
    
    # Strict exclusion
    if any(k in text for k in ["回收", "带回", "到货", "全部"]):
        return False
        
    # If it's just a city name or code (short text), skip it
    if len(text) < 4: 
        return False
        
    # Check for store keywords
    if any(k in text for k in store_keywords):
        return True
        
    return False

def extract_logistics_data():
    print("Initializing OCR (this may take a moment)...")
    # lang='ch' for Chinese. use_textline_orientation=True helps with rotated text.
    ocr = PaddleOCR(use_textline_orientation=True, lang="ch")
    
    # Find all matching images
    extensions = ['*.jpg', '*.png', '*.jpeg']
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join('.', '江西' + ext)))
    
    # Sort files naturally (1.2, 1.3, ...)
    files.sort(key=get_file_sort_key)
    
    all_output_lines = []
    
    for file_path in files:
        print(f"Processing: {file_path}")
        result = ocr.ocr(file_path, cls=True)
        
        if not result or result[0] is None:
            continue
            
        # result[0] is a list of [box, (text, score)]
        # We sort boxes by vertical position (Y) to process top-to-bottom
        boxes = result[0]
        boxes.sort(key=lambda x: x[0][0][1])
        
        file_version = get_file_sort_key(file_path)
        all_output_lines.append(f"{file_version}") # Add the "1.2", "1.3" label
        
        current_car_lines = []
        
        for line in boxes:
            text = line[1][0]
            
            if is_header(text):
                # We found a header like "临努1车"
                # If we have accumulated rows for a previous car, add them to output
                # Then add a blank line separator
                if current_car_lines:
                    all_output_lines.extend(current_car_lines)
                    all_output_lines.append("") # Blank line between cars
                    current_car_lines = []
                
                # If there are lines already in all_output_lines (from previous file or car), 
                # ensure there is separation if not already present.
                if all_output_lines and all_output_lines[-1] != "":
                     all_output_lines.append("")
                     
                continue # Do not add the header text itself
            
            if is_store_name(text):
                current_car_lines.append(text)
        
        # Append any remaining lines from the last car in the file
        if current_car_lines:
            all_output_lines.extend(current_car_lines)
            
        # Add a separator between files
        if all_output_lines and all_output_lines[-1] != "":
            all_output_lines.append("")
            all_output_lines.append("") # Double space between files for clarity

    # Write to file
    output_filename = "auto_extracted_data.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        # Clean up multiple empty lines
        final_content = "\n".join(all_output_lines)
        final_content = re.sub(r'\n{3,}', '\n\n', final_content) # Max 2 empty lines
        f.write(final_content)
        
    print(f"\nExtraction complete. Data saved to: {output_filename}")

if __name__ == "__main__":
    extract_logistics_data()
