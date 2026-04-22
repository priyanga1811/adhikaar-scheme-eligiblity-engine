
import json
def load_schemes():
    """
    Load a hardcoded list of government schemes with their eligibility rules.
    """
    return [
        {
            "id": "ignwps",
            "scheme_name": "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
            "category": "Pension",
            "conditions": {
                "gender": ["female"],
                "marital_status": ["widow"],
                "min_age": 40,
                "max_income": 100000
            },
            "required_documents": ["Aadhaar Card", "BPL Ration Card", "Husband's Death Certificate", "Bank Account Passbook", "Age Proof"],
            "official_apply_link": "https://nsap.nic.in/",
            "benefit_summary": "Financial assistance of ₹300/month (varies by state) to widows below the poverty line.",
            "application_steps": [
                "Visit the nearest Gram Panchayat or Block Office.",
                "Obtain the IGNWPS application form.",
                "Fill the form and attach the required documents.",
                "Submit to the Social Welfare Department officer."
            ]
        },
        {
            "id": "pmsym",
            "scheme_name": "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)",
            "category": "Pension",
            "conditions": {
                "min_age": 18,
                "max_age": 40,
                "max_income": 180000,
                "occupation": ["unorganized", "worker", "farmer", "unemployed", "labourer"]
            },
            "required_documents": ["Aadhaar Card", "Savings Bank Account / Jan Dhan Account with IFSC"],
            "official_apply_link": "https://maandhan.in/",
            "benefit_summary": "Assured monthly pension of ₹3000 after attaining the age of 60 years.",
            "application_steps": [
                "Visit nearest Common Service Centre (CSC).",
                "Carry Aadhaar and Bank account details.",
                "Initial contribution amount in cash will be made to the Village Level Entrepreneur (VLE)."
            ]
        },
        {
            "id": "ujjwala",
            "scheme_name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
            "category": "Women",
            "conditions": {
                "gender": ["female"],
                "min_age": 18,
                "max_income": 100000
            },
            "required_documents": ["Aadhaar Card", "Ration Card", "Bank Account Details", "Passport Size Photograph"],
            "official_apply_link": "https://www.pmuy.gov.in/",
            "benefit_summary": "Provides a deposit-free LPG connection to women from BPL households.",
            "application_steps": [
                "Download the application form from PMUY website or collect it from nearest LPG distributor.",
                "Fill the form and submit it at the LPG distributor office.",
                "Document verification will be done before issuing connection."
            ]
        },
        {
            "id": "pmay",
            "scheme_name": "Pradhan Mantri Awas Yojana (PMAY)",
            "category": "Housing",
            "conditions": {
                "max_income": 1800000
            },
            "required_documents": ["Aadhaar Card", "Income Proof", "Property Documents", "Bank Statement"],
            "official_apply_link": "https://pmaymis.gov.in/",
            "benefit_summary": "Credit linked subsidy scheme for buying or building a house.",
            "application_steps": [
                "Apply online on PMAY portal or through CSCs.",
                "Fill application with Aadhaar details.",
                "Apply for home loan at banks/HFCs claiming PMAY subsidy."
            ]
        },
        {
            "id": "bihar_widow",
            "scheme_name": "Bihar State Widow Pension Scheme",
            "category": "State-specific",
            "conditions": {
                "state": ["bihar"],
                "marital_status": ["widow"],
                "min_age": 18,
                "max_income": 60000
            },
            "required_documents": ["Aadhaar Card", "Husband's Death Certificate", "Income Certificate", "Domicile Certificate of Bihar"],
            "official_apply_link": "https://sspmis.bihar.gov.in/",
            "benefit_summary": "Monthly pension for widows residing in Bihar.",
            "application_steps": [
                "Apply online on SSPMIS portal or visit RTPS counter.",
                "Provide Aadhaar and bank details.",
                "Submit hard copies to the block office if required."
            ]
        },
        {
            "id": "eshram",
            "scheme_name": "e-Shram Support",
            "category": "Employment",
            "conditions": {
                "min_age": 16,
                "max_age": 59,
                "occupation": ["unorganized", "worker", "farmer", "unemployed", "labourer"]
            },
            "required_documents": ["Aadhaar Card", "Aadhaar linked active mobile number", "Bank account details"],
            "official_apply_link": "https://eshram.gov.in/",
            "benefit_summary": "Accidental insurance cover of ₹2 Lakhs under PMSBY and social security benefits.",
            "application_steps": [
                "Visit e-Shram portal.",
                "Self-register using Aadhaar linked mobile number.",
                "Fill personal, address, and bank details."
            ]
        },
        {
            "id": "mahila_rojgar",
            "scheme_name": "Mukhyamantri Mahila Rojgar Yojana",
            "category": "Women",
            "conditions": {
                "gender": ["female"],
                "min_age": 18,
                "max_age": 50,
                "state": ["maharashtra", "bihar", "uttar pradesh"],
                "max_income": 200000
            },
            "required_documents": ["Aadhaar Card", "Project Report", "Caste Certificate (if applicable)", "Bank Details"],
            "official_apply_link": "https://www.india.gov.in/",
            "benefit_summary": "Financial assistance and subsidized loans for women to start micro-enterprises.",
            "application_steps": [
                "Visit the District Industries Centre (DIC).",
                "Submit the project proposal and application.",
                "Bank approval and subsidy disbursement."
            ]
        }
    ]

