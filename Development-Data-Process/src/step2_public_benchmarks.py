import os
import io
import re
import time
import zipfile
import urllib.request
import warnings
import joblib
import numpy as np
import pandas as pd
import m2cgen as m2c

from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "datasets")
TEMP_DIR = os.path.join(BASE_DIR, "temp_bench")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Print contents of datasets folder and datasets links.txt if present
links_file = os.path.join(DATA_DIR, "datasets links.txt")
if os.path.exists(links_file):
    print("=== Contents of datasets/datasets links.txt ===")
    with open(links_file, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read())
    print("===============================================")

# Exact PhishShield 11 URL feature extractor (matching feature_extractor.js)
SHORTENERS = [
    "bit.ly", "goo.gl", "shorte.st", "go2l.ink", "x.co", "ow.ly", "t.co",
    "tinyurl", "tr.im", "is.gd", "cli.gs", "yfrog.com", "migre.me", "ff.im",
    "tiny.cc", "url4.eu", "twit.ac", "su.pr", "twurl.nl", "snipurl.com",
    "short.to", "budurl.com", "ping.fm", "post.ly", "just.as", "bkite.com",
    "snipr.com", "fic.kr", "loopt.us", "doiop.com", "short.ie", "kl.am",
    "wp.me", "rubyurl.com", "om.ly", "to.ly", "bit.do", "lnkd.in", "db.tt",
    "qr.ae", "adf.ly", "cur.lv", "ity.im", "q.gs", "po.st", "bc.vc",
    "twitthis.com", "u.to", "j.mp", "buzurl.com", "cutt.us", "u.bb",
    "yourls.org", "prettylinkpro.com", "scrnch.me", "filoops.info",
    "vzturl.com", "qr.net", "1url.com", "tweez.me", "v.gd", "link.zip.net"
]
COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "uk", "us", "ca",
    "au", "de", "fr", "it", "jp", "io", "co", "ai"
}
IP_REGEX = re.compile(
    r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

def extract_ps_11_url_features(urls):
    rows = []
    for u in urls:
        u_str = str(u).strip()
        try:
            parsed = urlparse(u_str if "://" in u_str else "http://" + u_str)
            domain = (parsed.hostname or "").lower()
        except Exception:
            domain = ""

        f1 = 1 if IP_REGEX.match(domain) else 0
        f2 = 1 if len(u_str) > 75 else 0
        f3 = 1 if any(s in domain for s in SHORTENERS) else 0
        f4 = 1 if "@" in u_str else 0
        f5 = 1 if u_str.rfind("//") > 7 else 0
        f6 = 1 if "-" in domain else 0

        parts = [p for p in domain.split(".") if p and p != "www"]
        f7 = 1 if len(parts) > 3 else 0
        f8 = domain.count("-")
        clean_dom = domain[4:] if domain.startswith("www.") else domain
        f9 = clean_dom.count(".")
        f10 = sum(c.isdigit() for c in domain)
        suffix = parts[-1] if parts else ""
        f11 = 0 if suffix in COMMON_TLDS else 1

        rows.append([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11])
    cols = [
        "having_IP", "URL_Length", "Shortining_Service", "having_At_Symbol",
        "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain",
        "Hyphen_Count", "Dot_Count", "Numeric_Chars", "Is_Common_TLD"
    ]
    return pd.DataFrame(rows, columns=cols)

# Gupta et al. (2021) 9 lexical features for ISCX-URL-2016 comparison
def extract_gupta_9_lexical(urls):
    rows = []
    for u in urls:
        u_str = str(u).strip()
        try:
            parsed = urlparse(u_str if "://" in u_str else "http://" + u_str)
            domain = (parsed.hostname or "").lower()
            path = parsed.path or ""
            query = parsed.query or ""
        except Exception:
            domain, path, query = "", "", ""
        url_len = len(u_str)
        dom_len = len(domain)
        path_len = len(path)
        num_dots = u_str.count(".")
        num_hyphens = u_str.count("-")
        num_slashes = u_str.count("/")
        num_digits = sum(c.isdigit() for c in u_str)
        num_query = len(query.split("&")) if query else 0
        has_https = 1 if u_str.lower().startswith("https") else 0
        rows.append([
            url_len, dom_len, path_len, num_dots, num_hyphens,
            num_slashes, num_digits, num_query, has_https
        ])
    cols = [
        "url_len", "dom_len", "path_len", "num_dots", "num_hyphens",
        "num_slashes", "num_digits", "num_query", "has_https"
    ]
    return pd.DataFrame(rows, columns=cols)

def run_models_on_split(X_train, X_test, y_train, y_test, title):
    print(f"\n==================== {title} ====================")
    print(f"Train: {len(X_train)} | Test: {len(X_test)} | Features: {X_train.shape[1]}")
    models = [
        ("RF Light (n=20, d=10)", RandomForestClassifier(n_estimators=20, max_depth=10, n_jobs=-1, random_state=42), True),
        ("RF Golden (n=100, d=10, leaf=15)", RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=15, max_features="sqrt", n_jobs=-1, random_state=42), True),
        ("RF Heavy (n=100, d=20)", RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42), True),
        ("XGBoost (n=100, d=10)", XGBClassifier(n_estimators=100, max_depth=10, eval_metric="logloss", n_jobs=-1, random_state=42), False),
        ("Gradient Boosting (n=100, d=5)", GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42), False),
        ("Extra Trees (n=100, d=10)", ExtraTreesClassifier(n_estimators=100, max_depth=10, n_jobs=-1, random_state=42), True),
        ("Decision Tree (d=10)", DecisionTreeClassifier(max_depth=10, random_state=42), True),
        ("MLP Neural Net (64-32-1)", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=30, random_state=42), False),
    ]
    hdr = f"{'MODEL':<34} | {'ACC%':<6} | {'PREC%':<6} | {'REC%':<6} | {'F1%':<6} | {'ROC-AUC':<7} | {'FPR%':<5} | {'PY(KB)':<7} | {'JS(KB)':<8}"
    print(hdr)
    print("-" * len(hdr))
    for name, clf, do_js in models:
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]
        acc = accuracy_score(y_test, y_pred) * 100
        prec = precision_score(y_test, y_pred, zero_division=0) * 100
        rec = recall_score(y_test, y_pred, zero_division=0) * 100
        f1 = f1_score(y_test, y_pred, zero_division=0) * 100
        roc = roc_auc_score(y_test, y_prob)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0

        jb_path = os.path.join(TEMP_DIR, "m.joblib")
        joblib.dump(clf, jb_path)
        py_kb = os.path.getsize(jb_path) / 1024.0
        os.remove(jb_path)

        js_str = "N/A"
        if do_js:
            try:
                js_code = m2c.export_to_javascript(clf, function_name="scoreModel")
                js_kb = len(js_code.encode("utf-8")) / 1024.0
                js_str = f"{js_kb:.1f}"
            except Exception:
                js_str = "Err"

        print(f"{name:<34} | {acc:6.2f} | {prec:6.2f} | {rec:6.2f} | {f1:6.2f} | {roc:7.4f} | {fpr:5.2f} | {py_kb:7.1f} | {js_str:<8}")

