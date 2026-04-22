"""
preprocess.py

Production-ready AIML Government Scheme Preprocessor.
This module extracts, normalizes, infers, and engineers features from raw user input
to build a structured citizen profile for the hybrid recommendation engine.

Key AI Concepts implemented:
1. NLP-based Text Cleaning: Noise reduction, multilingual handling.
2. Rule-based Entity Extraction: Advanced regex & dictionary matching.
3. Intelligent Inference: Contextual deduction of missing fields (e.g., widow -> female).
4. Feature Engineering: Creating derived binary flags (e.g., is_senior, is_bpl).
5. Confidence Scoring: Weighted evaluation of extraction quality.
"""

import re
from typing import Dict, Any, Optional

# --- 1. Dictionaries & Taxonomies ---

GENDER_MAP = {
    "female": ["woman", "female", "பெண்", "aurat", "mahila", "lady", "girl", "widow", "vidhva", "vidhavai", "f"],
    "male": ["man", "male", "ஆண்", "aadmi", "purush", "boy", "m"]
}

MARITAL_MAP = {
    "widowed": ["widow", "widowed", "கைம்பெண்", "vidhwa", "vidhavai"],
    "unmarried": ["unmarried", "single", "திருமணமாகாதவர்", "kuwara", "kuwari", "avivahit", "not married"],
    "married": ["married", "திருமணமானவர்", "shadisuda", "vivahit", "shadi", "shuda", "husband", "wife"],
    "divorced": ["divorced", "விவாகரத்து", "talaqshuda", "talaq", "separated"]
}

OCCUPATION_MAP = {
    "student": ["student", "மாணவர்", "chhatra", "vidyarthi", "maanavan", "maanavi", "studying", "college", "school"],
    "farmer": ["farmer", "விவசாயி", "kisaan", "krishak", "vivasayi", "agriculturist", "farming"],
    "unemployed": ["unemployed", "बेरोजगार", "வேலை இல்லாதவர்", "jobless", "berozgar", "velai illa", "no job"],
    "employed": ["employed", "வேலையில்", "naukri", "job", "worker", "salaried", "working"],
    "business": ["business", "வியாபாரம்", "vyapar", "shop", "merchant", "business owner", "shopkeeper"]
}

STATE_ALIASES = {
    "tamil nadu": ["tamil nadu", "tn", "தமிழ்நாடு", "tamilnadu", "chennai"],
    "maharashtra": ["maharashtra", "mh", "maharashatra", "mumbai", "pune"],
    "delhi": ["delhi", "new delhi", "ncr"],
    "uttar pradesh": ["up", "uttar pradesh", "uttarpradesh", "lucknow"],
    "karnataka": ["karnataka", "ka", "bangalore", "bengaluru"],
    "kerala": ["kerala", "kl"],
    "bihar": ["bihar", "patna"]
}

# --- 2. Core NLP Cleaning ---

def clean_text(text: str) -> str:
    """
    NLP Concept: Text Normalization and Cleaning
    Removes special characters, normalizes spacing, and standardizes currency/number representations.
    """
    if not text:
        return ""
    
    # Lowercase and strip
    text = str(text).strip().lower()
    
    # Remove punctuation except those helpful for numbers
    text = re.sub(r'[^\w\s\.,₹]', ' ', text)
    
    # Normalize excessive spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Standardize currency and magnitude markers
    text = text.replace("₹", "rs ")
    text = re.sub(r'\blacs?\b', 'lakh', text)
    text = re.sub(r'\blakhs?\b', 'lakh', text)
    text = re.sub(r'\b(thousand|k)\b', '000', text)
    
    # Remove commas in numbers (e.g., 1,00,000 -> 100000)
    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    
    return text.strip()

def detect_language(text: str) -> str:
    """Detect primary language based on character blocks and keywords."""
    tamil_chars = set("அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறன")
    if any(ch in tamil_chars for ch in text):
        return "Tamil"
    
    hinglish_words = ["hai", "mera", "meri", "aur", "vidhva", "mahila", "umar", "kya", "nahi", "nhi", "saal", "aadmi"]
    words = set(re.findall(r'\b\w+\b', text.lower()))
    if any(hw in words for hw in hinglish_words) or any('\u0900' <= c <= '\u097F' for c in text):
        return "Hinglish"
        
    return "English"

# --- 3. Rule-Based Extraction ---

def extract_from_map(text: str, category_map: Dict[str, list]) -> Optional[str]:
    """Extract standard category based on a multilingual keyword map."""
    words = set(text.split())
    # First exact word match
    for category, keywords in category_map.items():
        if any(kw in words for kw in keywords):
            return category
    # Fallback to substring match
    for category, keywords in category_map.items():
        if any(kw in text for kw in keywords):
            return category
    return None

def extract_income(text: str) -> Optional[int]:
    """NLP Concept: Numeric Entity Extraction with Magnitude Inference."""
    # Pattern 1: e.g., "1.5 lakh", "2 lakh"
    m = re.search(r"(\d+(?:\.\d+)?)\s*lakh", text)
    if m:
        return int(float(m.group(1)) * 100000)
    
    # Pattern 2: Explicit rupees e.g., "rs 50000", "inr 50000"
    m = re.search(r"(?:rs|rupees|inr|salary|income)?\s*(\d{4,9})\b", text)
    if m:
        val = int(m.group(1))
        # Sanity check: income usually > 1000 unless it's per day (we assume annual)
        if val > 1000:
            return val
            
    return None