def normalize_profile(profile):
    """
    Normalize user profile data for matching logic.
    """
    p = {}
    for k, v in profile.items():
        if v is None or str(v).strip() == "":
            p[k] = None
        else:
            if isinstance(v, str):
                p[k] = v.lower().strip()
            else:
                p[k] = v
                
    # Normalize income
    if 'income' in p and p['income']:
        try:
            if isinstance(p['income'], str):
                val = p['income'].replace(',', '').replace('₹', '').replace('rs', '').strip()
                if 'lakh' in val:
                    num = float(val.replace('lakh', '').strip())
                    p['income'] = int(num * 100000)
                else:
                    p['income'] = float(val)
            else:
                p['income'] = float(p['income'])
        except ValueError:
            p['income'] = None

    # Normalize age
    if 'age' in p and p['age']:
        try:
            p['age'] = int(p['age'])
        except ValueError:
            p['age'] = None

    # Handle widow_status derived from marital_status
    if p.get('marital_status') == 'widow':
        p['widow_status'] = True
    elif p.get('widow_status') in ['true', 'yes', True, '1']:
        p['marital_status'] = 'widow'
        
    return p

def segment_user(profile):
    """
    AI Concept: User Segmentation / Clustering
    Classifies the user into demographic segments to boost relevant schemes.
    """
    segments = set()
    age = profile.get('age')
    income = profile.get('income')
    occupation = profile.get('occupation')
    marital_status = profile.get('marital_status')
    gender = profile.get('gender')

    if income is not None and income <= 150000:
        segments.add("bpl")
        segments.add("low income")
    
    if age is not None:
        if age >= 60:
            segments.add("senior citizen")
            segments.add("old age")
            segments.add("elderly")
        elif age <= 30:
            segments.add("youth")
            segments.add("student")
    
    if occupation in ["farmer", "agriculture"]:
        segments.add("farmer")
        segments.add("agriculture")
    
    if marital_status == "widow":
        segments.add("widow")
        
    if gender == "female":
        segments.add("women")
        segments.add("female")

    return list(segments)

def calculate_relevance_score(profile, scheme, user_segments):
    """
    AI Concept: Content-Based Filtering / Relevance Scoring
    Calculates Jaccard-like keyword overlap between user profile and scheme keywords.
    """
    scheme_keywords = set(k.lower() for k in scheme.get("match_keywords", []))
    
    if not scheme_keywords:
        return 50 # Default relevance if no keywords defined

    # Implicit keywords derived from profile
    user_keywords = set(user_segments)
    if profile.get('occupation'):
        user_keywords.add(str(profile['occupation']).lower())
    if profile.get('state') and profile['state'] != "Other":
        user_keywords.add(str(profile['state']).lower())
        
    # Calculate Jaccard similarity or simple intersection score
    intersection = len(user_keywords.intersection(scheme_keywords))
    union = len(scheme_keywords) # Using scheme_keywords size as base to not penalize users with lots of segments
    
    if union == 0:
        return 50
        
    relevance_pct = min(100, int((intersection / union) * 100))
    # Give a base score so we don't zero out completely unless absolutely irrelevant
    return max(20, relevance_pct)

