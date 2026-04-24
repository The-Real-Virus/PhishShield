import m2cgen as m2c
import joblib
import os

# --- 1. Setup Paths ---
BASE_DIR = os.getcwd()
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Input Model Path
INPUT_MODEL_PATH = os.path.join(MODELS_DIR, "phishshield_rf.joblib")

# Output Paths
# 1. Save in models folder (Archive/Organization)
OUTPUT_ARCHIVE_PATH = os.path.join(MODELS_DIR, "model_logic.js")

# --- 2. Load the Trained Model ---
print(f"Loading trained model from: {INPUT_MODEL_PATH}...")
try:
    model = joblib.load(INPUT_MODEL_PATH)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model file not found. Please run 'src/train_rf_model.py' first.")
    exit()

# --- 3. Convert to JavaScript ---
print("Transpiling model to JavaScript (m2cgen)...")
# This creates the 'scoreModel' function used by background.js
try:
    js_code = m2c.export_to_javascript(model, function_name="scoreModel")
except Exception as e:
    print(f"Error during transpilation: {e}")
    exit()

# --- 4. Save the Files ---

# Save to Models Directory (Archive)
with open(OUTPUT_ARCHIVE_PATH, "w") as f:
    f.write(js_code)
print(f"[Saved] JS Model Archive: {OUTPUT_ARCHIVE_PATH}")

# --- 5. Stats ---
size_kb = os.path.getsize(OUTPUT_ARCHIVE_PATH) / 1024
print(f"\nSUCCESS! Deployment Complete.")
print(f"Final JavaScript Model Size: {size_kb:.2f} KB")