import math
from os.path import splitext
from urllib.parse import urlparse
import tldextract
import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join('..')))


def extract_features(url):
    features = {}
    url = re.sub(r'[^\x00-\x7F]', '', url) 
    url = url.strip()
    #url = url if url.startswith(('http://', 'https://')) else 'http://' + url
    # URL Length
    features['url_length'] = len(url)

    # Extract domain and subdomain
    extracted = tldextract.extract(url)
    features['subdomain_count'] = len(
        extracted.subdomain.split('.')) if extracted.subdomain else 0
    features['domain_length'] = len(extracted.domain)

    # Domain entropy
    domain = extracted.domain + "." + extracted.suffix
    entropy = -sum((domain.count(c) / len(domain)) * math.log2(domain.count(c) / len(domain))
                   for c in set(domain)) if domain else 0
    features['domain_entropy'] = entropy

    # Common TLD
    tld = extracted.suffix
    features['is_common_tld'] = 1 if tld in [
        'com', 'org', 'net', 'edu', 'gov','ru'] else 0

    # Presence of special characters
    special_characters = re.findall(r'[@\-_.?&=]', url)
    features['special_character_count'] = len(special_characters)

    # Use of HTTPS
    features['is_https'] = 0 if url.lower().startswith('http://') else 1

    # Path Length and Depth
    parsed = urlparse(url)
    path = parsed.path
    features['path_length'] = len(path)
    features['path_depth'] = len([p for p in path.split('/') if p])

    # Query Parameters Count
    query = parsed.query
    features['query_param_count'] = len(query.split('&')) if query else 0

    # Suspicious query patterns
    suspicious_query = ['id=', 'page=', 'php?', 'admin=']
    features['has_suspicious_query'] = 1 if any(
        q in query.lower() for q in suspicious_query) else 0

    # Defacement keywords
    deface_keywords = ['hacked', 'defaced', 'admin', 'shell', 'hack']
    features['has_deface_keywords'] = 1 if any(
        kw in path.lower() or kw in query.lower() for kw in deface_keywords) else 0

    # Digit-to-letter ratio
    letters = len(re.findall(r'[a-zA-Z]', url))
    digits = len(re.findall(r'\d', url))
    features['digit_letter_ratio'] = digits / \
        (letters + 1) if letters + digits > 0 else 0

    # File extension
    features['file_extension'] = get_ext(path)

    return features


def get_ext(path) -> int:
    #parsed = urlparse(url)
    root, ext = splitext(path)
    ext = ext[1:].lower() if ext else ''
    return categorize_file_ext(ext)


def categorize_file_ext(ext) -> int:
    media = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
             'mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav', 'aac']
    doc = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
    html = ['html', 'htm', 'php', 'asp', 'js', 'css']
    archive = ['zip', 'rar', 'tar', 'gz', '7z']
    executables = ['exe', 'bat', 'cmd', 'sh']
    if not ext:
        return 0
    if ext in executables:
        return 1
    elif ext in archive:
        return 2
    elif ext in media:
        return 3
    elif ext in doc:
        return 4
    elif ext in html:
        return 5
    else:
        return 6  # Other/unknown
