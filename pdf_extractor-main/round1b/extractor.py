import fitz 
import re
from collections import defaultdict
import os

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

HEADING_PATTERNS = [
    r'^PROGRAM\s+\d+',
    r'^(AIM|ALGORITHM|CODE|OUTPUT|RESULT|PROCEDURE|INTRODUCTION|实验|小结)$',
    r'^[A-Z][A-Z\s]{2,}$',
    r'^[0-9]+(\.[0-9]+)*\s+[A-Z].+',
    r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){0,5}$',
    r'^[\u4e00-\u9fa5]{2,10}$' 
]

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

def is_heading_like(text):
    return any(re.match(p, text.strip(), re.IGNORECASE) for p in HEADING_PATTERNS)

def cluster_fonts_by_page(doc):
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
    return font_profile[:5]

def determine_level(text, size, is_bold, common_sizes, font_tag):
    if re.match(r'^PROGRAM\s+\d+', text, re.IGNORECASE):
        return "H1"
    if text.upper() in ["AIM", "ALGORITHM", "PROCEDURE", "OUTPUT", "RESULT", "实验", "小结"]:
        return "H2"
    if font_tag == 0:
        return "H1"
    elif font_tag == 1:
        return "H2"
    return "H3"

def extract_outline(pdf_path, lang='en'):
    doc = fitz.open(pdf_path)
    keywords = LANG_HEADING_KEYWORDS.get(lang, LANG_HEADING_KEYWORDS['en'])
    title = get_title(doc)
    outline = []

    font_clusters = cluster_fonts_by_page(doc)
    font_tags = {(font, size): i for i, (font, size, _) in enumerate(font_clusters)}

    seen = set()
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                max_size = 0
                is_bold = False
                dominant_font = ""

                for span in line["spans"]:
                    content = span["text"].strip()
                    if not content:
                        continue
                    line_text += content + " "
                    if span["size"] > max_size:
                        max_size = span["size"]
                        dominant_font = span.get("font", "")
                    if "bold" in span.get("font", "").lower():
                        is_bold = True

                text = line_text.strip()
                if not text or text in seen:
                    continue
                seen.add(text)

                lowered = text.lower()
                if any(k in lowered for k in keywords) or is_heading_like(text):
                    tag = font_tags.get((dominant_font, round(max_size)), 2)
                    level = determine_level(text, max_size, is_bold, [], tag)
                    outline.append({
                        "level": level,
                        "text": text,
                        "page": page_num
                    })

    return {
        "title": title,
        "outline": outline
    }

def extract_all_documents(input_dir, lang='en'):
    all_sections = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            doc = fitz.open(pdf_path)
            result = extract_outline(pdf_path, lang)
            for section in result["outline"]:
                content = doc[section["page"] - 1].get_text()
                all_sections.append({
                    "document": filename,
                    "page": section["page"],
                    "title": section["text"],
                    "content": content.strip()
                })
    return all_sections