def calculate_rule_score(profile, scheme):
    """
    AI Concept: Expert System / Rule-Based Logic
    Validates hard constraints.
    Returns: score (0-100), critical_mismatch (bool), why_matched (list), why_not_matched (list), missing_fields (list)
    """
    matched_conditions = 0
    total_conditions = 0
    why_matched = []
    why_not_matched = []
    missing_fields = []
    critical_mismatch = False

    # 1. Gender
    scheme_gender = scheme.get('gender', [])
    if scheme_gender and "any" not in scheme_gender:
        total_conditions += 1
        if profile.get('gender'):
            if profile['gender'] in scheme_gender:
                matched_conditions += 1
                why_matched.append(f"Gender matches ({profile['gender'].capitalize()})")
            else:
                why_not_matched.append(f"Requires gender: {', '.join(scheme_gender).capitalize()}")
                critical_mismatch = True
        else:
            missing_fields.append("gender")

    # 2. Marital status
    scheme_marital = scheme.get('marital_status', [])
    if scheme_marital and "any" not in scheme_marital:
        total_conditions += 1
        if profile.get('marital_status'):
            if profile['marital_status'] in scheme_marital:
                matched_conditions += 1
                why_matched.append(f"Marital status matches ({profile['marital_status'].capitalize()})")
            else:
                why_not_matched.append(f"Requires marital status: {', '.join(scheme_marital).capitalize()}")
                critical_mismatch = True
        else:
            missing_fields.append("marital_status")

    # 3. State
    scheme_state = scheme.get('state', [])
    if scheme_state and "all" not in scheme_state:
        total_conditions += 1
        if profile.get('state'):
            if profile['state'] in scheme_state:
                matched_conditions += 1
                why_matched.append(f"Resident of eligible state ({profile['state'].capitalize()})")
            else:
                why_not_matched.append(f"Requires residence in: {', '.join([s.capitalize() for s in scheme_state])}")
                critical_mismatch = True
        else:
            missing_fields.append("state")

    # 4. Age
    age_limit = scheme.get('age_limit', {})
    min_age = age_limit.get('min', 0)
    max_age = age_limit.get('max', 999)
    if min_age > 0 or max_age < 999:
        total_conditions += 1
        if profile.get('age') is not None:
            if min_age <= profile['age'] <= max_age:
                matched_conditions += 1
                why_matched.append(f"Age {profile['age']} is within eligible range ({min_age}-{max_age} yrs)")
            else:
                why_not_matched.append(f"Age must be between {min_age} and {max_age} years")
                critical_mismatch = True
        else:
            missing_fields.append("age")

    # 5. Income
    max_income = scheme.get('income_limit')
    if max_income:
        total_conditions += 1
        if profile.get('income') is not None:
            if profile['income'] <= max_income:
                matched_conditions += 1
                why_matched.append(f"Income ₹{profile['income']:,.0f} is within limit (Max ₹{max_income:,.0f})")
            else:
                why_not_matched.append(f"Income exceeds the maximum limit of ₹{max_income:,.0f}")
                critical_mismatch = True
        else:
            missing_fields.append("income")

    # 6. Occupation
    scheme_occupation = scheme.get('occupation', [])
    if scheme_occupation and "any" not in scheme_occupation:
        total_conditions += 1
        if profile.get('occupation'):
            if profile['occupation'] in scheme_occupation:
                matched_conditions += 1
                why_matched.append(f"Occupation ({profile['occupation'].capitalize()}) is eligible")
            else:
                why_not_matched.append(f"Occupation must be one of: {', '.join(scheme_occupation).capitalize()}")
                critical_mismatch = True
        else:
            missing_fields.append("occupation")

    rule_score = 100 if total_conditions == 0 else int((matched_conditions / total_conditions) * 100)
    
    # Penalize heavily if missing fields exist but no critical mismatch
    if len(missing_fields) > 0 and not critical_mismatch:
        rule_score = max(0, rule_score - (len(missing_fields) * 15))

    return rule_score, critical_mismatch, why_matched, why_not_matched, missing_fields

def fuse_scores(rule_score, relevance_score, priority_score, critical_mismatch):
    """
    AI Concept: Weighted Score Fusion
    Combines rule validation (60%), semantic relevance (30%), and priority base (10%).
    """
    if critical_mismatch:
        return min(rule_score, 20), "No Match"  # hard floor for critical mismatches

    w_rule = 0.60
    w_rel = 0.30
    w_prio = 0.10
    
    norm_prio = min(100, max(0, priority_score))
    final_score = (rule_score * w_rule) + (relevance_score * w_rel) + (norm_prio * w_prio)
    final_score = int(min(100, max(0, final_score)))
    
    if final_score >= 75 and rule_score >= 80:
        status = "Full Match"
    elif final_score >= 40:
        status = "Partial Match"
    else:
        status = "Low Match"
        
    return final_score, status

