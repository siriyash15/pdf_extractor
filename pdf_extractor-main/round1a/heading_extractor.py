import fitz  # PyMuPDF
import re
from collections import defaultdict


LANG_HEADING_KEYWORDS = {
    'en': ['chapter', 'section', 'contents', 'introduction', 'program', 'aim', 'algorithm', 'code', 'result', 'output', 'procedure'],
    'hi': ['अध्याय', 'अनुच्छेद', 'परिचय', 'कार्यक्रम', 'लक्ष्य', 'प्रक्रिया', 'परिणाम'],
    'ta': ['அத்தியாயம்', 'பிரிவு', 'அறிமுகம்', 'நிரல்', 'நோக்கம்', 'செயல்முறை', 'விளைவுகள்'],
    'bn': ['অধ্যায়', 'অনুচ্ছেদ', 'ভূমিকা', 'প্রোগ্রাম', 'উদ্দেশ্য', 'পদ্ধতি', 'ফলাফল'],
    'te': ['అధ్యాయం', 'విభాగం', 'పరిచయం', 'ప్రోగ్రాం', 'లక్ష్యం', 'విధానం', 'ఫలితాలు'],
    'gu': ['અધ્યાય', 'વિભાગ', 'પરિચય', 'પ્રોગ્રામ', 'હેતુ', 'પ્રક્રિયા', 'પરિણામ'],
    'mr': ['अध्याय', 'परिच्छेद', 'परिचय', 'कार्यक्रम', 'उद्दिष्ट', 'प्रक्रिया', 'निकाल'],
    'ur': ['باب', 'دفعہ', 'تعارف', 'پروگرام', 'مقصد', 'طریقہ', 'نتیجہ'],
    'pa': ['ਅਧਿਆਇ', 'ਧਾਰਾ', 'ਭੂਮਿਕਾ', 'ਕਾਰਜਕ੍ਰਮ', 'ਉਦੇਸ਼', 'ਕਾਰਜਵਿਧੀ', 'ਨਤੀਜਾ'],
    'ja': ['章', '節', '紹介', 'プログラム', '目的', '手順', '結果'],
    'zh': ['章节', '部分', '介绍', '程序', '目标', '过程', '结果', '实验', '小结'],
    'ko': ['장', '절', '소개', '프로그램', '목표', '절차', '결과'],
    'es': ['capítulo', 'sección', 'introducción', 'programa', 'objetivo', 'procedimiento', 'resultado'],
    'fr': ['chapitre', 'section', 'introduction', 'programme', 'objectif', 'procédure', 'résultat'],
    'de': ['kapitel', 'abschnitt', 'einleitung', 'programm', 'ziel', 'vorgehen', 'ergebnis'],
    'it': ['capitolo', 'sezione', 'introduzione', 'programma', 'obiettivo', 'procedura', 'risultato'],
    'pt': ['capítulo', 'seção', 'introdução', 'programa', 'objetivo', 'procedimento', 'resultado'],
}


ALL_KEYWORDS = set()
for v in LANG_HEADING_KEYWORDS.values():
    ALL_KEYWORDS.update([w.lower() for w in v])

HEADING_REGEXES = [
    r'^PROGRAM\s+\d+',
    r'^(AIM|ALGORITHM|CODE|OUTPUT|RESULT|PROCEDURE|INTRODUCTION|实验|小结)$',
    r'^[A-Z][A-Z\s]{2,}$',
    r'^[0-9]+(\.[0-9]+)*\s+[A-Z].+',
    r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){0,5}$',
    r'^[\u4e00-\u9fa5]{2,10}$'
]

def is_heading_like(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    for p in HEADING_REGEXES:
        if re.match(p, t, re.IGNORECASE):
            return True
    low = t.lower()
    return any(kw in low for kw in ALL_KEYWORDS)

def get_title(doc):
    first_page = doc[0].get_text("dict")
    title_candidates = []
    for block in first_page["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    title_candidates.append((span["size"], text))
    if title_candidates:
        return sorted(title_candidates, reverse=True)[0][1]
    return ""

def cluster_fonts(doc):
    """
    Return top (font, size) combos sorted by size & frequency.
    We'll map them to Title/H1/H2/H3.
    """
    font_info = defaultdict(lambda: defaultdict(int))
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font = span.get("font", "")
                    size = round(span.get("size", 0))
                    font_info[font][size] += 1

    font_profile = []
    for font, sizes in font_info.items():
        total = sum(sizes.values())
        most_common_size = max(sizes.items(), key=lambda x: x[1])[0]
        font_profile.append((font, most_common_size, total))

   
    font_profile.sort(key=lambda x: (-x[1], -x[2]))
    return font_profile[:4]

def map_level(tag_idx):
    if tag_idx == 0:
        return "Title"
    if tag_idx == 1:
        return "H1"
    if tag_idx == 2:
        return "H2"
    return "H3"

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    title = get_title(doc)
    outline = []

    font_clusters = cluster_fonts(doc)
    font_tag = {(f, s): i for i, (f, s, _) in enumerate(font_clusters)}

    seen = set()

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue

                text = " ".join(s["text"].strip() for s in spans if s["text"].strip())
                if not text or text in seen:
                    continue
                seen.add(text)

                
                max_span = max(spans, key=lambda s: s.get("size", 0))
                dom_font = max_span.get("font", "")
                dom_size = round(max_span.get("size", 0))

                
                if is_heading_like(text):
                    tag_idx = font_tag.get((dom_font, dom_size), 3)
                    lvl = map_level(tag_idx)
                    
                    if lvl == "Title":
                        if not title:
                            title = text
                        else:
                            lvl = "H1"
                    if lvl != "Title":
                        outline.append({
                            "level": lvl,
                            "text": text,
                            "page": page_num
                        })

   
    if not title:
        for h in outline:
            if h["level"] == "H1":
                title = h["text"]
                break

    return {
        "title": title,
        "outline": outline
    }
