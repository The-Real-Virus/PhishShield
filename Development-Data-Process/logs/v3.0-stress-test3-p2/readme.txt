Phase B: Adversarial Manual Testing ("Red Teaming")
Automated scripts test volume; manual testing tests intelligence. We will manually subject the extension to specific hacker evasion techniques.

The Obfuscation Test: Create a local phishing page where the word "Password" is written as an image, or uses zero-width characters (P&#8203;assword). Goal: See if the NLP fails and if Phase 3 catches it.

The Overlay Test: Create a legitimate page that has a malicious, transparent iframe floating over the screen. Goal: Test the structural extraction features.

The Redirect Chain Test: Use a URL shortener that redirects to an open redirect vulnerability on a trusted site, which then redirects to the phishing page. Goal: Ensure the extension analyzes the final landing page, not the shortener.