def score_scheme(profile, scheme):
    """
    Orchestrator for the Hybrid AI Recommendation Pipeline.
    """
    # 1. Segment User (Clustering)
    user_segments = segment_user(profile)
    
    # 2. Rule Validation (Expert System)
    rule_score, critical_mismatch, why_matched, why_not_matched, missing_fields = calculate_rule_score(profile, scheme)
    
    # 3. Content Relevance (Information Retrieval)
    relevance_score = calculate_relevance_score(profile, scheme, user_segments)
    
    # 4. Feature Extraction
    priority_score = scheme.get("priority_score", 50)
    
    # 5. Score Fusion (Ensemble logic)
    final_score, match_status = fuse_scores(rule_score, relevance_score, priority_score, critical_mismatch)
    
    for field in missing_fields:
        why_not_matched.append(f"Missing information: Please provide your {field.replace('_', ' ')}")

    # 6. Explainability Breakdown (XAI)
    xai_breakdown = {
        "rule_contribution": f"{rule_score}% (weight: 60%)",
        "relevance_contribution": f"{relevance_score}% (weight: 30%)",
        "priority_contribution": f"{priority_score}% (weight: 10%)"
    }

    # Inject AI reasoning into the positive feedback list so the UI can display it
    if not critical_mismatch:
        why_matched.insert(0, f"🧠 AI Score Breakdown: Rules={rule_score}%, Relevance={relevance_score}%, Priority={priority_score}")

    return {
        "scheme_name": scheme["scheme_name"],
        "match_status": match_status,
        "match_score": final_score,
        "why_matched": why_matched,
        "why_not_matched": why_not_matched,
        "missing_fields": missing_fields,
        "required_documents": scheme.get("required_documents", []),
        "official_apply_link": scheme.get("official_apply_link", ""),
        "benefit_summary": scheme.get("benefit_summary", ""),
        "application_steps": scheme.get("application_steps", []),
        "category": scheme.get("category", ""),
        "xai_breakdown": xai_breakdown
    }

def match_user_to_schemes(user_profile, schemes_data):
    """
    Match a user profile against all available schemes.
    """
    normalized_profile = normalize_profile(user_profile)
    
    results = []
    for scheme in schemes_data:
        score_result = score_scheme(normalized_profile, scheme)
        results.append(score_result)
        
    return results

def rank_schemes(scored_schemes):
    """
    Rank matched schemes based on their match score in descending order.
    """
    return sorted(scored_schemes, key=lambda x: x['match_score'], reverse=True)

def explain_match(scored_scheme):
    """
    Generate a human-readable explanation of why a user matched or didn't match a scheme.
    AI Concept: Explainable AI (XAI)
    """
    explanation = ""
    if scored_scheme["why_matched"]:
        explanation += "Why you are eligible:\n"
        for reason in scored_scheme["why_matched"]:
            explanation += f"- {reason}\n"
    if scored_scheme["why_not_matched"]:
        if explanation:
            explanation += "\n"
        explanation += "Action Required or Mismatches:\n"
        for reason in scored_scheme["why_not_matched"]:
            explanation += f"- {reason}\n"
            
    explanation += "\n[AI Score Breakdown]\n"
    for k, v in scored_scheme.get("xai_breakdown", {}).items():
        explanation += f"- {k.replace('_', ' ').capitalize()}: {v}\n"
        
    return explanation.strip()

def get_top_matches(user_profile, schemes_data, top_n=5):
    """
    Get the top N matching schemes for a user profile.
    """
    scored = match_user_to_schemes(user_profile, schemes_data)
    ranked = rank_schemes(scored)
    return ranked[:top_n]

def search_schemes(query, schemes_data):
    """Search schemes by keyword, scheme name, category, state, and match keywords."""
    if not query or not query.strip():
        return []
    
    query = query.lower()
    keywords = query.split()
    results = []
    
    for scheme in schemes_data:
        search_text = " ".join([
            scheme.get("scheme_name", ""),
            scheme.get("category", ""),
            " ".join(scheme.get("state", [])),
            scheme.get("eligibility_criteria", ""),
            scheme.get("benefit_summary", ""),
            " ".join(scheme.get("match_keywords", []))
        ]).lower()
        
        score = sum(1 for kw in keywords if kw in search_text)
        if score > 0:
            results.append((score, scheme))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]

def format_scheme_details(scheme):
    """Format scheme details for text display."""
    docs = ", ".join(scheme.get("required_documents", []))
    steps = " ".join(scheme.get("application_steps", []))
    return {
        "name": scheme.get("scheme_name", ""),
        "category": str(scheme.get("category", "")).capitalize(),
        "eligibility": scheme.get("eligibility_criteria", ""),
        "benefits": scheme.get("benefit_summary", ""),
        "documents": docs,
        "application_steps": steps,
        "source_url": scheme.get("official_apply_link", "") or scheme.get("source_url", "")
    }

def generate_speech_text(scheme_details):
    """Helper to convert scheme details into clean speech text."""
    return f"{scheme_details['name']}. Eligibility: {scheme_details['eligibility']}. Benefits: {scheme_details['benefits']}."