# ==============================================================================
# PART 1: PhiUSIIL BENCHMARK (235,795 URLs)
# ==============================================================================
phi_csv = os.path.join(DATA_DIR, "PhiUSIIL_Phishing_URL_Dataset.csv")
if not os.path.exists(phi_csv):
    print("\nDownloading PhiUSIIL Phishing URL Dataset from UCI Repository (ID 967)...")
    uci_zip_url = "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"
    req = urllib.request.Request(uci_zip_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        zbytes = resp.read()
    with zipfile.ZipFile(io.BytesIO(zbytes)) as zf:
        for member in zf.namelist():
            if member.endswith(".csv"):
                zf.extract(member, DATA_DIR)
                extracted_path = os.path.join(DATA_DIR, member)
                if extracted_path != phi_csv:
                    os.replace(extracted_path, phi_csv)
    print(f"Saved PhiUSIIL dataset to: {phi_csv}")

print(f"\nLoading PhiUSIIL dataset from {phi_csv}...")
df_phi = pd.read_csv(phi_csv)
print(f"PhiUSIIL shape: {df_phi.shape}")

# In PhiUSIIL, label 1 = Legitimate, 0 = Phishing. Invert so 1 = Phishing (matching PhishShield)
y_phi = (1 - df_phi["label"]).astype(int)
print(f"PhiUSIIL Phishing (1): {int((y_phi == 1).sum())} | Legitimate (0): {int((y_phi == 0).sum())}")

# Extract PhishShield 11 URL features across all 235,795 URLs
print("Extracting PhishShield 11 URL features on all 235,795 PhiUSIIL URLs...")
X_phi_ps11 = extract_ps_11_url_features(df_phi["URL"])

# Regime A: PhishShield 11 URL features on PhiUSIIL
X_tr, X_te, y_tr, y_te = train_test_split(X_phi_ps11, y_phi, test_size=0.2, random_state=42, stratify=y_phi)
run_models_on_split(X_tr, X_te, y_tr, y_te, "PhiUSIIL (N=235,795) - Regime A: PhishShield 11 URL Features")

# Regime B: PhishShield 16-Feature Local Browser Schema (11 URL + 5 local DOM features from PhiUSIIL)
X_phi_ps16 = X_phi_ps11.copy()
X_phi_ps16["SFH_proxy"] = ((df_phi["HasExternalFormSubmit"] == 1) | (df_phi["NoOfEmptyRef"] > 0)).astype(int)
X_phi_ps16["Submit_proxy"] = df_phi["HasSubmitButton"].astype(int)
X_phi_ps16["Popup_proxy"] = (df_phi["NoOfPopup"] > 0).astype(int)
X_phi_ps16["Pass_proxy"] = df_phi["HasPasswordField"].astype(int)
X_phi_ps16["Iframe"] = (df_phi["NoOfiFrame"] > 0).astype(int)

X_tr16, X_te16, y_tr16, y_te16 = train_test_split(X_phi_ps16, y_phi, test_size=0.2, random_state=42, stratify=y_phi)
run_models_on_split(X_tr16, X_te16, y_tr16, y_te16, "PhiUSIIL (N=235,795) - Regime B: 16-Feature Browser-Compatible Schema")

# Regime C: Full 50 Numeric Features of PhiUSIIL
drop_cols = [c for c in ["FILENAME", "URL", "Domain", "TLD", "Title", "label"] if c in df_phi.columns]
X_phi_full = df_phi.drop(columns=drop_cols)
X_tr50, X_te50, y_tr50, y_te50 = train_test_split(X_phi_full, y_phi, test_size=0.2, random_state=42, stratify=y_phi)
run_models_on_split(X_tr50, X_te50, y_tr50, y_te50, "PhiUSIIL (N=235,795) - Regime C: All 50 Native Numeric Features")

# ==============================================================================
# PART 2: ISCX-URL-2016 BENCHMARK / CROSS-CORPUS LEXICAL COMPARISON
# ==============================================================================
iscx_benign_url = "https://raw.githubusercontent.com/matf-ml/ml19-classifying-spam-urls/master/Benign_list_big_final.csv"
iscx_benign_path = os.path.join(DATA_DIR, "ISCX_Benign_list_big_final.csv")

try:
    if not os.path.exists(iscx_benign_path):
        print("\nDownloading ISCX-URL-2016 Benign URL corpus...")
        req = urllib.request.Request(iscx_benign_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(iscx_benign_path, "wb") as f:
                f.write(resp.read())

    benign_df = pd.read_csv(iscx_benign_path, header=None)
    benign_urls = benign_df.iloc[:, 0].dropna().astype(str).tolist()

    # Load verified PhishTank URLs from datasets/phishtank_urls.csv to pair with ISCX-URL-2016 Benign (following Gupta et al. 20,000-URL benchmark protocol)
    pt_path = os.path.join(DATA_DIR, "phishtank_urls.csv")
    if os.path.exists(pt_path):
        pt_df = pd.read_csv(pt_path)
        url_col = "url" if "url" in pt_df.columns else pt_df.columns[0]
        phish_urls = pt_df[url_col].dropna().astype(str).tolist()

        n_benign = min(11964, len(benign_urls))
        n_phish = min(7999, len(phish_urls))
        b_sample = pd.Series(benign_urls).sample(n=n_benign, random_state=42).tolist()
        p_sample = pd.Series(phish_urls).sample(n=n_phish, random_state=42).tolist()

        all_iscx_urls = b_sample + p_sample
        y_iscx = np.array([0] * n_benign + [1] * n_phish)

        print(f"\nBenchmarking on ISCX-URL-2016 Protocol Corpus (Total={len(all_iscx_urls)}: Benign={n_benign}, Phishing={n_phish})...")
        X_iscx_ps11 = extract_ps_11_url_features(all_iscx_urls)
        X_itr, X_ite, y_itr, y_ite = train_test_split(X_iscx_ps11, y_iscx, test_size=0.2, random_state=42, stratify=y_iscx)
        run_models_on_split(X_itr, X_ite, y_itr, y_ite, "ISCX-URL-2016 Benchmark - PhishShield 11 URL Features")

        X_iscx_gupta9 = extract_gupta_9_lexical(all_iscx_urls)
        X_gtr, X_gte, y_gtr, y_gte = train_test_split(X_iscx_gupta9, y_iscx, test_size=0.2, random_state=42, stratify=y_iscx)
        run_models_on_split(X_gtr, X_gte, y_gtr, y_gte, "ISCX-URL-2016 Benchmark - Gupta et al. (2021) 9 Lexical Features")
except Exception as e:
    print(f"ISCX benchmark step encountered an issue: {e}")

print("\nAll Step 2 benchmark evaluations completed!")