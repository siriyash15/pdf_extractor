import json
import os
import time
from extractor import extract_all_documents
from ranker import compute_relevance

# === Configuration ===
INPUT_DIR = "input"
OUTPUT_DIR = "output"
OUTPUT_FILE = "ranked_sections.json"

# Example persona + job — customize as needed
PERSONA = "PhD Researcher in Computational Biology"
JOB_TO_BE_DONE = "Prepare a literature review on graph neural networks for drug discovery"

def main():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: Extract headings and content from PDFs
    print(f"📥 Extracting sections from PDFs in '{INPUT_DIR}'...")
    sections = extract_all_documents(INPUT_DIR)

    # Step 2: Rank relevance for persona + job
    print(f"🔍 Ranking based on persona + job: {PERSONA} | {JOB_TO_BE_DONE}")
    ranked_sections = compute_relevance(PERSONA, JOB_TO_BE_DONE, sections)

    # Step 3: Build final output
    output = {
        "metadata": {
            "input_documents": os.listdir(INPUT_DIR),
            "persona": PERSONA,
            "job_to_be_done": JOB_TO_BE_DONE,
            "timestamp": timestamp
        },
        "sections": []
    }

    for i, sec in enumerate(ranked_sections[:10]):  # Top 10 relevant
        output["sections"].append({
            "document": sec["document"],
            "page": sec["page"],
            "section_title": sec["title"],
            "importance_rank": i + 1,
            "score": round(sec["score"], 4),
            "refined_text": sec["content"][:1000]  # Trim large text
        })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Output saved to '{out_path}'\n")

if __name__ == "__main__":
    main()
