chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.target === 'offscreen' && request.action === 'hash_image') {
        generateHash(request.dataUrl).then(hash => sendResponse({ hash }));
        return true; 
    }
});

async function generateHash(dataUrl) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            canvas.width = 8;
            canvas.height = 8;
            
            // Draw scaled down to 8x8 (64 pixels total)
            ctx.drawImage(img, 0, 0, 8, 8);
            const imageData = ctx.getImageData(0, 0, 8, 8).data;
            
            let total = 0;
            const grays = [];
            
            // Convert to grayscale and sum
            for (let i = 0; i < imageData.length; i += 4) {
                const gray = (imageData[i] * 0.299 + imageData[i + 1] * 0.587 + imageData[i + 2] * 0.114);
                grays.push(gray);
                total += gray;
            }
            
            const avg = total / 64;
            let hashBin = '';
            
            // Map pixels to 1 or 0 based on average
            for (let i = 0; i < 64; i++) {
                hashBin += grays[i] >= avg ? '1' : '0';
            }
            
            // Convert 64-bit binary string to Hex
            let hashHex = '';
            for (let i = 0; i < 64; i += 4) {
                hashHex += parseInt(hashBin.substr(i, 4), 2).toString(16);
            }
            
            resolve(hashHex);
        };
        img.src = dataUrl;
    });
}