import requests
import pandas as pd
import random
import os

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

PHISH_COUNT = 500
LEGIT_COUNT = 500

# Standard User-Agent to prevent API blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def build_dataset():
    dataset = []
    print(f"🛠️ Starting PhishShield Dataset Builder...")

    # --- 1. FETCH PHISHING SITES (OpenPhish) ---
    print("\n[1/2] Fetching active zero-day phishing URLs from OpenPhish...")
    try:
        phish_resp = requests.get("https://openphish.com/feed.txt", headers=HEADERS, timeout=10)
        phish_resp.raise_for_status()
        
        # Parse and clean URLs
        phish_urls = [line.strip() for line in phish_resp.text.splitlines() if line.strip().startswith("http")]
        
        # Randomly sample the requested amount (or take all if less are available)
        phish_sample = random.sample(phish_urls, min(PHISH_COUNT, len(phish_urls)))
        
        for url in phish_sample:
            dataset.append({"url": url, "expected_label": "PHISHING"})
            
        print(f"✅ Successfully loaded {len(phish_sample)} phishing URLs.")
    except Exception as e:
        print(f"❌ Failed to fetch OpenPhish feed: {e}")

    # --- 2. FETCH LEGITIMATE SITES (Majestic Million) ---
    print("\n[2/2] Streaming Top 1M Legitimate Domains from Majestic...")
    try:
        legit_urls = []
        # We use stream=True so we don't load a 100MB CSV into RAM just to get 500 lines
        with requests.get("http://downloads.majestic.com/majestic_million.csv", stream=True, timeout=10) as r:
            r.raise_for_status()
            lines = r.iter_lines()
            next(lines)  # Skip the CSV header row
            
            for _ in range(LEGIT_COUNT):
                try:
                    line = next(lines).decode('utf-8')
                    # Majestic CSV format: GlobalRank,TldRank,Domain,...
                    domain = line.split(',')[2] 
                    legit_urls.append(f"https://www.{domain}")
                except StopIteration:
                    break
                    
        for url in legit_urls:
            dataset.append({"url": url, "expected_label": "LEGITIMATE"})
            
        print(f"✅ Successfully loaded {len(legit_urls)} legitimate URLs.")
    except Exception as e:
        print(f"❌ Failed to fetch Majestic Million: {e}")

    # --- 3. SHUFFLE AND SAVE ---
    if not dataset:
        print("\n⚠️ Failed to build dataset. Check your internet connection.")
        return

    print("\n[3/3] Shuffling dataset to randomize test order...")
    df = pd.DataFrame(dataset)
    
    # Shuffle the dataframe so Legit/Phishing are completely mixed
    df = df.sample(frac=1, random_state=42).reset_index(drop=True) 
    
    df.to_csv(DATASET_PATH, index=False)
    print(f"🎉 Dataset successfully saved to: {DATASET_PATH}")
    print(f"📊 Total Rows: {len(df)}")

if __name__ == "__main__":
    build_dataset()