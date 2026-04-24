document.addEventListener('DOMContentLoaded', () => {
    // 1. Get the current active tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const currentTab = tabs[0];
        const tabIdKey = currentTab.id.toString();
        
        // 2. Fetch result using the Tab ID
        chrome.storage.local.get([tabIdKey], (result) => {
            const data = result[tabIdKey];
            updateUI(data);
        });
    });

    // 3. Button Listeners
    document.getElementById('btn-scan').addEventListener('click', () => {
        window.close(); 
        chrome.tabs.reload(); 
    });
});

function updateUI(data) {
    const statusText = document.getElementById('status-text');
    const statusIcon = document.getElementById('status-icon');
    const scoreBar = document.getElementById('score-bar');
    const scoreText = document.getElementById('score-text');

    if (!data) {
        // If no data, it usually means the page hasn't loaded fully yet
        statusText.textContent = "Scanning...";
        statusIcon.textContent = "⏳";
        return;
    }

    const score = parseInt(data.score);
    scoreText.textContent = `${score}%`;
    scoreBar.style.width = `${score}%`;

    if (data.result === "PHISHING") {
        statusText.textContent = "DANGEROUS";
        statusText.className = "status-text danger-color";
        statusIcon.textContent = "💀";
        scoreBar.style.backgroundColor = "#e74c3c"; // Red
    } else {
        statusText.textContent = "SAFE";
        statusText.className = "status-text safe-color";
        statusIcon.textContent = "🛡️";
        scoreBar.style.backgroundColor = "#2ecc71"; // Green
    }
}