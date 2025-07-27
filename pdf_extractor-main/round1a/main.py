import os
import json
from heading_extractor import extract_outline

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        in_path = os.path.join(INPUT_DIR, filename)
        print(f"Processing: {filename}")

        result = extract_outline(in_path)

        out_path = os.path.join(OUTPUT_DIR, filename[:-4] + ".json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f" -> saved: {out_path}")

if __name__ == "__main__":
    main()
