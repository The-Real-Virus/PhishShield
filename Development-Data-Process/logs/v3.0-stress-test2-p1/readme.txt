Phase A: Automated Mass-Testing (The "Stress Test")
The current Python script uses requests, which only sees raw HTML. Modern phishing uses JavaScript to build the page. We must upgrade the automation to simulate a real Chrome browser.

The Engine Upgrade: We transition the Python test script from requests to Playwright or Selenium. This launches a hidden ("headless") Chrome browser that fully renders the page, executes JS, and takes actual screenshots to test Phase 3 locally.

The Datasets (The 10,000 Challenge):

Phishing Feed: We script an automated daily pull from the OpenPhish API or PhishTank database to grab 5,000 live, active phishing URLs.

Legitimate Feed: We pull the top 5,000 sites from the Tranco List (the modern Alexa Top 1M) to aggressively test for False Positives.

The Output (The Confusion Matrix): The script will run overnight and output an enterprise-grade report showing:

True Positives (Caught Phish): Target > 90%

False Positives (Blocked Legit Sites): Target < 1% (This is the most critical metric for industry acceptance).

True Negatives / False Negatives.
