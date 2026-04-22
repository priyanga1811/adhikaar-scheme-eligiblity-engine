import json
import streamlit as st
import streamlit.components.v1 as components
import time
import re
import requests
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from gtts import gTTS
from logic import get_top_matches, normalize_profile, search_schemes, format_scheme_details, generate_speech_text
from preprocess import build_profile

def transliterate_to_tamil(text):
    try:
        words = text.split()
        out = []
        for w in words:
            if re.search('[a-zA-Z]', w):
                url = f"https://inputtools.google.com/request?text={w}&itc=ta-t-i0-und&num=1&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"
                r = requests.get(url, timeout=3).json()
                if r[0] == "SUCCESS" and r[1]:
                    out.append(r[1][0][1][0])
                else:
                    out.append(w)
            else:
                out.append(w)
        return " ".join(out)
    except Exception:
        return text

@st.cache_data
def load_schemes_data():
    with open("schemes.json", "r", encoding="utf-8") as f:
        return json.load(f)
        
# --- Translation Dictionaries ---
TEXTS = {
    "en": {
        "app_title": "Adhikaar",
        "app_subtitle": "Find government schemes you may be eligible for",
        "app_trust": "Simple. Multilingual. Explainable.",
        "btn_english": "English",
        "btn_tamil": "தமிழ்",
        "btn_hinglish": "Hinglish",
        "btn_check_eligibility": "Check My Eligibility",
        "btn_browse_schemes": "Browse Schemes",
        
        "how_it_works": "How it works",
        "step1_title": "Tell us about yourself",
        "step1_desc": "Type naturally or use your voice in your preferred language about your current situation.",
        "step2_title": "We check matching schemes",
        "step2_desc": "Our smart engine transparently matches your details against government scheme rules.",
        "step3_title": "View eligible schemes & apply",
        "step3_desc": "Get a clear list of what you qualify for and exactly which documents you need to apply.",
        "btn_back": "← Back",
        "input_title": "Tell us about yourself",
        "input_desc": "Type naturally in English, தமிழ், or Hinglish. Or use voice input below.",
        "quick_tags": "Quick Select Tags:",
        "btn_continue": "Continue to Match",
        "warn_empty_input": "Please enter some details about yourself to continue.",
        "review_title": "Review Your Profile",
        "stepper_1": "✅ Understand input",
        "stepper_2": "✅ Extract details",
        "stepper_3": "⏳ Check schemes",
        "stepper_4": "Prepare results",
        "review_info": "We extracted the following details from your input. Please verify and correct them if needed. Accurate details ensure better scheme matching.",
        "lbl_gender": "Gender",
        "lbl_income": "Annual Income (₹)",
        "lbl_occupation": "Occupation",
        "lbl_marital": "Marital Status",
        "lbl_state": "State",
        "lbl_age": "Age",
        "meta_title": "System Detected Metadata:",
        "meta_lang": "Detected Language:",
        "meta_income": "Normalized Income:",
        "not_provided": "Not provided",
        "btn_edit_input": "← Edit Input",
        "analyzing": "Analyzing rules & matching schemes...",
        "schemes_found": "schemes found",
        "based_on_profile": "Based on your verified profile",
        "btn_start_over": "Start Over",
        
        "warn_no_schemes": "No schemes found. Please go back and edit your details.",
        "match": "Match:",
        "category": "Category:",
        "why_matched": "Why matched:",
        "why_not_matched": "Why not matched:",
        "req_docs": "Required documents:",
        "btn_view_details": "View Details",
        "btn_save_later": "Save for Later",
        "btn_apply": "Apply on Official Site",
        "btn_back_results": "← Back to Results",
        "overview": "Overview",
        "who_can_apply": "Who can apply",
        "matched": "Matched:",
        "not_matched": "Not matched / notes:",
        "how_to_apply": "How to apply",
        "docs_required": "Documents required",
        "btn_find_center": "Find Nearest Application Center",
        "no_match_title": "No exact schemes found",
        "no_match_desc": "We couldn't find a scheme that exactly matches all your details right now. But don't worry, there might still be options for you.",
        "suggestions_title": "Suggestions to improve matches",
        "sugg_1": "<strong>Check your details:</strong> Make sure your income and age are entered correctly.",
        "sugg_2": "<strong>Broaden your search:</strong> Browse all schemes in your state manually.",
        "btn_edit_details": "Edit My Details",
        "btn_browse_all": "Browse All Schemes",
        "status_full_match": "Full Match",
        "status_partial_match": "Partial Match",
        "status_low_match": "Low Match",
        "status_no_match": "No Match",
        "reason_no_pos": "No clear positive matches.",
        "reason_no_neg": "No major mismatches.",
        "lbl_chips": ["Woman", "Widow", "Senior Citizen", "Farmer", "Student", "Disability", "Low Income", "Unemployed"]
    },
    "ta": {
        "app_title": "அதிகார் (Adhikaar)",
        "app_subtitle": "நீங்கள் தகுதிபெறக்கூடிய அரசு திட்டங்களை கண்டறியுங்கள்",
        "app_trust": "எளிமையானது. பன்மொழி ஆதரவு. விளக்கமானது.",
        "btn_english": "English",
        "btn_tamil": "தமிழ்",
        "btn_hinglish": "Hinglish",
        "btn_check_eligibility": "எனது தகுதியை சரிபார்க்கவும்",
        "btn_browse_schemes": "திட்டங்களை உலாவுக",
        "voice_enabled": "🎙️ பன்மொழி குரல் பதிவு வசதி உள்ளது",
        "how_it_works": "இது எப்படி வேலை செய்கிறது",
        "step1_title": "உங்களைப் பற்றி சொல்லுங்கள்",
        "step1_desc": "உங்கள் தற்போதைய சூழ்நிலையைப் பற்றி உங்கள் விருப்பமான மொழியில் தட்டச்சு செய்யவும் அல்லது குரல் பதிவு செய்யவும்.",
        "step2_title": "பொருத்தமான திட்டங்களை சரிபார்க்கிறோம்",
        "step2_desc": "எங்கள் ஸ்மார்ட் எஞ்சின் உங்கள் விவரங்களை அரசு திட்ட விதிகளுடன் வெளிப்படையாகப் பொருத்துகிறது.",
        "step3_title": "தகுதியான திட்டங்களைப் பார்த்து விண்ணப்பிக்கவும்",
        "step3_desc": "நீங்கள் தகுதி பெற்றுள்ள திட்டங்கள் மற்றும் விண்ணப்பிக்கத் தேவையான ஆவணங்களின் தெளிவான பட்டியலைப் பெறுங்கள்.",
        "btn_back": "← பின்செல்",
        "input_title": "உங்களைப் பற்றி சொல்லுங்கள்",
        "input_desc": "ஆங்கிலம், தமிழ் அல்லது ஹிங்க்லிஷில் இயல்பாக தட்டச்சு செய்யவும். அல்லது கீழே உள்ள குரல் பதிவைப் பயன்படுத்தவும்.",
        "quick_tags": "விரைவான தேர்வுகள்:",
        "btn_continue": "பொருத்தத்தை தொடரவும்",
        "warn_empty_input": "தொடர உங்களைப் பற்றிய சில விவரங்களை உள்ளிடவும்.",
        "review_title": "உங்கள் சுயவிவரத்தை சரிபார்க்கவும்",
        "stepper_1": "✅ உள்ளீட்டை புரிந்துகொள்ளல்",
        "stepper_2": "✅ விவரங்களை பிரித்தெடுத்தல்",
        "stepper_3": "⏳ திட்டங்களை சரிபார்த்தல்",
        "stepper_4": "முடிவுகளை தயாரித்தல்",
        "review_info": "உங்கள் உள்ளீட்டிலிருந்து பின்வரும் விவரங்களை எடுத்துள்ளோம். தேவைப்பட்டால் சரிபார்த்து திருத்தவும். சரியான விவரங்கள் சிறந்த திட்ட பொருத்தத்தை உறுதி செய்யும்.",
        "lbl_gender": "பாலினம்",
        "lbl_income": "ஆண்டு வருமானம் (₹)",
        "lbl_occupation": "தொழில்",
        "lbl_marital": "திருமண நிலை",
        "lbl_state": "மாநிலம்",
        "lbl_age": "வயது",
        "meta_title": "கணினி கண்டறிந்த விவரங்கள்:",
        "meta_lang": "கண்டறியப்பட்ட மொழி:",
        "meta_income": "இயல்பாக்கப்பட்ட வருமானம்:",
        "not_provided": "வழங்கப்படவில்லை",
        "btn_edit_input": "← உள்ளீட்டை திருத்து",
        "analyzing": "விதிகளை பகுப்பாய்வு செய்து திட்டங்களை பொருத்துகிறது...",
        "schemes_found": "திட்டங்கள் கிடைத்துள்ளன",
        "based_on_profile": "உங்கள் சரிபார்க்கப்பட்ட சுயவிவரத்தின் அடிப்படையில்",
        "btn_start_over": "மீண்டும் தொடங்கு",
        
        "warn_no_schemes": "திட்டங்கள் எதுவும் கிடைக்கவில்லை. தயவுசெய்து திரும்பிச் சென்று உங்கள் விவரங்களை திருத்தவும்.",
        "match": "பொருத்தம்:",
        "category": "வகை:",
        "why_matched": "ஏன் பொருந்துகிறது:",
        "why_not_matched": "ஏன் பொருந்தவில்லை:",
        "req_docs": "தேவையான ஆவணங்கள்:",
        "btn_view_details": "விவரங்களை காண்க",
        "btn_save_later": "பின்னர் சேமிக்கவும்",
        "btn_apply": "அதிகாரப்பூர்வ தளத்தில் விண்ணப்பிக்கவும்",
        "btn_back_results": "← முடிவுகளுக்கு திரும்புக",
        "overview": "மேலோட்டம்",
        "who_can_apply": "யார் விண்ணப்பிக்கலாம்",
        "matched": "பொருந்தியது:",
        "not_matched": "பொருந்தவில்லை / குறிப்புகள்:",
        "how_to_apply": "எப்படி விண்ணப்பிப்பது",
        "docs_required": "தேவையான ஆவணங்கள்",
        "btn_find_center": "அருகிலுள்ள விண்ணப்ப மையத்தை கண்டறியவும்",
        "no_match_title": "சரியான திட்டங்கள் எதுவும் கிடைக்கவில்லை",
        "no_match_desc": "தற்போது உங்கள் எல்லா விவரங்களுக்கும் பொருந்தக்கூடிய ஒரு திட்டத்தை எங்களால் கண்டுபிடிக்க முடியவில்லை. ஆனால் கவலைப்பட வேண்டாம், உங்களுக்கான மாற்று திட்டங்கள் இருக்கலாம்.",
        "suggestions_title": "பொருத்தங்களை மேம்படுத்துவதற்கான ஆலோசனைகள்",
        "sugg_1": "<strong>உங்கள் விவரங்களை சரிபார்க்கவும்:</strong> உங்கள் வருமானம் மற்றும் வயது சரியாக உள்ளிடப்பட்டுள்ளதா என்பதை உறுதிப்படுத்தவும்.",
        "sugg_2": "<strong>உங்கள் தேடலை விரிவாக்கவும்:</strong> உங்கள் மாநிலத்தில் உள்ள அனைத்து திட்டங்களையும் நாமே தேடி பார்க்கவும்.",
        "btn_edit_details": "எனது விவரங்களை திருத்து",
        "btn_browse_all": "அனைத்து திட்டங்களையும் உலாவுக",
        "status_full_match": "முழுமையான பொருத்தம்",
        "status_partial_match": "பகுதி பொருத்தம்",
        "status_low_match": "குறைந்த பொருத்தம்",
        "status_no_match": "பொருத்தம் இல்லை",
        "reason_no_pos": "தெளிவான நேர்மறையான பொருத்தங்கள் இல்லை.",
        "reason_no_neg": "பெரிய பொருத்தமின்மைகள் இல்லை.",
        "lbl_chips": ["பெண்", "விதவை", "முதியவர்", "விவசாயி", "மாணவர்", "மாற்றுத்திறனாளி", "குறைந்த வருமானம்", "வேலையில்லாதவர்"]
    }
}

