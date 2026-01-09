import json
import difflib
import re

def tokenize(text: str):
    return re.findall(r"\w+", (text or "").lower())

def smart_match(query, target):
    return difflib.SequenceMatcher(None, query.lower(), target.lower()).ratio() > 0.55

def load_guide():
    with open("resume_guide_dataset.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_resume_guide_for_domain(user_query):
    data = load_guide()
    q = user_query.lower().strip()

    # Step 1 — exact key match
    if q in data:
        return q, data[q]

    # Step 2 — exact substring match
    for d in data.keys():
        if q in d.lower():
            return d, data[d]

    # Step 3 — strict token containment (at least 2 matching words)
    tokens = tokenize(q)
    best_domain = None
    best_score = 0

    for d in data.keys():
        score = 0
        dom_tokens = tokenize(d)
        for t in tokens:
            if t in dom_tokens:
                score += 1
        if score > best_score:
            best_score = score
            best_domain = d

    if best_score >= 2:
        return best_domain, data.get(best_domain)

    # Step 4 — HIGH cutoff fuzzy match
    matches = difflib.get_close_matches(q, list(data.keys()), cutoff=0.80, n=1)
    if matches:
        return matches[0], data[matches[0]]

    return None, None
