import os
import json
import logging
from heading_extractor import extract_outline

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def ensure_output_dir(path: str):
    """Create the output directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created output directory: {path}")

def process_pdfs():
    """Process all PDF files in the input directory and save results as JSON."""
    if not os.path.exists(INPUT_DIR):
        logging.error(f"Input directory '{INPUT_DIR}' does not exist.")
        return

    ensure_output_dir(OUTPUT_DIR)

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.pdf')]
    
    if not pdf_files:
        logging.warning(f"No PDF files found in '{INPUT_DIR}'.")
        return

    for filename in pdf_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace('.pdf', '.json')
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        logging.info(f"Processing {filename}...")

        try:
            result = extract_outline(input_path)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logging.info(f"Saved to: {output_path}")
        except Exception as e:
            logging.error(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    process_pdfs()
