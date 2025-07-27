from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")  
def compute_relevance(persona, job, sections):
    query_text = persona + " " + job
    query_embedding = model.encode([query_text])[0]

    scored_sections = []

    for section in sections:
        section_text = section["title"] + " " + section["content"]
        section_embedding = model.encode([section_text])[0]
        score = cosine_similarity(
            [query_embedding],
            [section_embedding]
        )[0][0]
        section["score"] = float(score)
        scored_sections.append(section)

    
    scored_sections.sort(key=lambda x: x["score"], reverse=True)
    return scored_sections