DATA_DICT = {
    "Female": "பெண்",
    "Male": "ஆண்",
    "Other": "மற்றவை",
    "Unemployed": "வேலையில்லாதவர்",
    "Farmer": "விவசாயி",
    "Student": "மாணவர்",
    "Employed": "வேலை செய்பவர்",
    "Business": "வியாபாரம்",
    "Widow": "விதவை",
    "Single": "திருமணமாகாதவர்",
    "Married": "திருமணமானவர்",
    "Divorced": "விவாகரத்து பெற்றவர்",
    "Tamil Nadu": "தமிழ்நாடு",
    "Bihar": "பீகார்",
    "Maharashtra": "மகாராஷ்டிரா",
    "Uttar Pradesh": "உத்தர பிரதேசம்"
}

def detect_output_language(text):
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"
    return "en"

def t(key):
    lang = st.session_state.get("output_language", "en")
    return TEXTS.get(lang, TEXTS["en"]).get(key, key)

def t_data(val):
    lang = st.session_state.get("output_language", "en")
    if lang == "ta" and isinstance(val, str):
        return DATA_DICT.get(val, val)
    return val

def translate_explanation(text):
    lang = st.session_state.get("output_language", "en")
    if lang == "en":
        return text
        
    trans = {
        "Gender matches": "பாலினம் பொருந்துகிறது",
        "Female": "பெண்",
        "Male": "ஆண்",
        "Marital status matches": "திருமண நிலை பொருந்துகிறது",
        "Widow": "விதவை",
        "Resident of eligible state": "தகுதியான மாநிலத்தின் வசிப்பவர்",
        "Income": "வருமானம்",
        "is within limit": "வரம்பிற்குள் உள்ளது",
        "Age": "வயது",
        "is within eligible range": "தகுதியான வரம்பிற்குள் உள்ளது",
        "Requires gender": "தேவைப்படும் பாலினம்",
        "Requires marital status": "தேவைப்படும் திருமண நிலை",
        "Requires residence in": "வசிப்பிடம் தேவைப்படும் மாநிலம்",
        "Age must be between": "வயது இவற்றுக்குள் இருக்க வேண்டும்",
        "Income exceeds the maximum limit": "வருமானம் அதிகபட்ச வரம்பை மீறுகிறது",
        "Occupation": "தொழில்",
        "is eligible": "தகுதி உள்ளது",
        "Occupation must be one of": "தொழில் இவற்றில் ஒன்றாக இருக்க வேண்டும்",
        "Missing information: Please provide your": "விடுபட்ட தகவல்: தயவுசெய்து உங்கள் தகவலை வழங்கவும்",
        "Full Match": "முழுமையான பொருத்தம்",
        "Partial Match": "பகுதி பொருத்தம்",
        "Low Match": "குறைந்த பொருத்தம்",
        "No Match": "பொருத்தம் இல்லை",
        "AI Score Breakdown": "AI மதிப்பெண் முறிவு",
        "Rules": "விதிகள்",
        "Relevance": "பொருத்தம்",
        "Priority": "முன்னுரிமை"
    }
    
    for en_text, ta_text in trans.items():
        if en_text in text:
            text = text.replace(en_text, ta_text)
            
    return text

