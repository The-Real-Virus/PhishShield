import os
import time
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

import tensorflow as tf
from tensorflow.keras import layers, models, Input

warnings.filterwarnings("ignore")
tf.random.set_seed(42)
np.random.seed(42)

BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, "processed_data", "realistic_dataset.csv")
PHI_PATH = os.path.join(BASE_DIR, "datasets", "PhiUSIIL_Phishing_URL_Dataset.csv")
TEMP_DIR = os.path.join(BASE_DIR, "temp_sota")
os.makedirs(TEMP_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
X = df.drop("class", axis=1).values.astype(np.float32)
y = df["class"].values.astype(int)
feature_names = list(df.drop("class", axis=1).columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==============================================================================
# PART 1: GREY WOLF OPTIMIZER (GWO) + RF (Dandotiya et al., 2026 SOTA Paradigm)
# ==============================================================================
print("Running Part 1: GWO-Optimized RF (Dandotiya et al., 2026 SOTA paradigm)...")

def run_gwo_rf(X_tr, y_tr, X_te, y_te, n_wolves=8, max_iter=8):
    rng = np.random.RandomState(42)
    dim = X_tr.shape[1] + 2  # 16 feature weights + n_estimators + max_depth
    positions = rng.uniform(0, 1, size=(n_wolves, dim))
    # Ensure at least one wolf starts with all features enabled
    positions[0, :X_tr.shape[1]] = 0.9

    alpha_pos, alpha_score = None, -1.0
    beta_pos, beta_score = None, -1.0
    delta_pos, delta_score = None, -1.0

    # Internal validation split from training set only (no test leakage)
    X_sub, X_val, y_sub, y_val = train_test_split(
        X_tr, y_tr, test_size=0.2, random_state=42
    )

    for it in range(max_iter):
        for i in range(n_wolves):
            mask = positions[i, :X_tr.shape[1]] > 0.35
            if mask.sum() < 4:
                mask[:4] = True
            n_est = int(20 + positions[i, -2] * 130)   # [20, 150]
            m_dep = int(6 + positions[i, -1] * 14)     # [6, 20]
            clf = RandomForestClassifier(
                n_estimators=n_est, max_depth=m_dep, n_jobs=-1, random_state=42
            )
            clf.fit(X_sub[:, mask], y_sub)
            score = accuracy_score(y_val, clf.predict(X_val[:, mask]))

            if score > alpha_score:
                delta_score, delta_pos = beta_score, (beta_pos.copy() if beta_pos is not None else None)
                beta_score, beta_pos = alpha_score, (alpha_pos.copy() if alpha_pos is not None else None)
                alpha_score, alpha_pos = score, positions[i].copy()
            elif score > beta_score:
                delta_score, delta_pos = beta_score, (beta_pos.copy() if beta_pos is not None else None)
                beta_score, beta_pos = score, positions[i].copy()
            elif score > delta_score:
                delta_score, delta_pos = score, positions[i].copy()

        a = 2.0 - it * (2.0 / max_iter)
        for i in range(n_wolves):
            for j in range(dim):
                r1, r2 = rng.rand(), rng.rand()
                X1 = alpha_pos[j] - (2 * a * r1 - a) * abs(2 * r2 * alpha_pos[j] - positions[i, j])
                r1, r2 = rng.rand(), rng.rand()
                X2 = beta_pos[j] - (2 * a * r1 - a) * abs(2 * r2 * beta_pos[j] - positions[i, j])
                r1, r2 = rng.rand(), rng.rand()
                X3 = delta_pos[j] - (2 * a * r1 - a) * abs(2 * r2 * delta_pos[j] - positions[i, j])
                positions[i, j] = np.clip((X1 + X2 + X3) / 3.0, 0.0, 1.0)

    best_mask = alpha_pos[:X_tr.shape[1]] > 0.35
    best_n_est = int(20 + alpha_pos[-2] * 130)
    best_m_dep = int(6 + alpha_pos[-1] * 14)
    final_clf = RandomForestClassifier(
        n_estimators=best_n_est, max_depth=best_m_dep, n_jobs=-1, random_state=42
    )
    final_clf.fit(X_tr[:, best_mask], y_tr)
    return final_clf, best_mask, best_n_est, best_m_dep

# ==============================================================================
# PART 2: DEEP SOTA ARCHITECTURES (2024-2026)
# 1. BiLSTM + Attention (PhishingRTDS / Asiri et al., 2024)
# 2. TCN + Multi-Head Self-Attention (Do et al., 2025)
# 3. Tabular Self-Attention Transformer (HET / Dam et al., 2026)
# ==============================================================================
def build_bilstm_attention(input_dim):
    inp = Input(shape=(input_dim, 1))
    x = layers.Bidirectional(layers.LSTM(32, return_sequences=True))(inp)
    # Attention mechanism over sequence steps
    attn = layers.Dense(1, activation="tanh")(x)
    attn = layers.Softmax(axis=1)(attn)
    context = layers.Multiply()([x, attn])
    x = layers.GlobalAveragePooling1D()(context)
    x = layers.Dense(32, activation="relu")(x)
    out = layers.Dense(1, activation="sigmoid")(x)
    model = models.Model(inputs=inp, outputs=out)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def build_tcn_mhsa(input_dim):
    inp = Input(shape=(input_dim, 1))
    # Dilated causal/temporal convolutions (TCN block)
    c1 = layers.Conv1D(32, kernel_size=3, padding="same", dilation_rate=1, activation="relu")(inp)
    c2 = layers.Conv1D(32, kernel_size=3, padding="same", dilation_rate=2, activation="relu")(c1)
    c3 = layers.Conv1D(32, kernel_size=3, padding="same", dilation_rate=4, activation="relu")(c2)
    x = layers.Add()([c1, c3])
    x = layers.LayerNormalization()(x)
    # Multi-Head Self-Attention (MHSA)
    attn_out = layers.MultiHeadAttention(num_heads=4, key_dim=8)(x, x)
    x = layers.Add()([x, attn_out])
    x = layers.LayerNormalization()(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(32, activation="relu")(x)
    out = layers.Dense(1, activation="sigmoid")(x)
    model = models.Model(inputs=inp, outputs=out)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def build_tabular_transformer(input_dim):
    inp = Input(shape=(input_dim, 1))
    # Feature token projection + positional embedding
    x = layers.Dense(32)(inp)
    attn1 = layers.MultiHeadAttention(num_heads=4, key_dim=8)(x, x)
    x = layers.LayerNormalization()(layers.Add()([x, attn1]))
    ffn = layers.Dense(64, activation="relu")(x)
    ffn = layers.Dense(32)(ffn)
    x = layers.LayerNormalization()(layers.Add()([x, ffn]))
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(1, activation="sigmoid")(x)
    model = models.Model(inputs=inp, outputs=out)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def measure_single_sample_latency_sklearn(clf, sample_2d, n_runs=500):
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        _ = clf.predict_proba(sample_2d)
        times.append((time.perf_counter() - t0) * 1000.0)
    return np.median(times), np.percentile(times, 99)

def measure_single_sample_latency_keras(model, sample_3d, n_runs=200):
    # Warm-up
    _ = model(sample_3d, training=False)
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        _ = model(sample_3d, training=False)
        times.append((time.perf_counter() - t0) * 1000.0)
    return np.median(times), np.percentile(times, 99)

print("\n==================== SOTA ARCHITECTURES ON PHISHSHIELD 20,000-URL DATASET ====================")
hdr = f"{'SOTA ARCHITECTURE':<38} | {'ACC%':<6} | {'PREC%':<6} | {'REC%':<6} | {'F1%':<6} | {'ROC-AUC':<7} | {'FPR%':<5} | {'1-URL p50(ms)':<13} | {'SIZE(KB)':<8}"
print(hdr)
print("-" * len(hdr))

def report_row(name, y_true, y_pred, y_prob, lat_p50, size_kb):
    acc = accuracy_score(y_true, y_pred) * 100
    prec = precision_score(y_true, y_pred) * 100
    rec = recall_score(y_true, y_pred) * 100
    f1 = f1_score(y_true, y_pred) * 100
    roc = roc_auc_score(y_true, y_prob)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = (fp / (fp + tn)) * 100
    print(f"{name:<38} | {acc:6.2f} | {prec:6.2f} | {rec:6.2f} | {f1:6.2f} | {roc:7.4f} | {fpr:5.2f} | {lat_p50:13.3f} | {size_kb:8.1f}")

# 1. PhishShield RF Baseline (20 trees)
rf_base = RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42)
rf_base.fit(X_train, y_train)
p50_rf, _ = measure_single_sample_latency_sklearn(rf_base, X_test[:1])
report_row("PhishShield RF Baseline (n=20, d=10)", y_test, rf_base.predict(X_test), rf_base.predict_proba(X_test)[:, 1], p50_rf, 327.9)

# 2. PhishShield RF Golden (100 trees, leaf=15)
rf_gold = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=15, max_features="sqrt", random_state=42)
rf_gold.fit(X_train, y_train)
p50_gold, _ = measure_single_sample_latency_sklearn(rf_gold, X_test[:1])
report_row("PhishShield RF Golden (n=100, d=10)", y_test, rf_gold.predict(X_test), rf_gold.predict_proba(X_test)[:, 1], p50_gold, 365.2)

# 3. HistGradientBoosting (LightGBM algorithm)
hgb = HistGradientBoostingClassifier(max_iter=100, max_depth=10, random_state=42)
hgb.fit(X_train, y_train)
jb_p = os.path.join(TEMP_DIR, "hgb.joblib")
joblib.dump(hgb, jb_p)
hgb_kb = os.path.getsize(jb_p) / 1024.0
p50_hgb, _ = measure_single_sample_latency_sklearn(hgb, X_test[:1])
report_row("HistGradientBoosting (LightGBM SOTA)", y_test, hgb.predict(X_test), hgb.predict_proba(X_test)[:, 1], p50_hgb, hgb_kb)

# 4. GWO-Optimized RF (Dandotiya et al., 2026)
gwo_clf, gwo_mask, gwo_n, gwo_d = run_gwo_rf(X_train, y_train, X_test, y_test)
jb_gwo = os.path.join(TEMP_DIR, "gwo.joblib")
joblib.dump(gwo_clf, jb_gwo)
gwo_kb = os.path.getsize(jb_gwo) / 1024.0
p50_gwo, _ = measure_single_sample_latency_sklearn(gwo_clf, X_test[:1, gwo_mask])
report_row(f"GWO-RF (k={int(gwo_mask.sum())}/16, n={gwo_n}, d={gwo_d})", y_test, gwo_clf.predict(X_test[:, gwo_mask]), gwo_clf.predict_proba(X_test[:, gwo_mask])[:, 1], p50_gwo, gwo_kb)

# Prepare 3D inputs for sequence/attention SOTA models
X_tr_3d = np.expand_dims(X_train, axis=-1)
X_te_3d = np.expand_dims(X_test, axis=-1)

# 5. BiLSTM + Attention (PhishingRTDS 2024)
bilstm = build_bilstm_attention(X_train.shape[1])
bilstm.fit(X_tr_3d, y_train, epochs=15, batch_size=64, verbose=0)
y_prob_bi = bilstm.predict(X_te_3d, verbose=0).ravel()
p50_bi, _ = measure_single_sample_latency_keras(bilstm, X_te_3d[:1])
k_bi = os.path.join(TEMP_DIR, "bi.keras")
bilstm.save(k_bi)
report_row("BiLSTM + Attention (PhishingRTDS 24)", y_test, (y_prob_bi > 0.5).astype(int), y_prob_bi, p50_bi, os.path.getsize(k_bi) / 1024.0)

# 6. TCN + Multi-Head Self-Attention (Do et al., 2025)
tcn = build_tcn_mhsa(X_train.shape[1])
tcn.fit(X_tr_3d, y_train, epochs=15, batch_size=64, verbose=0)
y_prob_tcn = tcn.predict(X_te_3d, verbose=0).ravel()
p50_tcn, _ = measure_single_sample_latency_keras(tcn, X_te_3d[:1])
k_tcn = os.path.join(TEMP_DIR, "tcn.keras")
tcn.save(k_tcn)
report_row("TCN + MHSA (Do et al., 2025)", y_test, (y_prob_tcn > 0.5).astype(int), y_prob_tcn, p50_tcn, os.path.getsize(k_tcn) / 1024.0)

# 7. Tabular Self-Attention Transformer (HET 2026)
het = build_tabular_transformer(X_train.shape[1])
het.fit(X_tr_3d, y_train, epochs=15, batch_size=64, verbose=0)
y_prob_het = het.predict(X_te_3d, verbose=0).ravel()
p50_het, _ = measure_single_sample_latency_keras(het, X_te_3d[:1])
k_het = os.path.join(TEMP_DIR, "het.keras")
het.save(k_het)
report_row("Self-Attention Transformer (HET 26)", y_test, (y_prob_het > 0.5).astype(int), y_prob_het, p50_het, os.path.getsize(k_het) / 1024.0)

# ==============================================================================
# PART 3: REALISTIC REAL-WORLD CLASS IMBALANCE & MULTI-LAYER V3.0 EVALUATION
# (Addressing Reviewer 3 Issue i: Realistic Real-World Phishing Scenarios)
# ==============================================================================
print("\n==================== REALISTIC SKEWED BASE-RATE TRAFFIC SCENARIOS ====================")
print("Evaluating Standalone RF vs. PhishShield V3.0 Multi-Layer Scoring (Heuristics + Non-Login Relaxer)")

# Load PhiUSIIL test split to evaluate realistic web base rates (1:1, 1:10, 1:50, 1:100 Phish:Legit)
if os.path.exists(PHI_PATH):
    from step2_public_benchmarks import extract_ps_11_url_features
    df_phi = pd.read_csv(PHI_PATH)
    y_phi = (1 - df_phi["label"]).astype(int).values
    X_phi_16 = extract_ps_11_url_features(df_phi["URL"])
    X_phi_16["SFH"] = ((df_phi["HasExternalFormSubmit"] == 1) | (df_phi["NoOfEmptyRef"] > 0)).astype(int)
    X_phi_16["Submit_email"] = df_phi["HasSubmitButton"].astype(int)
    X_phi_16["on_mouseover"] = (df_phi["NoOfPopup"] > 0).astype(int)
    X_phi_16["RightClick"] = df_phi["HasPasswordField"].astype(int)
    X_phi_16["Iframe"] = (df_phi["NoOfiFrame"] > 0).astype(int)
    has_pwd_all = df_phi["HasPasswordField"].values.astype(bool)

    idx_all = np.arange(len(y_phi))
    idx_tr, idx_te = train_test_split(idx_all, test_size=0.2, random_state=42, stratify=y_phi)

    X_p_tr, y_p_tr = X_phi_16.iloc[idx_tr].values, y_phi[idx_tr]
    X_p_te, y_p_te = X_phi_16.iloc[idx_te].values, y_phi[idx_te]
    pwd_te = has_pwd_all[idx_te]

    rf_phi = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=15, max_features="sqrt", n_jobs=-1, random_state=42)
    rf_phi.fit(X_p_tr, y_p_tr)

    raw_probs = rf_phi.predict_proba(X_p_te)[:, 1]

    # Apply exact V3.0 background.js multi-layer rules (Heuristics + Non-Login Contextual Relaxer)
    v3_scores = raw_probs.copy()
    for i in range(len(v3_scores)):
        s = v3_scores[i]
        feats = X_p_te[i]
        if feats[9] >= 4:
            s += 0.45
        if feats[7] > 1:
            s += 0.25
        if feats[10] == 1:
            s += 0.30
        # Non-Login Contextual Relaxer (background.js line 142)
        if 0.50 <= s <= 0.75 and not pwd_te[i]:
            s -= 0.20
        v3_scores[i] = np.clip(s, 0.0, 1.0)

    legit_indices = np.where(y_p_te == 0)[0]
    phish_indices = np.where(y_p_te == 1)[0]
    n_legit = len(legit_indices)  # 26,970 legitimate test URLs

    ratios = [
        ("Balanced Benchmark (1:1)", len(phish_indices)),
        ("Moderate Real-World Skew (1:10 Phish:Legit)", n_legit // 10),
        ("High Real-World Skew (1:50 Phish:Legit)", n_legit // 50),
        ("Enterprise Browsing Skew (1:100 Phish:Legit)", n_legit // 100),
    ]

    hdr2 = f"{'TRAFFIC SCENARIO':<44} | {'PIPELINE':<18} | {'ACC%':<6} | {'PREC%':<6} | {'REC%':<6} | {'F1%':<6} | {'FPR%':<5} | {'PR-AUC':<6}"
    print(hdr2)
    print("-" * len(hdr2))

    rng = np.random.RandomState(42)
    for label_str, n_p_sample in ratios:
        chosen_p = rng.choice(phish_indices, size=min(n_p_sample, len(phish_indices)), replace=False)
        eval_idx = np.concatenate([legit_indices, chosen_p])
        yt = y_p_te[eval_idx]

        for pipe_name, probs in [("Standalone RF", raw_probs[eval_idx]), ("PhishShield V3.0", v3_scores[eval_idx])]:
            yp = (probs > 0.50).astype(int)
            acc = accuracy_score(yt, yp) * 100
            prec = precision_score(yt, yp, zero_division=0) * 100
            rec = recall_score(yt, yp, zero_division=0) * 100
            f1 = f1_score(yt, yp, zero_division=0) * 100
            tn, fp, fn, tp = confusion_matrix(yt, yp).ravel()
            fpr = (fp / (fp + tn)) * 100
            prauc = average_precision_score(yt, probs)
            print(f"{label_str:<44} | {pipe_name:<18} | {acc:6.2f} | {prec:6.2f} | {rec:6.2f} | {f1:6.2f} | {fpr:5.2f} | {prauc:6.4f}")

print("\nStep 3 evaluation complete!")