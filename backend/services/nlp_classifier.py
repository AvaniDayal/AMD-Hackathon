CATEGORIES = {
    "lighting": ["dark", "light", "lamp", "unlit", "dim", "no light", "visibility", "cant see"],
    "suspicious": ["suspicious", "stranger", "following", "threat", "unsafe person", "harassment", "scared", "man", "group"],
    "infrastructure": ["broken", "damaged", "pothole", "gate", "road", "blocked", "construction", "closed"],
    "discomfort": ["uncomfortable", "uneasy", "worried", "alone", "isolated", "empty", "unsafe"]
}

SEVERITY = {
    3: ["threat", "harassment", "following", "attack", "scared", "danger"],
    2: ["suspicious", "uncomfortable", "dark", "isolated", "stranger"],
    1: ["broken", "pothole", "dim", "blocked", "damaged"]
}

def classify_incident(text):
    text_lower = text.lower()
    
    category = "discomfort"
    for cat, keywords in CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break
    
    severity = 1
    for sev, keywords in SEVERITY.items():
        if any(kw in text_lower for kw in keywords):
            severity = sev
            break
    
    return {"category": category, "severity": severity}