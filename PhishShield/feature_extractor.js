// Feature Extractor - 16 ROBUST FEATURES

function isIP(domain) {
    const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(domain);
}

function extractFeaturesFromPage() {
    try {
        const url = window.location.href;
        const urlObj = new URL(url);
        let domain = urlObj.hostname;
        const features = [];

        // --- URL Features (7 Original) ---
        features.push(isIP(domain) ? 1 : 0); // 1
        features.push(url.length > 75 ? 1 : 0); // 2
        
        const shorteners = ["bit.ly", "goo.gl", "shorte.st", "go2l.ink", "x.co", "ow.ly", "t.co", "tinyurl", "tr.im", "is.gd", "cli.gs", "yfrog.com", "migre.me", "ff.im", "tiny.cc", "url4.eu", "twit.ac", "su.pr", "twurl.nl", "snipurl.com", "short.to", "budurl.com", "ping.fm", "post.ly", "just.as", "bkite.com", "snipr.com", "fic.kr", "loopt.us", "doiop.com", "short.ie", "kl.am", "wp.me", "rubyurl.com", "om.ly", "to.ly", "bit.do", "lnkd.in", "db.tt", "qr.ae", "adf.ly", "cur.lv", "ity.im", "q.gs", "po.st", "bc.vc", "twitthis.com", "u.to", "j.mp", "buzurl.com", "cutt.us", "u.bb", "yourls.org", "prettylinkpro.com", "scrnch.me", "filoops.info", "vzturl.com", "qr.net", "1url.com", "tweez.me", "v.gd", "link.zip.net"];
        features.push(shorteners.some(s => domain.includes(s)) ? 1 : 0); // 3

        features.push(url.includes("@") ? 1 : 0); // 4
        features.push(url.lastIndexOf("//") > 7 ? 1 : 0); // 5
        features.push(domain.includes("-") ? 1 : 0); // 6

        const parts = domain.split('.').filter(p => p !== 'www');
        features.push(parts.length > 3 ? 1 : 0); // 7

        // --- NEW FEATURES (4) ---
        
        // 8. Hyphen_Count
        features.push((domain.match(/-/g) || []).length);

        // 9. Dot_Count (Ignore www)
        let cleanDomain = domain.startsWith("www.") ? domain.substring(4) : domain;
        features.push((cleanDomain.match(/\./g) || []).length);

        // 10. Numeric_Chars
        features.push((domain.match(/\d/g) || []).length);

        // 11. Is_Common_TLD (0=Safe, 1=Risk)
        // We extract the suffix roughly (last part). 
        const suffix = parts[parts.length - 1];
        const common_tlds = ['com', 'org', 'net', 'edu', 'gov', 'uk', 'us', 'ca', 'au', 'de', 'fr', 'it', 'jp', 'io', 'co', 'ai'];
        features.push(common_tlds.includes(suffix) ? 0 : 1);


        // --- HTML Features (5 Original) --- 
        const forms = Array.from(document.querySelectorAll('form'));
        let sfh = 0;
        if (forms.some(f => !f.action || f.action === "about:blank" || f.action === "")) sfh = 1;
        features.push(sfh); // 12

        features.push(forms.some(f => f.action && f.action.startsWith('mailto:')) ? 1 : 0); // 13

        const htmlStr = document.documentElement.outerHTML.toLowerCase();
        features.push(htmlStr.includes('onmouseover') ? 1 : 0); // 14
        features.push((htmlStr.includes('event.button==2') || htmlStr.includes('oncontextmenu')) ? 1 : 0); // 15
        features.push(document.querySelectorAll('iframe').length > 0 ? 1 : 0); // 16

        console.log("PhishShield 16 Features:", features);
        return features;
    } catch (e) {
        console.error("Feature Extraction Error", e);
        return new Array(16).fill(0); 
    }
}
// --- NLP CONTENT SCANNER (Phase 2) ---

function calculateNLPScore() {
    try {
        const textContent = document.body.innerText.toLowerCase();
        let nlpScore = 0;

        // 1. Define Keyword Groups
        const urgencyWords = ['suspended', 'locked', 'banned', 'authorized', 'prevent', 'immediately', 'urgent', 'shutdown', 'deactivate'];
        const sensitiveWords = ['password', 'credit card', 'social security', 'bank account', 'routing number', 'pin', 'verify identity'];
        const actionWords = ['click here', 'login', 'sign in', 'update now', 'confirm', 'restore'];

        // 2. Scan for presence (Boolean)
        const hasUrgency = urgencyWords.some(w => textContent.includes(w));
        const hasSensitive = sensitiveWords.some(w => textContent.includes(w));
        const hasAction = actionWords.some(w => textContent.includes(w));

        // 3. Logic Scoring (Combinations are deadly)
        
        // Scenario A: "Your account is suspended" (Urgency + Sensitive)
        // Common in: Account lockout scams
        if (hasUrgency && hasSensitive) {
            console.log("NLP: Urgency + Sensitive keywords detected (+0.25)");
            nlpScore += 0.25;
        }

        // Scenario B: "Click here to login" (Action + Sensitive)
        // Common in: Credential harvesting
        if (hasAction && hasSensitive) {
            console.log("NLP: Action + Sensitive keywords detected (+0.15)");
            nlpScore += 0.15;
        }

        // Scenario C: "Urgent update required" (Urgency + Action)
        if (hasUrgency && hasAction) {
            console.log("NLP: Urgency + Action keywords detected (+0.15)");
            nlpScore += 0.15;
        }

        return nlpScore;

    } catch (e) {
        console.error("NLP Scan Failed", e);
        return 0;
    }
}