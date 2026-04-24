// 1. Run Extraction HERE (on the page)
const features = extractFeaturesFromPage(); // Extract URL/HTML features
const nlpScore = calculateNLPScore(); // Run Phase 2 NLP Scan
const currentUrl = window.location.href; // Get the URL

// Phase 3: Password Field Detection
const hasPasswordInput = document.querySelector('input[type="password"]') !== null;

// 2. Send FEATURES AND URL to Background
chrome.runtime.sendMessage({
    action: "predict_features",
    features: features,
    nlpScore: nlpScore,
    hasPassword: hasPasswordInput,
    url: currentUrl 
}, (response) => {
    if (response && response.result === "PHISHING") {
        const div = document.createElement('div');
        div.style = "position:fixed; top:0; left:0; width:100%; height:100px; background:red; color:white; z-index:99999; font-size:24px; text-align:center; padding-top:30px; font-family:sans-serif; box-shadow: 0 4px 12px rgba(0,0,0,0.5);";
        div.innerHTML = `
            <div style="font-weight: bold;">⚠️ PhishShield Warning</div>
            <div style="font-size: 16px; margin-top: 10px;">This site is ${response.score}% likely to be Phishing! Proceed with caution.</div>
            <button id="ps-close" style="position: absolute; top: 10px; right: 20px; background: white; color: red; border: none; padding: 5px 10px; cursor: pointer; font-weight: bold;">X</button>
        `;
        document.body.appendChild(div);
        
        document.getElementById('ps-close').onclick = function() {
            div.remove();
        };
    } else {
        console.log("PhishShield: Site Safe (" + response.score + "%)");
    }
});