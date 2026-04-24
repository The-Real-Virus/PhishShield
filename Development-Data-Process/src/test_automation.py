import pandas as pd
import joblib
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from feature_extractor import extract_all_features
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# --- 1. Setup ---
BASE_DIR = os.getcwd()
MODEL_PATH = os.path.join(BASE_DIR, "models", "phishshield_rf.joblib")

# --- 2. The Universal Test Suite ---
test_urls = [
    # LEGITIMATE SITES (Should be SAFE)
    "https://www.google.com",
    "https://web.whatsapp.com",       
    "https://www.amazon.com",
    "https://grok.com",               
    "https://stackoverflow.com",      
    "https://github.com",
    "https://www.instagram.com",      
    "https://www.instagram.com/accounts/login/?hl=en",
    "https://gemini.google.com/app?",
    "https://www.netflix.com/browse",
    "https://openai.com/research/",
    "https://www.youtube.com/",
    "https://www.facebook.com/login.php",
    "https://www.facebook.com/",    
    
    # PHISHING SITES (Should be PHISHING)
    "http://82273v.com",              
    "http://trezor.la",               
    "https://secure-update-paypal-login.com", 
    "http://testsafebrowsing.appspot.com/s/phishing.html",
    "https://allegro.prytwanite5.sbs", 
    "https://ma.usa.codify.inc/",
    "https://www.web3vaultencrypt.com/wallets",
    "http://testsafebrowsing.appspot.com/s/phishing.html",
    "http://allegro.15s195j181-1s.sbs",
    "https://kra4.pro/",
    "https://allegro-lokalnie.oi383y3y.cfd",
    "https://iconeflow.com/",
    "https://promoairfryer.online/",
    "https://0xpr.top/usdc/?claim.circle.com",
    "http://bigtrout300.lol",
    "https://web3chatbot.com/",
    "http://www.alturasbuga.com/9muljx",
    "https://vivasorteoficial.com.ua/",
    "https://vivasortecapitalizacao.com/"
]

# --- 3. The Mega-Whitelist (Mirrors whitelist.js) ---
TRUSTED_DOMAINS = {
    'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'wikipedia.org', 
    'twitter.com', 'linkedin.com', 'instagram.com', 'netflix.com', 'microsoft.com', 
    'github.com', 'whatsapp.com', 'apple.com', 'yahoo.com', 'bing.com', 
    'live.com', 'office.com', 'twitch.tv', 'adobe.com', 'paypal.com', 
    'stackoverflow.com', 'reddit.com', 'tiktok.com', 'zoom.us', 'salesforce.com', 
    'canva.com', 'ebay.com', 'dropbox.com', 'openai.com', 'grok.com'
}

# --- 4. Load Model ---
print(f"Loading model from {MODEL_PATH}...")
try:
    model = joblib.load(MODEL_PATH)
except:
    print("Error: Model not found. Run src/deploy_rf_model.py first.")
    exit()

# --- 5. Phase 2: NLP Content Scanner (Python Equivalent) ---
def calculate_nlp_score(url):
    try:
        # Fetch page content with a short timeout
        response = requests.get(url, timeout=3)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text().lower()

        nlp_score = 0
        urgency_words = ['suspended', 'locked', 'banned', 'unauthorized', 'prevent', 'immediately', 'urgent', 'shutdown', 'deactivate']
        sensitive_words = ['password', 'credit card', 'social security', 'bank account', 'routing number', 'pin', 'verify identity']
        action_words = ['click here', 'login', 'sign in', 'update now', 'confirm', 'restore']

        has_urgency = any(w in text_content for w in urgency_words)
        has_sensitive = any(w in text_content for w in sensitive_words)
        has_action = any(w in text_content for w in action_words)

        if has_urgency and has_sensitive: nlp_score += 0.25
        if has_action and has_sensitive: nlp_score += 0.15
        if has_urgency and has_action: nlp_score += 0.15

        return nlp_score
    except Exception:
        # Fails silently if site is dead/offline, mirroring client-side behavior
        return 0.0

# --- 6. The Hybrid Logic Function ---
def get_hybrid_score(features, url, nlp_score):
    raw_score = model.predict_proba([features])[0][1]
    
    hyphen_count = features[7]
    numeric_chars = features[9]
    is_risky_tld = features[10]
    
    final_score = raw_score
    logic_applied = []

    # Rule A: High Entropy
    if numeric_chars >= 4:
        final_score += 0.45
        logic_applied.append("ENTROPY")

    # Rule B: Structure Imitation
    if hyphen_count > 1:
        final_score += 0.25 
        logic_applied.append("STRUCTURE")

    # Rule C: Low Reputation TLD
    if is_risky_tld == 1:
        final_score += 0.30 
        logic_applied.append("RISKY_TLD")

    # Rule D: Intent Keywords
    dangerous_words = ['login', 'verify', 'account', 'update', 'wallet', 'vault', 'secure', 'confirm', 'banking']
    if any(w in url.lower() for w in dangerous_words):
        final_score += 0.20
        logic_applied.append("INTENT_KEYWORD")

    # Phase 2: Apply NLP Score
    if nlp_score > 0:
        final_score += nlp_score
        logic_applied.append(f"NLP_SCAN(+{nlp_score:.2f})")

    # Clamp Score
    final_score = min(final_score, 1.0)

    # Rule E: Whitelist Safety Net
    try:
        domain = urlparse(url).netloc
        clean_domain = domain.replace("www.", "")
        is_trusted = False
        
        if clean_domain in TRUSTED_DOMAINS:
            is_trusted = True
        else:
            for trusted in TRUSTED_DOMAINS:
                if clean_domain.endswith("." + trusted):
                    is_trusted = True
                    break
        
        if is_trusted:
            final_score = 0.0
            logic_applied.append("WHITELISTED")
    except:
        pass

    return final_score, raw_score, logic_applied

# --- 7. Run Automation ---
print(f"\n{'URL':<45} | {'RAW':<5} | {'FINAL':<5} | {'RESULT':<10} | {'LOGIC USED'}")
print("-" * 125)

for url in test_urls:
    try:
        feats = extract_all_features(url)
        nlp_score = calculate_nlp_score(url) 
        final_score, raw_score, logic = get_hybrid_score(feats, url, nlp_score)
        
        result = "PHISHING" if final_score > 0.50 else "LEGIT"
        
        logic_str = ", ".join(logic) if logic else "ML_ONLY"
        
        print(f"{url[:45]:<45} | {raw_score:.2f}  | {final_score:.2f}  | {result:<10} | {logic_str}")
    except Exception as e:
        print(f"Error processing {url}: {e}")

print("-" * 125)