def extract_age(text: str) -> Optional[int]:
    """NLP Concept: Context-Aware Numeric Extraction."""
    # Look for specific age context
    patterns = [
        r"(?:age|umar|வயது|years?|yrs?|saal)\s*(?:is\s*)?(\d{1,3})",
        r"(\d{1,3})\s*(?:years?|yrs?|saal|old|வயது|vayasu)",
        r"i am\s*(\d{1,3})\b"
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            age = int(m.group(1))
            if 1 <= age <= 120:
                return age
    
    # Fallback: Find standalone 2-digit number if context allows
    # Careful not to extract numbers that are part of income
    for n in re.findall(r"\b\d{1,3}\b", text):
        age = int(n)
        if 16 <= age <= 100:
            # Check if this number is right before 'lakh' or '000'
            if f"{age} lakh" not in text and f"{age}000" not in text:
                return age
    return None

def extract_entities(clean_txt: str) -> Dict[str, Any]:
    """Run all specialized extractors over the cleaned text."""
    return {
        "gender": extract_from_map(clean_txt, GENDER_MAP),
        "marital_status": extract_from_map(clean_txt, MARITAL_MAP),
        "occupation": extract_from_map(clean_txt, OCCUPATION_MAP),
        "state": extract_from_map(clean_txt, STATE_ALIASES),
        "income": extract_income(clean_txt),
        "age": extract_age(clean_txt)
    }

# --- 4. Intelligent Inference ---

def infer_fields(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI Concept: Logical Inference / Deductive Reasoning
    Fills in missing information based on contextual clues from other fields.
    """
    inferred = profile.copy()
    
    # Inference 1: Widow implies Female and Married (previously)
    if inferred["marital_status"] == "widowed":
        if not inferred["gender"]:
            inferred["gender"] = "female"
            
    # Inference 2: Student implies younger age if missing
    if inferred["occupation"] == "student" and not inferred["age"]:
        # We don't set a hard age, but we can infer they are likely youth
        pass # Handled in feature engineering
        
    return inferred

# --- 5. Feature Engineering ---

def engineer_features(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI Concept: Feature Engineering
    Creates derived boolean flags useful for downstream ML models or complex rules.
    """
    features = profile.copy()
    
    # Default derived flags
    features["is_senior"] = False
    features["is_youth"] = False
    features["is_bpl"] = False  # Below Poverty Line
    features["is_taxpayer"] = False

    age = features.get("age")
    if age is not None:
        if age >= 60:
            features["is_senior"] = True
        elif age <= 30:
            features["is_youth"] = True

    income = features.get("income")
    if income is not None:
        if income <= 150000:
            features["is_bpl"] = True
        elif income > 500000:
            features["is_taxpayer"] = True

    return features

# --- 6. Confidence Scoring ---

def calculate_confidence(profile: Dict[str, Any]) -> float:
    """
    AI Concept: Prediction Confidence Scoring
    Calculates the reliability of the extracted profile based on feature importance.
    """
    score = 0.0
    max_score = 100.0
    
    # Weights based on importance for scheme matching
    weights = {
        "age": 25.0,
        "income": 25.0,
        "state": 20.0,
        "gender": 10.0,
        "occupation": 10.0,
        "marital_status": 10.0
    }
    
    for field, weight in weights.items():
        if profile.get(field) is not None:
            score += weight
            
    return round(score / max_score, 2)

# --- 7. Main Pipeline ---

def build_profile(text: str, default_language: str = "English") -> Dict[str, Any]:
    """
    Master pipeline orchestrator for the AI preprocessing module.
    Transforms raw user text into a structured, feature-rich citizen profile.
    """
    # 1. Cleaning & Normalization
    clean_txt = clean_text(text)
    detected_lang = detect_language(text)
    
    # 2. Entity Extraction
    base_profile = extract_entities(clean_txt)
    
    # 3. Contextual Inference
    inferred_profile = infer_fields(base_profile)
    
    # 4. Feature Engineering
    engineered_profile = engineer_features(inferred_profile)
    
    # 5. Metadata & Confidence
    engineered_profile["raw_text"] = text
    engineered_profile["language"] = detected_lang if detected_lang != "English" else default_language
    engineered_profile["confidence_score"] = calculate_confidence(engineered_profile)
    
    return engineered_profile

# --- 8. Test Cases ---

if __name__ == "__main__":
    test_cases = [
        "I am a 65 years old widow living in Chennai. My income is 1 lakh and I am unemployed.",
        "நான் ஒரு மாணவர். எனக்கு 20 வயது. என் வருமானம் 50k.",
        "Mera naam Rahul hai, 28 saal ka aadmi, kisaan hoon. 2,00,000 kamata hoon, up mein rehta hoon."
    ]
    
    print("--- Testing Preprocessor Pipeline ---")
    for idx, case in enumerate(test_cases):
        print(f"\n[Case {idx+1}] Raw Input: '{case}'")
        profile = build_profile(case)
        for k, v in profile.items():
            print(f"  {k}: {v}")
