import os
import time
import warnings
import joblib
import numpy as np
import pandas as pd
import m2cgen as m2c

from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# --- 1. Paths & Data Loading ---
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, "processed_data", "realistic_dataset.csv")
TEMP_DIR = os.path.join(BASE_DIR, "temp_eval")
os.makedirs(TEMP_DIR, exist_ok=True)

print(f"Loading final 16-feature dataset from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"Dataset shape: {df.shape} | Columns: {list(df.columns)}")

X = df.drop("class", axis=1)
y = df["class"]

# Exact same 80/20 split used in train_rf_model.py and ablation_test.py
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")
print(f"Test class counts -> Phishing (1): {int((y_test == 1).sum())}, Legitimate (0): {int((y_test == 0).sum())}")
print("=" * 120)

# --- 2. Define Full Candidate Sweep ---
candidates = [
    # Random Forest Sweep + Golden Config
    ("RF (Light: n=20, d=10)", RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42), True),
    ("RF (Medium: n=50, d=15)", RandomForestClassifier(n_estimators=50, max_depth=15, random_state=42), True),
    ("RF (Heavy: n=100, d=20)", RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42), True),
    ("RF (Golden: n=100, d=10, leaf=15)", RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=15, max_features="sqrt", random_state=42), True),

    # XGBoost Sweep
    ("XGB (Light: n=50, d=6)", XGBClassifier(n_estimators=50, max_depth=6, eval_metric="logloss", random_state=42), True),
    ("XGB (Medium: n=100, d=10)", XGBClassifier(n_estimators=100, max_depth=10, eval_metric="logloss", random_state=42), True),
    ("XGB (Heavy: n=200, d=15)", XGBClassifier(n_estimators=200, max_depth=15, eval_metric="logloss", random_state=42), True),

    # Gradient Boosting Sweep
    ("GB (Light: n=50, d=3)", GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42), False),
    ("GB (Medium: n=100, d=5)", GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42), False),
    ("GB (Heavy: n=200, d=7)", GradientBoostingClassifier(n_estimators=200, max_depth=7, random_state=42), False),

    # Additional Classical & Neural Baselines on the same 16 features
    ("Decision Tree (d=10)", DecisionTreeClassifier(max_depth=10, random_state=42), True),
    ("Extra Trees (n=100, d=10)", ExtraTreesClassifier(n_estimators=100, max_depth=10, random_state=42), True),
    ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42), True),
    ("SVM (RBF Kernel)", SVC(kernel="rbf", probability=True, random_state=42), False),
    ("MLP Neural Net (64-32-1)", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=50, random_state=42), False),
]

header = (
    f"{'MODEL':<33} | {'ACC%':<6} | {'PREC%':<6} | {'REC%':<6} | {'F1%':<6} | "
    f"{'ROC-AUC':<7} | {'PR-AUC':<7} | {'FP':<4} | {'FN':<4} | {'PY(KB)':<7} | {'JS(KB)':<8}"
)
print(header)
print("-" * len(header))

for name, model, try_js in candidates:
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred) * 100
    prec = precision_score(y_test, y_pred) * 100
    rec = recall_score(y_test, y_pred) * 100
    f1 = f1_score(y_test, y_pred) * 100
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    # Python joblib size
    jb_path = os.path.join(TEMP_DIR, "tmp.joblib")
    joblib.dump(model, jb_path)
    py_kb = os.path.getsize(jb_path) / 1024.0
    os.remove(jb_path)

    # m2cgen JS size
    js_kb_str = "N/A"
    if try_js:
        try:
            js_code = m2c.export_to_javascript(model, function_name="scoreModel")
            js_path = os.path.join(TEMP_DIR, "tmp.js")
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(js_code)
            js_kb = os.path.getsize(js_path) / 1024.0
            js_kb_str = f"{js_kb:.1f}"
            os.remove(js_path)
        except Exception as e:
            js_kb_str = "Unsupported"

    print(
        f"{name:<33} | {acc:6.2f} | {prec:6.2f} | {rec:6.2f} | {f1:6.2f} | "
        f"{roc_auc:7.4f} | {pr_auc:7.4f} | {fp:<4} | {fn:<4} | {py_kb:7.1f} | {js_kb_str:<8}"
    )

# Also run Keras Sequential NN (64 -> Dropout(0.3) -> 32 -> Dropout(0.2) -> 1) on the EXACT 16-feature split
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout

    tf.random.set_seed(42)
    np.random.seed(42)

    keras_model = Sequential([
        Dense(64, activation="relu", input_shape=[X_train.shape[1]]),
        Dropout(0.3),
        Dense(32, activation="relu"),
        Dropout(0.2),
        Dense(1, activation="sigmoid"),
    ])
    keras_model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    keras_model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2, verbose=0)

    y_prob_k = keras_model.predict(X_test, verbose=0).ravel()
    y_pred_k = (y_prob_k > 0.5).astype(int)

    acc_k = accuracy_score(y_test, y_pred_k) * 100
    prec_k = precision_score(y_test, y_pred_k) * 100
    rec_k = recall_score(y_test, y_pred_k) * 100
    f1_k = f1_score(y_test, y_pred_k) * 100
    roc_k = roc_auc_score(y_test, y_prob_k)
    pr_k = average_precision_score(y_test, y_prob_k)
    tn_k, fp_k, fn_k, tp_k = confusion_matrix(y_test, y_pred_k).ravel()

    k_path = os.path.join(TEMP_DIR, "tmp.keras")
    keras_model.save(k_path)
    k_kb = os.path.getsize(k_path) / 1024.0
    os.remove(k_path)

    print(
        f"{'Keras Sequential NN (16-feat)':<33} | {acc_k:6.2f} | {prec_k:6.2f} | {rec_k:6.2f} | {f1_k:6.2f} | "
        f"{roc_k:7.4f} | {pr_k:7.4f} | {fp_k:<4} | {fn_k:<4} | {k_kb:7.1f} | {'TF.js 2MB+':<8}"
    )
except Exception as e:
    print(f"Keras evaluation skipped or failed: {e}")

try:
    os.rmdir(TEMP_DIR)
except Exception:
    pass
print("=" * 120)