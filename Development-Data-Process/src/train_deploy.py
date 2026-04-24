import pandas as pd
import m2cgen as m2c
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

# --- 1. Setup Paths ---
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, "processed_data", "realistic_dataset.csv")
EXTENSION_DIR = os.path.join(BASE_DIR, "extension")

# Create extension folder if it doesn't exist (we will populate it later)
os.makedirs(EXTENSION_DIR, exist_ok=True)

# --- 2. Load Your Data ---
print(f"Loading data from {DATA_PATH}...")
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print("Error: realistic_dataset.csv not found. Please run create_dataset.py first.")
    exit()

# Separate Features (X) and Target (y)
X = df.drop('class', axis=1)
y = df['class']

# --- 3. Train the Model (The "Deadline-Friendly" Configuration) ---
# We use n_estimators=20 and max_depth=10 as recommended by research
# to keep the resulting JavaScript file small and fast.
print("Training Random Forest (Optimized for Browser)...")
clf = RandomForestClassifier(
    n_estimators=20, 
    max_depth=10, 
    random_state=42
)
clf.fit(X, y)

# Evaluate Accuracy
accuracy = clf.score(X, y)
print(f"--- Model Accuracy: {accuracy * 100:.2f}% ---")

# --- 4. Convert to JavaScript ---
print("Transpiling model to JavaScript...")
# This converts the Python trees into a JavaScript function named 'scoreModel'
js_code = m2c.export_to_javascript(clf, function_name="scoreModel")

# --- 5. Save to Extension Folder ---
output_path = os.path.join(EXTENSION_DIR, "model_logic.js")
with open(output_path, "w") as f:
    f.write(js_code)

print(f"SUCCESS! Javascript model saved to: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")