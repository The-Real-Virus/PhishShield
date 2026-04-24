from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
import os
import time

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
EXTENSION_PATH = os.path.join(BASE_DIR, "extension")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv") 
REPORT_PATH = os.path.join(BASE_DIR, "v3_stress_test_report.csv")

def run_stress_test():
    try:
        df = pd.read_csv(DATASET_PATH)
        urls = df.to_dict('records')
    except FileNotFoundError:
        print(f"Error: Please create a {DATASET_PATH} file.")
        return

    results = []
    metrics = {"TP": 0, "FP": 0, "TN": 0, "FN": 0, "Errors": 0}

    print(f"🚀 Starting PhishShield v3.0 Stress Test Engine...")
    print(f"📦 Loading Extension from: {EXTENSION_PATH}")
    print(f"🌐 Target Sites: {len(urls)}\n")

    with sync_playwright() as p:
        browser_args = [
            f"--disable-extensions-except={EXTENSION_PATH}",
            f"--load-extension={EXTENSION_PATH}",
        ]
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE_DIR, "chrome_profile"),
            headless=False, 
            args=browser_args,
            ignore_https_errors=True 
        )
        
        page = context.new_page()
        
        # --- THE X-RAY VISION (Bridges Chrome Console to Python Terminal) ---
        page.on("console", lambda msg: print(f"      [Chrome] {msg.text}"))
        page.on("pageerror", lambda err: print(f"      [Chrome ERROR] {err}"))
        
        print("⏳ Waiting 6 seconds for Background Service Worker to boot & fetch GitLab data...")
        time.sleep(6) # Increased boot time for fresh profiles

        for i, item in enumerate(urls):
            url = item['url']
            expected = str(item['expected_label']).upper()
            print(f"\n[{i+1}/{len(urls)}] Testing: {url[:60]}...")
            
            start_time = time.time()
            actual_result = "ERROR"
            score = "0"
            
            try:
                # 1. Navigate to URL 
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
                
                # 2. Wait for content.js to inject our handshake tag (Increased to 8s)
                element = page.wait_for_selector('#phishshield-result', state='attached', timeout=8000)
                
                # 3. Read the injected data
                if element:
                    content = element.get_attribute("content")
                    if ":" in content:
                        actual_result, score = content.split(":")
                    else:
                        actual_result = "PARSE_ERROR"
                
                # 4. Calculate Metrics
                if actual_result == "PHISHING" and expected == "PHISHING": metrics["TP"] += 1
                elif actual_result == "PHISHING" and expected == "LEGITIMATE": metrics["FP"] += 1
                elif actual_result == "LEGITIMATE" and expected == "LEGITIMATE": metrics["TN"] += 1
                elif actual_result == "LEGITIMATE" and expected == "PHISHING": metrics["FN"] += 1

            except PlaywrightTimeoutError:
                actual_result = "TIMEOUT"
                metrics["Errors"] += 1
            except Exception as e:
                actual_result = f"FAILED: {str(e)[:20]}"
                metrics["Errors"] += 1

            latency = round((time.time() - start_time) * 1000, 2)
            
            icon = "✅" if actual_result == expected else ("⚠️" if "ERROR" in actual_result or "TIMEOUT" in actual_result else "❌")
            print(f"    {icon} Result: {actual_result} ({score}%) | Expected: {expected} | Time: {latency}ms")
            
            results.append({
                "url": url,
                "expected": expected,
                "actual": actual_result,
                "score": score,
                "latency_ms": latency
            })

        context.close()

    # --- SAVE AND PRINT REPORT ---
    report_df = pd.DataFrame(results)
    report_df.to_csv(REPORT_PATH, index=False)
    
    total_valid = len(urls) - metrics["Errors"]
    accuracy = ((metrics["TP"] + metrics["TN"]) / total_valid) * 100 if total_valid > 0 else 0
    fpr = (metrics["FP"] / (metrics["FP"] + metrics["TN"])) * 100 if (metrics["FP"] + metrics["TN"]) > 0 else 0

    print("\n" + "="*50)
    print("📊 PHISHSHIELD V3.0 STRESS TEST RESULTS")
    print("="*50)
    print(f"Total Processed : {len(urls)}")
    print(f"Errors/Dead URLs: {metrics['Errors']}")
    print(f"Valid Tests     : {total_valid}")
    print("-" * 50)
    print(f"🎯 ACCURACY            : {accuracy:.2f}%")
    print(f"🚨 FALSE POSITIVE RATE : {fpr:.2f}% (Target: < 1.0%)")
    print("="*50)

if __name__ == "__main__":
    run_stress_test()