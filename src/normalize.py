import pandas as pd
from rapidfuzz import process, fuzz
from src.catalogue import clean_name

def build_index(cat):
    return list(cat["brand_clean"].unique())

def normalize_one(raw, brand_list, cat, threshold):
    q = clean_name(raw)
    if q == "":
        return {"matched_generic": None, "score": 0.0, "abstained": True}
    best = process.extractOne(q, brand_list, scorer=fuzz.ratio)
    if best is None:
        return {"matched_generic": None, "score": 0.0, "abstained": True}
    name, score, _ = best
    score = score / 100.0
    if score < threshold:
        return {"matched_generic": None, "score": score, "abstained": True}
    hits = cat[cat["brand_clean"] == name]["generic_clean"].tolist()
    return {"matched_generic": hits, "score": score, "abstained": False}
