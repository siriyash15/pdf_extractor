import sys
import json
from extractor import extract_outline

if __name__ == "__main__":
    pdf_path = sys.argv[1]  # e.g., sample.pdf
    lang = sys.argv[2] if len(sys.argv) > 2 else 'en'

    result = extract_outline(pdf_path, lang)

    output_filename = pdf_path.replace('.pdf', '.json')
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted: {output_filename}")