def setup_page():
    st.set_page_config(
        page_title="Adhikaar: Multilingual Scheme Eligibility Engine",
        page_icon="🏛️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"]  { font-family: 'Plus Jakarta Sans', sans-serif; }
        .stApp {
            background-color: #f8fafc;
            background-image: radial-gradient(at 0% 0%, hsla(183,40%,94%,1) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(212,40%,94%,1) 0, transparent 50%);
            background-attachment: fixed;
        }
        .main-header {
            text-align: center;
            font-size: 3.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0d9488, #0369a1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            padding-top: 1rem;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }
        .sub-header {
            text-align: center;
            font-size: 1.2rem;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 1rem;
        }
        .stButton > button {
            border-radius: 14px !important;
            width: 100% !important;
            font-weight: 600 !important;
            border: 1px solid #e2e8f0 !important;
            background-color: #ffffff !important;
            color: #334155 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05) !important;
        }
        .stButton > button * { color: #334155 !important; font-weight: 600 !important; }
        .stButton > button:hover {
            border-color: #0d9488 !important;
            background-color: #f0fdfa !important;
            color: #0d9488 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.1), 0 4px 6px -4px rgba(13, 148, 136, 0.05) !important;
        }
        .stButton > button:hover * { color: #0d9488 !important; }
        .stButton > button:focus {
            outline: none !important;
            border-color: #0d9488 !important;
            box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.15) !important;
            color: #0d9488 !important;
        }
        .stButton > button:focus * { color: #0d9488 !important; }
        .stButton > button:active {
            transform: translateY(0) !important;
            background-color: #ccfbf1 !important;
            box-shadow: none !important;
            color: #0f766e !important;
        }
        .stButton > button:active * { color: #0f766e !important; }
        .stButton > button:disabled {
            background-color: #f8fafc !important;
            border-color: #e2e8f0 !important;
            color: #cbd5e1 !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }
        .stButton > button:disabled * { color: #cbd5e1 !important; }
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important;
            border: none !important;
            color: #ffffff !important;
            box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.3), 0 2px 4px -2px rgba(13, 148, 136, 0.2) !important;
        }
        .stButton > button[data-testid="baseButton-primary"] * { color: #ffffff !important; }
        .stButton > button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #0f766e 0%, #115e59 100%) !important;
            box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.4), 0 4px 6px -4px rgba(13, 148, 136, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        .premium-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 1.75rem 2rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.03), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            margin-bottom: 1.5rem;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .premium-card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02); }
        .premium-card h4 {
            margin-top: 0;
            color: #0f172a;
            font-weight: 700;
            display: flex;
            align-items: center;
            font-size: 1.25rem;
        }
        .scheme-card {
            background: #ffffff;
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid #e2e8f0;
            border-left: 8px solid #0d9488;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .scheme-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, rgba(13, 148, 136, 0.03) 0%, transparent 100%);
            pointer-events: none;
        }
        .scheme-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
            border-color: #cbd5e1;
        }
        .badge-eligible {
            background: #ecfdf5;
            color: #059669;
            padding: 6px 16px;
            border-radius: 24px;
            font-size: 0.85rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 16px;
            border: 1px solid #a7f3d0;
            box-shadow: 0 2px 4px rgba(5, 150, 105, 0.05);
        }
        .badge-partial {
            background: #fefce8;
            color: #ca8a04;
            padding: 6px 16px;
            border-radius: 24px;
            font-size: 0.85rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 16px;
            border: 1px solid #fef08a;
            box-shadow: 0 2px 4px rgba(202, 138, 4, 0.05);
        }
        .trust-text {
            background: linear-gradient(90deg, #0d9488, #2563eb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: 0.5px;
        }
        .stepper {
            display: flex;
            justify-content: space-between;
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 2.5rem;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 1.5rem;
            font-weight: 600;
        }
        .stepper span { display: flex; align-items: center; gap: 8px; }
        .stepper-active {
            color: #0d9488;
            font-weight: 700;
            position: relative;
        }
        .stepper-active::after {
            content: '';
            position: absolute;
            bottom: -1.6rem;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 3px;
            background-color: #0d9488;
            border-radius: 3px 3px 0 0;
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-12px); }
            100% { transform: translateY(0px); }
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            border-radius: 14px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        }
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {
            border-color: #0d9488 !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15), inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        }
        .stMarkdown label, .stSelectbox label, .stTextInput label, .stTextArea label {
            font-weight: 600 !important;
            color: #334155 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.25rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def init_session():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'language' not in st.session_state:
        st.session_state.language = "English"
    if 'output_language' not in st.session_state:
        st.session_state.output_language = "en"
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'profile' not in st.session_state:
        st.session_state.profile = {}
    if 'selected_scheme' not in st.session_state:
        st.session_state.selected_scheme = None
    if 'results' not in st.session_state:
        st.session_state.results = []

def build_backend_profile():
    return {
        "gender": st.session_state.profile.get("Gender"),
        "marital_status": st.session_state.profile.get("Marital Status"),
        "income": st.session_state.profile.get("Income"),
        "state": st.session_state.profile.get("State"),
        "occupation": st.session_state.profile.get("Occupation"),
        "age": st.session_state.profile.get("Age"),
    }

def generate_documents_pdf(scheme):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.textColor = HexColor('#0d9488')
    title_style.alignment = 1 # Center
    
    heading_style = styles['Heading2']
    heading_style.textColor = HexColor('#0f172a')
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        leftIndent=20,
        bulletIndent=10
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#64748b'),
        alignment=1
    )
    
    story = []
    
    # App Name
    story.append(Paragraph("Adhikaar", title_style))
    story.append(Spacer(1, 12))
    
    # Scheme Name
    scheme_name = scheme.get('scheme_name', 'Unknown Scheme')
    story.append(Paragraph(f"<b>Scheme:</b> {scheme_name}", heading_style))
    story.append(Spacer(1, 12))
    
    # Match Percentage
    match_score = scheme.get('match_score')
    if match_score is not None:
        story.append(Paragraph(f"<b>Match Percentage:</b> {match_score}%", normal_style))
        story.append(Spacer(1, 12))
    
    # Section Title
    story.append(Paragraph("Required Documents", heading_style))
    story.append(Spacer(1, 12))
    
    # Bullet list of documents
    docs = scheme.get('required_documents', [])
    if docs:
        list_items = [ListItem(Paragraph(translate_explanation(doc), bullet_style)) for doc in docs]
        story.append(ListFlowable(list_items, bulletType='bullet', start='circle'))
    else:
        story.append(Paragraph("No specific documents listed. Please check official portal.", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Date generated
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Date generated: {current_date}", normal_style))
    story.append(Spacer(1, 12))
    
    # Footer
    story.append(Paragraph("Generated by Adhikaar Eligibility Engine", footer_style))
    
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def render_home():
    st.markdown(f"<h1 class='main-header'>{t('app_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{t('app_subtitle')}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><span class='trust-text'>{t('app_trust')}</span></p>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("btn_english"), use_container_width=True, type="primary" if st.session_state.language == "English" else "secondary"):
            st.session_state.language = "English"
            st.session_state.output_language = "en"
            st.rerun()
    with col2:
        if st.button(t("btn_tamil"), use_container_width=True, type="primary" if st.session_state.language == "தமிழ்" else "secondary"):
            st.session_state.language = "தமிழ்"
            st.session_state.output_language = "ta"
            st.rerun()
    with col3:
        if st.button(t("btn_hinglish"), use_container_width=True, type="primary" if st.session_state.language == "Hinglish" else "secondary"):
            st.session_state.language = "Hinglish"
            st.session_state.output_language = "en"
            st.rerun()
    st.write("")
    st.write("")
    col_main1, col_main2 = st.columns([1, 1])
    with col_main1:
        if st.button(t("btn_check_eligibility"), type="primary", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col_main2:
        if st.button(t("btn_browse_schemes"), use_container_width=True):
            st.session_state.step = 'browse'
            st.rerun()
    st.write("")
    st.markdown(f"<p style='text-align: center; color: #0d9488; font-size: 1rem; font-weight: 600; background: #ccfbf1; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 0 auto 2rem auto;'>{t('voice_enabled')}</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #1e293b; margin-bottom: 2rem; font-weight: 700;'>{t('how_it_works')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="premium-card">
        <h4><span style='font-size: 1.8rem; margin-right: 16px; background: #f1f5f9; border-radius: 12px; padding: 4px 8px;'>1️⃣</span> {t('step1_title')}</h4>
        <p style="color: #475569; margin-top: 12px; font-size: 1rem; line-height: 1.6; margin-left: 60px;">{t('step1_desc')}</p>
    </div>
    <div class="premium-card">
        <h4><span style='font-size: 1.8rem; margin-right: 16px; background: #f1f5f9; border-radius: 12px; padding: 4px 8px;'>2️⃣</span> {t('step2_title')}</h4>
        <p style="color: #475569; margin-top: 12px; font-size: 1rem; line-height: 1.6; margin-left: 60px;">{t('step2_desc')}</p>
    </div>
    <div class="premium-card">
        <h4><span style='font-size: 1.8rem; margin-right: 16px; background: #f1f5f9; border-radius: 12px; padding: 4px 8px;'>3️⃣</span> {t('step3_title')}</h4>
        <p style="color: #475569; margin-top: 12px; font-size: 1rem; line-height: 1.6; margin-left: 60px;">{t('step3_desc')}</p>
    </div>
    """, unsafe_allow_html=True)

def render_input():
    if st.button(t("btn_back")):
        st.session_state.step = 1
        st.rerun()
    st.markdown(f"<h2 style='color: #0f172a; font-weight: 800; margin-bottom: 0.5rem;'>{t('input_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #475569; font-size: 1.1rem; margin-bottom: 1.5rem;'>{t('input_desc')}</p>", unsafe_allow_html=True)
    current_lang = "ta-IN" if st.session_state.language == "தமிழ்" else "hi-IN" if st.session_state.language == "Hinglish" else "en-US"
    
    voice_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; background: transparent; }}
            .voice-container {{
                display: flex; align-items: center; gap: 16px;
                background: white; padding: 16px 20px; border-radius: 16px;
                border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            }}
            .mic-btn {{
                background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
                color: white; border: none; border-radius: 12px;
                padding: 12px 24px; cursor: pointer; font-weight: 700;
                font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px;
                transition: all 0.25s ease; box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.3);
            }}
            .mic-btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 12px -1px rgba(13, 148, 136, 0.4); }}
            select {{
                padding: 12px 16px; border-radius: 12px; border: 1px solid #cbd5e1;
                font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px; font-weight: 500; outline: none;
                transition: border-color 0.2s; background: white; color: #1e293b;
            }}
            select:focus {{ border-color: #0d9488; box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15); }}
            #status {{ font-size: 15px; color: #64748b; font-weight: 600; }}
            .pulse {{ animation: pulse-animation 1.5s infinite; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
            @keyframes pulse-animation {{
                0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="voice-container">
            <select id="lang">
                <option value="en-US" {'selected' if current_lang == 'en-US' else ''}>English (US)</option>
                <option value="ta-IN" {'selected' if current_lang == 'ta-IN' else ''}>தமிழ் (Tamil)</option>
                <option value="hi-IN" {'selected' if current_lang == 'hi-IN' else ''}>हिन्दी (Hindi)</option>
            </select>
            <button id="mic-btn" class="mic-btn">🎙️ Voice Input</button>
            <span id="status"></span>
        </div>
        <script>
            const btn = document.getElementById('mic-btn');
            const status = document.getElementById('status');
            const langSelect = document.getElementById('lang');
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                btn.onclick = () => {{
                    recognition.lang = langSelect.value;
                    recognition.start();
                    status.innerText = "Listening...";
                    btn.innerText = "🛑 Stop";
                    btn.classList.add("pulse");
                }};
                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    const lang = recognition.lang;
                    let langName = "English";
                    if(lang === "ta-IN") langName = "Tamil";
                    if(lang === "hi-IN") langName = "Hindi";
                    status.innerText = langName + " recognized! Updating...";
                    
                    try {{
                        const textAreas = window.parent.document.querySelectorAll('textarea');
                        if (textAreas.length > 0) {{
                            const textArea = textAreas[0];
                            const currentValue = textArea.value;
                            const newValue = currentValue ? currentValue + " " + transcript : transcript;
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                            nativeInputValueSetter.call(textArea, newValue);
                            const inputEvent = new Event('input', {{ bubbles: true }});
                            textArea.dispatchEvent(inputEvent);
                            setTimeout(() => {{ status.innerText = "Done!"; }}, 1500);
                        }} else {{
                            status.innerText = "Error: Textbox not found.";
                        }}
                    }} catch (e) {{
                        status.innerText = "Error updating text.";
                    }}
                }};
                recognition.onerror = (event) => {{
                    if(event.error === 'not-allowed') {{
                        status.innerText = "Microphone permission denied.";
                    }} else {{
                        status.innerText = "Error: " + event.error;
                    }}
                    btn.innerText = "🎙️ Voice Input";
                    btn.classList.remove("pulse");
                }};
                recognition.onend = () => {{
                    if (status.innerText === "Listening...") {{
                        status.innerText = "";
                    }}
                    btn.innerText = "🎙️ Voice Input";
                    btn.classList.remove("pulse");
                }};
            }} else {{
                btn.disabled = true;
                status.innerText = "Voice input not supported in this browser.";
                status.style.color = "red";
            }}
        </script>
    </body>
    </html>
    """
    components.html(voice_html, height=90)
    st.write("")
    
    st.session_state.user_input = st.text_area(
        "Your details",
        value=st.session_state.user_input,
        height=180,
        placeholder='e.g. "I am a widow, income 1 lakh, living in Bihar"',
        label_visibility="collapsed"
    )
    
    if st.session_state.language == "தமிழ்":
        use_transliteration = st.checkbox("Type Tamil using English letters", value=False)
    else:
        use_transliteration = False
    
    # Auto-detect language
    if st.session_state.user_input:
        st.session_state.output_language = detect_output_language(st.session_state.user_input)
        
    st.markdown(f"<p style='font-size: 0.95rem; color: #64748b; font-weight: 600; margin-bottom: 0.5rem;'>{t('quick_tags')}</p>", unsafe_allow_html=True)
    chip_cols = st.columns(4)
    chips = t("lbl_chips")
    for i, chip in enumerate(chips):
        with chip_cols[i % 4]:
            if st.button(chip, key=f"chip_{chip}", use_container_width=True):
                st.session_state.user_input = (st.session_state.user_input + " " + chip).strip()
                st.rerun()
    st.write("")
    st.write("")
    if st.button(t("btn_continue"), type="primary", use_container_width=True):
        if st.session_state.user_input.strip() == "":
            st.warning(t("warn_empty_input"))
        else:
            if use_transliteration:
                st.session_state.user_input = transliterate_to_tamil(st.session_state.user_input)
                st.session_state.output_language = detect_output_language(st.session_state.user_input)

            raw_profile = build_profile(st.session_state.user_input, st.session_state.language)
            
            gender_map = {"female": "Female", "male": "Male"}
            st.session_state.profile["Gender"] = gender_map.get(raw_profile.get("gender"))
            
            occ_map = {"unemployed": "Unemployed", "farmer": "Farmer", "student": "Student", "employed": "Employed", "business": "Business"}
            st.session_state.profile["Occupation"] = occ_map.get(raw_profile.get("occupation"))
            
            mar_map = {"widowed": "Widow", "unmarried": "Single", "married": "Married", "divorced": "Divorced"}
            st.session_state.profile["Marital Status"] = mar_map.get(raw_profile.get("marital_status"))
            
            state_map = {"bihar": "Bihar", "maharashtra": "Maharashtra", "tamil nadu": "Tamil Nadu", "uttar pradesh": "Uttar Pradesh"}
            state_val = raw_profile.get("state")
            st.session_state.profile["State"] = state_map.get(state_val, "Other") if state_val else None
            
            st.session_state.profile["Income"] = str(raw_profile.get("income")) if raw_profile.get("income") is not None else ""
            st.session_state.profile["Age"] = str(raw_profile.get("age")) if raw_profile.get("age") is not None else ""
            
            st.session_state.step = 3
            st.rerun()

def render_processing():
    st.markdown(f"<h2 style='color: #0f172a; font-weight: 800; margin-bottom: 1.5rem;'>{t('review_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stepper">
        <span style="color: #10b981;">{t('stepper_1')}</span>
        <span style="color: #10b981;">{t('stepper_2')}</span>
        <span class="stepper-active">{t('stepper_3')}</span>
        <span>{t('stepper_4')}</span>
    </div>
    """, unsafe_allow_html=True)
    st.info(t('review_info'))
    with st.container():
        st.markdown("<div class='premium-card' style='padding-top: 1rem;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            gender_opts = ["Female", "Male", "Other"]
            g_val = st.session_state.profile.get("Gender")
            g_idx = gender_opts.index(g_val) if g_val in gender_opts else None
            # Show translated options but map back to English keys internally
            disp_gender_opts = [t_data(g) for g in gender_opts]
            disp_g_val = t_data(g_val) if g_val else None
            disp_g_idx = disp_gender_opts.index(disp_g_val) if disp_g_val in disp_gender_opts else None
            selected_disp_g = st.selectbox(t('lbl_gender'), disp_gender_opts, index=disp_g_idx)
            if selected_disp_g:
                st.session_state.profile["Gender"] = gender_opts[disp_gender_opts.index(selected_disp_g)]
            
            st.session_state.profile["Income"] = st.text_input(t('lbl_income'), value=st.session_state.profile.get("Income", ""))
            
            occ_opts = ["Unemployed", "Farmer", "Student", "Employed", "Business"]
            o_val = st.session_state.profile.get("Occupation")
            disp_occ_opts = [t_data(o) for o in occ_opts]
            disp_o_val = t_data(o_val) if o_val else None
            disp_o_idx = disp_occ_opts.index(disp_o_val) if disp_o_val in disp_occ_opts else None
            selected_disp_o = st.selectbox(t('lbl_occupation'), disp_occ_opts, index=disp_o_idx)
            if selected_disp_o:
                st.session_state.profile["Occupation"] = occ_opts[disp_occ_opts.index(selected_disp_o)]
        with col2:
            mar_opts = ["Widow", "Single", "Married", "Divorced"]
            m_val = st.session_state.profile.get("Marital Status")
            disp_mar_opts = [t_data(m) for m in mar_opts]
            disp_m_val = t_data(m_val) if m_val else None
            disp_m_idx = disp_mar_opts.index(disp_m_val) if disp_m_val in disp_mar_opts else None
            selected_disp_m = st.selectbox(t('lbl_marital'), disp_mar_opts, index=disp_m_idx)
            if selected_disp_m:
                st.session_state.profile["Marital Status"] = mar_opts[disp_mar_opts.index(selected_disp_m)]
            
            state_opts = ["Bihar", "Maharashtra", "Tamil Nadu", "Uttar Pradesh", "Other"]
            s_val = st.session_state.profile.get("State")
            disp_state_opts = [t_data(s) for s in state_opts]
            disp_s_val = t_data(s_val) if s_val else None
            disp_s_idx = disp_state_opts.index(disp_s_val) if disp_s_val in disp_state_opts else None
            selected_disp_s = st.selectbox(t('lbl_state'), disp_state_opts, index=disp_s_idx)
            if selected_disp_s:
                st.session_state.profile["State"] = state_opts[disp_state_opts.index(selected_disp_s)]
            
            st.session_state.profile["Age"] = st.text_input(t('lbl_age'), value=st.session_state.profile.get("Age", ""))
        st.write("---")
        st.markdown(f"**{t('meta_title')}**")
        st.markdown(f"• {t('meta_lang')} **{st.session_state.language}**")
        inc_val = st.session_state.profile.get("Income", "")
        if inc_val:
            st.markdown(f"• {t('meta_income')} **₹{str(inc_val).replace(',', '')}**")
        else:
            st.markdown(f"• {t('meta_income')} **{t('not_provided')}**")
        st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(t("btn_edit_input"), use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button(t("btn_check_eligibility"), type="primary", use_container_width=True):
            with st.spinner(t("analyzing")):
                time.sleep(1.0)
                backend_profile = build_backend_profile()
                normalized_profile = normalize_profile(backend_profile)
                schemes_data = load_schemes_data()
                results = get_top_matches(normalized_profile, schemes_data, top_n=5)
                st.session_state.results = results
                st.session_state.selected_scheme = results[0] if results else None
                st.session_state.step = 4
                st.rerun()

def render_results():
    col1, col2 = st.columns([3, 1])
    with col1:
        total = len(st.session_state.results)
        st.markdown(f"<h2 style='color: #0f172a; font-weight: 800;'>{total} {t('schemes_found')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; margin-top: -10px;'>{t('based_on_profile')}</p>", unsafe_allow_html=True)
    with col2:
        if st.button(t("btn_start_over"), use_container_width=True):
            st.session_state.step = 1
            st.session_state.user_input = ""
            st.session_state.results = []
            st.session_state.selected_scheme = None
            st.rerun()
    
    st.write("---")
    if not st.session_state.results:
        st.warning(t("warn_no_schemes"))
        return
    for i, scheme in enumerate(st.session_state.results):
        raw_status = scheme.get("match_status", "No Match")
        status_key = "status_" + raw_status.lower().replace(" ", "_")
        status = t(status_key)
        
        score = scheme.get("match_score", 0)
        badge_class = "badge-eligible" if raw_status == "Full Match" else "badge-partial"
        
        raw_why_matched = scheme.get("why_matched", [])
        raw_why_not_matched = scheme.get("why_not_matched", [])
        
        matched_list = [translate_explanation(x) for x in raw_why_matched]
        not_matched_list = [translate_explanation(x) for x in raw_why_not_matched]
        
        reasons_matched = "<br>".join([f"✓ {x}" for x in matched_list]) or t("reason_no_pos")
        reasons_not = "<br>".join([f"✗ {x}" for x in not_matched_list]) or t("reason_no_neg")
        
        req_docs_text = ", ".join([translate_explanation(x) for x in scheme.get('required_documents', [])])
        
        st.markdown(f"""
        <div class="scheme-card">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <span class="{badge_class}">{status}</span>
                <span style="color:#0f766e; font-weight:800; font-size:0.9rem; background:#ccfbf1; padding:6px 14px; border-radius:16px; border:1px solid #99f6e4;">{t('match')} {score}%</span>
            </div>
            <h3 style="margin-top:0.5rem; color:#0f172a; font-weight:800;">{scheme.get('scheme_name', '')}</h3>
            <p style="color:#475569; line-height:1.6; font-size:1.05rem;"><strong>{t('category')}</strong> {translate_explanation(scheme.get('category', ''))}</p>
            <p style="color:#475569; line-height:1.6; font-size:1.05rem;"><strong>{t('why_matched')}</strong><br>{reasons_matched}</p>
            <p style="color:#b45309; line-height:1.6; background:#fffbeb; padding:12px 16px; border-radius:12px; border-left:4px solid #f59e0b; font-weight:500;"><strong>{t('why_not_matched')}</strong><br>{reasons_not}</p>
            <div style="background:#f8fafc; padding:12px 16px; border-radius:12px; margin-top:1rem;">
                <p style="color:#334155; line-height:1.5; margin-bottom:0;"><strong>{t('req_docs')}</strong> {req_docs_text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        with btn_col1:
            if st.button(t("btn_view_details"), key=f"view_{i}", type="primary", use_container_width=True):
                st.session_state.selected_scheme = scheme
                st.session_state.step = 5
                st.rerun()
        with btn_col2:
            st.button(t("btn_save_later"), key=f"save_{i}", use_container_width=True)
        with btn_col3:
            st.link_button(t("btn_apply"), scheme.get("official_apply_link", "#"), use_container_width=True)
        with btn_col4:
            pdf_bytes = generate_documents_pdf(scheme)
            safe_scheme_name = scheme.get('scheme_name', 'scheme').replace(' ', '_').lower()
            st.download_button(
                label="📄 Download Docs",
                data=pdf_bytes,
                file_name=f"{safe_scheme_name}_documents.pdf",
                mime="application/pdf",
                key=f"dl_{i}",
                use_container_width=True
            )
        st.write("")

def render_detail():
    scheme = st.session_state.get("selected_scheme")
    if not scheme:
        st.warning(t("warn_no_schemes"))
        return
    if st.button(t("btn_back_results")):
        st.session_state.step = 4
        st.rerun()
        
    raw_status = scheme.get("match_status", "No Match")
    status_key = "status_" + raw_status.lower().replace(" ", "_")
    status = t(status_key)
        
    st.markdown(f"<h2 style='color:#0f172a; font-weight:800; margin-bottom:0.5rem;'>{scheme.get('scheme_name', '')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<span class='badge-eligible' style='margin-bottom:2rem;'>{status} - {scheme.get('match_score', 0)}% Match</span>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1.2])
    with col1:
        st.markdown(f"<h3 style='color:#1e293b; font-weight:700;'>{t('overview')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#475569; font-size:1.1rem; line-height:1.6;'>{translate_explanation(scheme.get('benefit_summary', ''))}</p>", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"<h3 style='color:#1e293b; font-weight:700;'>{t('who_can_apply')}</h3>", unsafe_allow_html=True)
        
        matched_list = [translate_explanation(x) for x in scheme.get("why_matched", [])]
        not_matched_list = [translate_explanation(x) for x in scheme.get("why_not_matched", [])]
        
        matched = "<br>".join([f"• {x}" for x in matched_list]) or t("reason_no_pos")
        not_matched = "<br>".join([f"• {x}" for x in not_matched_list]) or t("reason_no_neg")
        
        st.markdown(f"<p style='color:#475569; line-height:1.7;'><strong>{t('matched')}</strong><br>{matched}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#b45309; line-height:1.7;'><strong>{t('not_matched')}</strong><br>{not_matched}</p>", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"<h3 style='color:#1e293b; font-weight:700;'>{t('how_to_apply')}</h3>", unsafe_allow_html=True)
        st.markdown("<ol style='color:#475569; font-size:1.05rem; line-height:1.8;'>" + "".join([f"<li>{translate_explanation(step)}</li>" for step in scheme.get("application_steps", [])]) + "</ol>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="premium-card" style="background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%); border: 1px solid #bbf7d0; box-shadow: 0 10px 25px -5px rgba(22, 101, 52, 0.05);">
            <h4 style="color: #166534;"><span style="font-size: 1.4rem; margin-right: 12px;">📁</span> {t('docs_required')}</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<ul style='color:#166534; font-size:1rem; line-height:1.8; margin-top:16px; font-weight:500;'>" + "".join([f"<li>{translate_explanation(doc)}</li>" for doc in scheme.get("required_documents", [])]) + "</ul>", unsafe_allow_html=True)
        st.link_button(t("btn_apply"), scheme.get("official_apply_link", "#"), use_container_width=True)
        st.write("")
        
        pdf_bytes = generate_documents_pdf(scheme)
        safe_scheme_name = scheme.get('scheme_name', 'scheme').replace(' ', '_').lower()
        st.download_button(
            label="📄 Download Docs",
            data=pdf_bytes,
            file_name=f"{safe_scheme_name}_documents.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.write("")
        
        if "show_map" not in st.session_state:
            st.session_state.show_map = False

        if st.button(t("btn_find_center"), type="primary", use_container_width=True):
            st.session_state.show_map = not st.session_state.show_map

        if st.session_state.show_map:
            st.markdown("---")
            st.markdown("#### 📍 Find Nearest Center")
            loc_option = st.selectbox("How would you like to set your location?", ["Use Current Location", "Enter City Manually"])
            
            user_loc = ""
            if loc_option == "Use Current Location":
                with st.spinner("Detecting location..."):
                    try:
                        res = requests.get("https://ipinfo.io/json", timeout=3).json()
                        city = res.get("city", "")
                        region = res.get("region", "")
                        if city or region:
                            user_loc = f"{city}, {region}".strip(", ")
                            st.success(f"Detected location: **{user_loc}**")
                        else:
                            st.warning("Could not automatically detect location. Please enter manually.")
                            user_loc = st.text_input("Enter City / District / Pincode:")
                    except Exception:
                        st.warning("Could not automatically detect location. Please enter manually.")
                        user_loc = st.text_input("Enter City / District / Pincode:")
            else:
                user_loc = st.text_input("Enter City / District / Pincode:")
                
            if user_loc:
                cat = scheme.get('category', '').lower()
                center_type = "Government Service Center"
                if "widow" in cat or "pension" in cat:
                    center_type = "Social Welfare Office"
                elif "housing" in cat or "home" in cat:
                    center_type = "Municipality Office"
                elif "farmer" in cat or "agriculture" in cat:
                    center_type = "Agriculture Office"
                elif "student" in cat or "education" in cat or "scholarship" in cat:
                    center_type = "Education Office"
                elif "employment" in cat or "job" in cat:
                    center_type = "Employment Exchange Office"
                elif "health" in cat or "medical" in cat:
                    center_type = "Government Hospital"
                    
                import urllib.parse
                query = f"{center_type} near {user_loc}"
                maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
                
                st.markdown(f"""
                <div style="background-color: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 1rem;">
                    <p style="margin: 0 0 8px 0; color: #334155;"><strong>🏢 Center Type:</strong> {center_type}</p>
                    <p style="margin: 0 0 8px 0; color: #334155;"><strong>📍 Search Area:</strong> {user_loc}</p>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;"><em>Distance & exact address available on Google Maps</em></p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                st.link_button("🗺️ Open in Google Maps", maps_url, use_container_width=True)

def render_no_match():
    st.write("")
    st.write("")
    st.markdown("<div style='text-align: center; padding: 2rem 0; animation: float 4s ease-in-out infinite;'>", unsafe_allow_html=True)
    st.markdown("<span style='font-size: 6rem; display: inline-block; filter: drop-shadow(0 10px 8px rgb(0 0 0 / 0.04));'>🔍</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: #0f172a; margin-top: 0; font-weight: 800;'>{t('no_match_title')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 1.15rem; max-width: 600px; margin: 1rem auto 2rem auto; line-height: 1.6;'>{t('no_match_desc')}</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="premium-card" style="max-width: 700px; margin: 0 auto;">
        <h4 style="margin-bottom: 1rem;">{t('suggestions_title')}</h4>
        <ul style="color: #475569; font-size: 1.05rem; line-height: 1.8; margin-bottom: 0;">
            <li>{t('sugg_1')}</li>
            <li>{t('sugg_2')}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(t("btn_edit_details"), type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        with col_btn2:
            if st.button(t("btn_browse_all"), use_container_width=True):
                st.session_state.step = 'browse'
                st.rerun()

def generate_audio_bytes(text, user_lang):
    try:
        # Map user language choice to gTTS language code
        # Hinglish gets 'hi', Tamil gets 'ta', default 'en'
        tts_lang = 'ta' if user_lang == 'ta' else ('hi' if st.session_state.language == 'Hinglish' else 'en')
        tts = gTTS(text=text, lang=tts_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"Audio generation failed: {e}")
        return None

def render_browse():
    st.markdown("<h2 class='main-header'>Browse Schemes</h2>", unsafe_allow_html=True)
    if st.button(t("btn_back")):
        st.session_state.step = 1
        st.rerun()
        
    st.markdown("<p style='color: #475569; font-size: 1.1rem;'>Search the official database using keywords or sentences.</p>", unsafe_allow_html=True)
    
    search_query = st.text_input("Search Schemes", placeholder="e.g., widow pension, housing, farmer...", label_visibility="collapsed")
    
    if st.button("Search", type="primary"):
        schemes_data = load_schemes_data()
        st.session_state.browse_results = search_schemes(search_query, schemes_data)
        
    if "browse_results" in st.session_state:
        results = st.session_state.browse_results
        if not results:
            st.warning("No schemes found. Try different keywords.")
        else:
            st.success(f"Found {len(results)} matching scheme(s).")
            for scheme in results:
                details = format_scheme_details(scheme)
                with st.expander(f"📌 {details['name']}"):
                    st.markdown(f"**Category:** {details['category']}")
                    # If Tamil selected, try to show translation from logic/app
                    eligibility_text = translate_explanation(details['eligibility'])
                    benefits_text = translate_explanation(details['benefits'])
                    
                    st.markdown(f"**Eligibility:** {eligibility_text}")
                    st.markdown(f"**Benefits:** {benefits_text}")
                    st.markdown(f"**Application Steps:** {translate_explanation(details['application_steps'])}")
                    st.markdown(f"**Required Documents:** {translate_explanation(details['documents'])}")
                    st.markdown(f"[🔗 Official Source / Apply Link]({details['source_url']})")
                    
                    st.write("---")
                    st.write("🎧 **Listen to scheme details**")
                    if st.button("🔊 Play Audio", key=f"audio_{scheme['scheme_name']}"):
                        with st.spinner("Generating audio..."):
                            speech_text = generate_speech_text(details)
                            final_speech_text = translate_explanation(speech_text) if st.session_state.output_language == 'ta' else speech_text
                            audio_bytes = generate_audio_bytes(final_speech_text, st.session_state.output_language)
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/mp3')

def main():
    setup_page()
    init_session()
    if st.session_state.step == 1:
        render_home()
    elif st.session_state.step == 'browse':
        render_browse()
    elif st.session_state.step == 2:
        render_input()
    elif st.session_state.step == 3:
        render_processing()
    elif st.session_state.step == 4:
        render_results()
    elif st.session_state.step == 5:
        render_detail()
    elif st.session_state.step == 6:
        render_no_match()

if __name__ == "__main__":
    main()