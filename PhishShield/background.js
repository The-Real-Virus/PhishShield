importScripts('model_logic.js');
importScripts('whitelist.js'); 
importScripts('phash_fallback.js');

// --- 1. CONFIGURATION ---

const REMOTE_WHITELIST_URL = "https://gitlab.com/-/snippets/5932458/raw/main/whitelist.json"; 
const REMOTE_PHASH_URL = "https://gitlab.com/-/snippets/5972646/raw/main/phash.json";

// NEW: Hackers abuse these free subdomains. Do not allow the Whitelist to auto-trust them.
const FREE_HOST_EXCLUSIONS = ['pages.dev', 'workers.dev', 'weebly.com', 'ghost.io', 'wixsite.com', 'appspot.com', 'repl.co', 'glitch.me', 'firebaseapp.com'];

// GLOBAL CACHE 
let cachedWhitelist = new Set(TRUSTED_DOMAINS_SET);
let cachedVisualHashes = FALLBACK_HASHES;

// --- 2. STORAGE & REMOTE FETCH SYSTEM ---

// Load from Storage (Offline Fallback)
async function loadDataFromStorage() {
    try {
        const wlData = await chrome.storage.local.get('living_whitelist');
        if (wlData.living_whitelist) {
            cachedWhitelist = new Set(wlData.living_whitelist);
            console.log(`[Local Fallback] Loaded ${cachedWhitelist.size} domains from storage.`);
        }
        
        const phData = await chrome.storage.local.get('visual_hashes');
        if (phData.visual_hashes) {
            cachedVisualHashes = phData.visual_hashes;
            console.log(`[Local Fallback] Loaded ${Object.keys(cachedVisualHashes).length} hashes from storage.`);
        }
    } catch (e) {
        console.warn("Storage read failed, using hardcoded fallbacks.");
    }
}

// Update from Remote
async function updateRemoteData() {
    // 1. Fetch Whitelist
    try {
        console.log(`[Living Whitelist] Checking for updates from GitLab...`);
        const wlResponse = await fetch(REMOTE_WHITELIST_URL);
        if (!wlResponse.ok) throw new Error(`GitLab response: ${wlResponse.status}`);
        
        const wlData = await wlResponse.json();
        if (wlData.domains && Array.isArray(wlData.domains)) {
            await chrome.storage.local.set({ 'living_whitelist': wlData.domains });
            cachedWhitelist = new Set(wlData.domains);
            console.log(`[Living Whitelist] Success! Updated with ${cachedWhitelist.size} domains.`);
        }
    } catch (error) {
        console.warn("[Living Whitelist] Fetch failed (Safe fallback active):", error.message);
    }

    // 2. Fetch Visual Hashes
    try {
        console.log(`[Phase 3] Checking for visual hash updates...`);
        const phResponse = await fetch(REMOTE_PHASH_URL);
        if (!phResponse.ok) throw new Error(`GitLab response: ${phResponse.status}`);
        
        const phData = await phResponse.json();
        if (phData.hashes) {
            await chrome.storage.local.set({ 'visual_hashes': phData.hashes });
            cachedVisualHashes = phData.hashes;
            console.log(`[Phase 3] Success! Updated with ${Object.keys(cachedVisualHashes).length} visual hashes.`);
        }
    } catch (error) {
        console.warn("[Phase 3] Fetch failed (Safe fallback active):", error.message);
    }
}

// Initialization
chrome.runtime.onInstalled.addListener(() => {
    loadDataFromStorage();
    updateRemoteData(); 
    chrome.alarms.create("refreshData", { periodInMinutes: 1440 }); 
});

chrome.runtime.onStartup.addListener(() => {
    loadDataFromStorage(); 
    updateRemoteData(); 
});

chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "refreshData") updateRemoteData();
});


// --- 3. OFFSCREEN & HAMMING UTILS (Phase 3) ---

async function setupOffscreenDocument(path) {
    const offscreenUrl = chrome.runtime.getURL(path);
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
        documentUrls: [offscreenUrl]
    });
    if (existingContexts.length > 0) return;
    await chrome.offscreen.createDocument({
        url: path,
        reasons: ['DOM_PARSER'],
        justification: 'Process screenshot for visual hashing'
    });
}

function getHammingDistance(hash1, hash2) {
    let dist = 0;
    for (let i = 0; i < hash1.length; i++) {
        const val1 = parseInt(hash1[i], 16);
        const val2 = parseInt(hash2[i], 16);
        let xor = val1 ^ val2;
        while (xor > 0) {
            dist += xor & 1;
            xor >>= 1;
        }
    }
    return dist;
}


