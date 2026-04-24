import pandas as pd
import os
from tqdm import tqdm
import random

# Import our feature extractor
from feature_extractor import extract_all_features, FINAL_FEATURE_LIST

# --- 1. Define Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "datasets")
PROC_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

phishtank_path = os.path.join(DATA_DIR, "phishtank_urls.csv")
legit_path = os.path.join(DATA_DIR, "top-1m.csv")
output_path = os.path.join(PROC_DATA_DIR, "realistic_dataset.csv")

# --- 2. Set Sample Size ---
# We'll take 10,000 of each to start. 
# Increase this for higher accuracy, but it will take longer.
SAMPLE_SIZE = 10000

# --- 3. Load and Process Phishing URLs ---
print(f"--- Loading Phishing URLs from {phishtank_path} ---")
try:
    phish_df = pd.read_csv(phishtank_path)
    # Get the 'url' column and shuffle it
    phish_urls = phish_df['url'].sample(frac=1, random_state=42).tolist()
    # Take our sample
    phish_urls_sample = phish_urls[:min(len(phish_urls), SAMPLE_SIZE)]
    print(f"Loaded {len(phish_urls)} phishing URLs. Using {len(phish_urls_sample)} samples.")
except Exception as e:
    print(f"Error loading PhishTank CSV: {e}")
    print("Please ensure 'phishtank_urls.csv' is in 'datasets' folder.")
    exit()

# --- 4. Load and Process Legitimate URLs ---
print(f"--- Loading Legitimate URLs from {legit_path} ---")
try:
    legit_df = pd.read_csv(legit_path, header=None, names=['Rank', 'Domain'])
    # Get the 'Domain' column
    legit_urls = legit_df['Domain'].tolist()
    # Take our sample
    legit_urls_sample = legit_urls[:min(len(legit_urls), SAMPLE_SIZE)]
    print(f"Loaded {len(legit_urls)} legitimate URLs. Using {len(legit_urls_sample)} samples.")
except Exception as e:
    print(f"Error loading Top-1M CSV: {e}")
    print("Please ensure 'top-1m.csv' is in 'datasets' folder.")
    exit()


# --- 5. Main Extraction Loop ---
all_features = []
all_labels = []

print("\n--- Starting Feature Extraction (This will take a while...) ---")

# Process Phishing URLs
print("Processing Phishing URLs...")
for url in tqdm(phish_urls_sample, desc="Phishing"):
    try:
        features = extract_all_features(url)
        all_features.append(features)
        all_labels.append(1) # Label 1 for Phishing
    except Exception as e:
        # print(f"Skipping {url} (Error: {e})")
        pass # Skip URLs that fail

# Process Legitimate URLs
print("\nProcessing Legitimate URLs...")
for domain in tqdm(legit_urls_sample, desc="Legitimate"):
    # Add 'https://www.' to make it a full URL
    url = f"https://www.{domain}"
    try:
        features = extract_all_features(url)
        all_features.append(features)
        all_labels.append(0) # Label 0 for Legitimate
    except Exception as e:
        # print(f"Skipping {url} (Error: {e})")
        pass # Skip URLs that fail

print("\n--- Feature extraction complete! ---")

# --- 6. Create and Save DataFrame ---
print("Creating DataFrame and saving to CSV...")

# Create the final DataFrame
final_df = pd.DataFrame(all_features, columns=FINAL_FEATURE_LIST)
final_df['class'] = all_labels

# Shuffle the dataset one last time
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to disk
final_df.to_csv(output_path, index=False)

print(f"\n--- SUCCESS! ---")
print(f"New dataset saved to: {output_path}")
print(f"Total rows: {len(final_df)}")
print("\nFirst 5 rows of new dataset:")
print(final_df.head())