import re
import ipaddress
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tldextract

# --- 1. URL-Based Features (11 Features) ---

def having_IP(url):
    try:
        domain = urlparse(url).netloc
        ipaddress.ip_address(domain)
        return 1
    except ValueError:
        return 0

def URL_Length(url):
    return 1 if len(url) > 75 else 0

def Shortining_Service(url):
    shortening_services = [
        "bit.ly", "goo.gl", "shorte.st", "go2l.ink", "x.co", "ow.ly", "t.co", "tinyurl", "tr.im", "is.gd", "cli.gs", "yfrog.com", "migre.me", "ff.im", "tiny.cc", "url4.eu", "twit.ac", "su.pr", "twurl.nl", "snipurl.com", "short.to", "budurl.com", "ping.fm", "post.ly", "just.as", "bkite.com", "snipr.com", "fic.kr", "loopt.us", "doiop.com", "short.ie", "kl.am", "wp.me", "rubyurl.com", "om.ly", "to.ly", "bit.do", "t.co", "lnkd.in", "db.tt", "qr.ae", "adf.ly", "goo.gl", "bitly.com", "cur.lv", "tinyurl.com", "ow.ly", "bit.ly", "ity.im", "q.gs", "is.gd", "po.st", "bc.vc", "twitthis.com", "u.to", "j.mp", "buzurl.com", "cutt.us", "u.bb", "yourls.org", "x.co", "prettylinkpro.com", "scrnch.me", "filoops.info", "vzturl.com", "qr.net", "1url.com", "tweez.me", "v.gd", "tr.im", "link.zip.net"
    ]
    domain = urlparse(url).netloc
    for service in shortening_services:
        if service in domain:
            return 1
    return 0

def having_At_Symbol(url):
    return 1 if "@" in url else 0

def double_slash_redirecting(url):
    return 1 if url.rfind('//') > 7 else 0

def Prefix_Suffix(url):
    domain = urlparse(url).netloc
    return 1 if "-" in domain else 0

def having_Sub_Domain(url):
    ext = tldextract.extract(url)
    subdomain = ext.subdomain
    if not subdomain: return 0
    if subdomain == 'www': return 0
    return 1 if subdomain.count('.') > 0 else 0

# --- NEW HIGH-DEF FEATURES ---
def Hyphen_Count(url):
    domain = urlparse(url).netloc
    return domain.count('-')

def Dot_Count(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.count('.')

def Numeric_Chars(url):
    domain = urlparse(url).netloc
    return sum(c.isdigit() for c in domain)

def Is_Common_TLD(url):
    # 0 = Safe/Common, 1 = Risky/Uncommon
    common_tlds = ['com', 'org', 'net', 'edu', 'gov', 'uk', 'us', 'ca', 'au', 'de', 'fr', 'it', 'jp', 'io', 'co', 'ai']
    ext = tldextract.extract(url)
    return 0 if ext.suffix in common_tlds else 1


# --- 2. HTML & Content-Based Features (5 Features) ---

def get_html_features(url):
    feature_dict = {
        'SFH': 0,
        'Submitting_to_email': 0,
        'on_mouseover': 0,
        'RightClick': 0,
        'Iframe': 0
    }
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        html_lower = response.text.lower()

        # 1. SFH
        for form in soup.find_all('form'):
            action = form.get('action')
            if not action or action == "about:blank" or action == "":
                feature_dict['SFH'] = 1
                break

        # 2. Email
        for form in soup.find_all('form'):
            action = form.get('action')
            if action and "mailto:" in action:
                feature_dict['Submitting_to_email'] = 1
                break

        # 3. on_mouseover
        if "onmouseover" in html_lower:
            feature_dict['on_mouseover'] = 1

        # 4. RightClick
        if "event.button==2" in html_lower or "oncontextmenu" in html_lower:
            feature_dict['RightClick'] = 1

        # 5. Iframe
        if len(soup.find_all('iframe')) > 0:
            feature_dict['Iframe'] = 1

    except:
        pass 
    
    return feature_dict

# --- 3. Main Function (Exports 16 Features) ---
FINAL_FEATURE_LIST = [
    'having_IP', 'URL_Length', 'Shortining_Service', 'having_At_Symbol',
    'double_slash_redirecting', 'Prefix_Suffix', 'having_Sub_Domain',
    'Hyphen_Count', 'Dot_Count', 'Numeric_Chars', 'Is_Common_TLD',
    'SFH', 'Submitting_to_email', 'on_mouseover', 'RightClick', 'Iframe'
]

def extract_all_features(url):
    features = []
    
    # URL Features
    features.append(having_IP(url))
    features.append(URL_Length(url))
    features.append(Shortining_Service(url))
    features.append(having_At_Symbol(url))
    features.append(double_slash_redirecting(url))
    features.append(Prefix_Suffix(url))
    features.append(having_Sub_Domain(url))
    
    # New URL Features
    features.append(Hyphen_Count(url))
    features.append(Dot_Count(url))
    features.append(Numeric_Chars(url))
    features.append(Is_Common_TLD(url))

    # HTML Features
    html_f = get_html_features(url)
    features.append(html_f['SFH'])
    features.append(html_f['Submitting_to_email'])
    features.append(html_f['on_mouseover'])
    features.append(html_f['RightClick'])
    features.append(html_f['Iframe'])

    return features