// --- 4. MAIN PREDICTION LISTENER ---

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "predict_features") {
        (async () => {
            try {
                const features = request.features;
                let urlObj = new URL(request.url);
                let hostname = urlObj.hostname;
                let cleanHostname = hostname.replace("www.", "");
                
                // A. Run ML Model
                let rawScores = scoreModel(features);
                let phishScore = Array.isArray(rawScores) ? rawScores[1] : rawScores;
                console.log(`[Tab ${sender.tab.id}] ML Raw Score: ${phishScore.toFixed(2)}`);

                // B. Universal Heuristics
                if (features[9] >= 4) {
                    console.log("Heuristic: High Entropy (+0.45)");
                    phishScore += 0.45;
                }
                if (features[7] > 1) {
                    console.log("Heuristic: Hyphen Attack (+0.25)");
                    phishScore += 0.25;
                }
                if (features[10] === 1) {
                    console.log("Heuristic: Risky TLD (+0.30)");
                    phishScore += 0.30;
                }
                const dangerousWords = ['login', 'verify', 'account', 'update', 'wallet', 'vault', 'secure', 'confirm', 'banking'];
                if (dangerousWords.some(w => hostname.toLowerCase().includes(w))) {
                     console.log("Heuristic: Intent Keyword (+0.20)");
                     phishScore += 0.20;
                }

                // C. NLP Content Scan (Phase 2)
                const nlpScore = request.nlpScore || 0; 
                if (nlpScore > 0) {
                     console.log(`[Phase 2] NLP Score added: +${nlpScore.toFixed(2)}`);
                     phishScore += nlpScore;
                }

                // C.5 NEW: False Positive Mitigation (Non-Login Relaxer)
                // Lowers score for ad-heavy legitimate sites (like news) that don't have password inputs
                if (phishScore >= 0.50 && phishScore <= 0.75 && !request.hasPassword) {
                     console.log("Heuristic: Non-Login ML Relaxer (-0.20)");
                     phishScore -= 0.20;
                }

                // Clamp to absolute bounds
                phishScore = Math.max(0.0, Math.min(phishScore, 1.0));

                // D. Visual Similarity Clone Detector (Phase 3)
                if (phishScore >= 0.10 && phishScore < 0.70 && request.hasPassword && Object.keys(cachedVisualHashes).length > 0) {
                    console.log("[Phase 3] Trigger condition met. Initiating Visual Scan...");
                    try {
                        const dataUrl = await chrome.tabs.captureVisibleTab(sender.tab.windowId, {format: 'jpeg', quality: 10});
                        await setupOffscreenDocument('offscreen.html');
                        
                        const response = await chrome.runtime.sendMessage({
                            target: 'offscreen',
                            action: 'hash_image',
                            dataUrl: dataUrl
                        });
                        
                        const liveHash = response.hash;
                        console.log(`[Phase 3] Live Viewport Hash: ${liveHash}`);
                        
                        let visualMatchFound = false;
                        let matchedTargetDomain = "";

                        // Compare against all stored targets and their variants
                        for (const [targetDomain, hashData] of Object.entries(cachedVisualHashes)) {
                            const hashVariants = Array.isArray(hashData) ? hashData : [hashData];
                            
                            for (const targetHash of hashVariants) {
                                const distance = getHammingDistance(liveHash, targetHash);
                                
                                // Distance <= 5 means ~92% visual match
                                if (distance <= 5) {
                                    visualMatchFound = true;
                                    matchedTargetDomain = targetDomain;
                                    break; 
                                }
                            }
                            if (visualMatchFound) break; 
                        }

                        // Apply the verdict if a visual match was found
                        if (visualMatchFound) {
                            if (!cleanHostname.endsWith(matchedTargetDomain)) {
                                console.log(`[Phase 3] CLONE DETECTED! UI matches ${matchedTargetDomain} but URL is ${hostname}. Overriding to Block.`);
                                phishScore = 1.0; 
                            } else {
                                console.log(`[Phase 3] Verified visual match for legitimate site: ${matchedTargetDomain}.`);
                                phishScore = 0.0;
                            }
                        }

                    } catch (visualError) {
                        console.error("[Phase 3] Visual scan failed, using fallback score.", visualError);
                    }
                }

                // E. Living Whitelist Check (Ultimate Safety Net)
                let isTrusted = false;
                let isExcluded = FREE_HOST_EXCLUSIONS.some(ext => cleanHostname.endsWith(ext));

                if (!isExcluded) {
                    if (cachedWhitelist.has(cleanHostname)) {
                        isTrusted = true;
                    } else {
                        for (let trusted of cachedWhitelist) {
                            if (cleanHostname.endsWith('.' + trusted)) {
                                isTrusted = true;
                                break;
                            }
                        }
                    }
                } else {
                    console.log(`[Living Whitelist] Domain (${hostname}) is on Free-Host Exclusion List. Bypassing whitelist.`);
                }

                if (isTrusted) {
                    console.log(`[Living Whitelist] Trusted Domain (${hostname}). Score forced to 0.`);
                    phishScore = 0;
                }

                // F. Final Result
                const isPhishing = phishScore > 0.50;
                const resultText = isPhishing ? "PHISHING" : "LEGITIMATE";
                const finalScorePercent = (phishScore * 100).toFixed(0);

                console.log(`[Tab ${sender.tab.id}] Final Decision: ${resultText} (${finalScorePercent}%)`);

                if (sender.tab && sender.tab.id) {
                    chrome.storage.local.set({
                        [sender.tab.id.toString()]: { result: resultText, score: finalScorePercent, url: request.url }
                    });
                }
                
                sendResponse({ result: resultText, score: finalScorePercent });

            } catch (e) {
                console.error("Analysis Failed", e);
                sendResponse({ error: e.message });
            }
        })();
        return true; 
    }
});