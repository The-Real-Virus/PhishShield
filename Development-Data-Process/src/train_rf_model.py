import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# --- 1. Setup Paths ---
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, "processed_data", "realistic_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# --- 2. Load Data ---
print(f"Loading data from {DATA_PATH}...")
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print("Error: Dataset not found.")
    exit()

# Separate Features (X) and Target (y)
X = df.drop('class', axis=1)
y = df['class']

# Split into Training (80%) and Testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 3. Train Model ---
# We use parameters optimized for Browser Extensions (Low depth = smaller file)
print("Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,      # Stability
    max_depth=10,          # Size Control (<500KB)
    min_samples_leaf=15,   # Prevents Overfitting (Real-world fix)
    max_features='sqrt',   # Diversity
    random_state=42
)
model.fit(X_train, y_train)

# --- 4. Detailed Evaluation ---
print("\n--- Evaluation Report ---")
y_pred = model.predict(X_test)

# Accuracy
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc * 100:.2f}%")

# Full Report (Precision, Recall, F1)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))

# Confusion Matrix (The Truth Table)
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix (Console):")
print(cm)

# --- 5. Generate & Save Confusion Matrix Image ---
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Legitimate', 'Phishing'], 
            yticklabels=['Legitimate', 'Phishing'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('PhishShield Model Performance')
cm_path = os.path.join(MODELS_DIR, "confusion_matrix.png")
plt.savefig(cm_path)
print(f"\n[Visual] Confusion Matrix saved to: {cm_path}")

# --- 6. Save the Model ---
model_path = os.path.join(MODELS_DIR, "phishshield_rf.joblib")
joblib.dump(model, model_path)
print(f"[Success] Trained model saved to: {model_path}")