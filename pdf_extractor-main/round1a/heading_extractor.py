import fitz 
from collections import defaultdict

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    font_info = defaultdict(list)
    headings = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text or len(text) < 3:
                        continue
                    font_size = round(span["size"])
                    font_info[font_size].append(text)
                    headings.append({
                        "text": text,
                        "size": font_size,
                        "page": page_number + 1
                    })

    size_levels = sorted(font_info.items(), key=lambda x: -len(x[1]))
    level_map = {}
    heading_levels = ['H3', 'H2', 'H1', 'Title']
    
    for i, (size, _) in enumerate(size_levels[:4]):
        level_map[size] = heading_levels[i]

    output = {
        "title": "",
        "outline": []
    }

    for heading in headings:
        level = level_map.get(heading["size"])
        if level == "Title":
            output["title"] = heading["text"]
        elif level:
            output["outline"].append({
                "level": level,
                "text": heading["text"],
                "page": heading["page"]
            })

    output["outline"].sort(key=lambda x: x["page"])
    return output
