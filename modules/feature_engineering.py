from collections import Counter
import csv
import math
from os.path import splitext
from urllib.parse import urlparse
import re
import sys
import os
from tld import get_tld, get_fld


sys.path.append(os.path.abspath(os.path.join('..')))


def feature_engineering(url: str):
    '''
    This function takes a url as input and returns a dictionary of features
    '''
    features = {}
    url = clean_url(url)
    components = get_url_components(url)
    domain = components['domain']
    path = components['path']
    query = components['query']
    tld = components['tld']

    # domain info
    # domain_info = get_domain_info(domain)
    # features['domain_age'] = domain_info['domain_age']
    # features['domain_status'] = domain_info['status']

    #
    features['shortening_service'] = shortening_service(url)
    features['file_extension'] = get_ext(path)
    features['domain_entropy'] = entropy(domain)

    features['special_characters_count'] = special_characters_count(url)
    features['suspicious_query'] = contains_suspicious_query(query)
    features['is_common_tld'] = is_common_tld(tld)

    features['domain_length'] = len(domain if domain else '')
    features['url_length'] = len(url)
    features['is_https'] = is_https(url)
    features['is_http'] = is_http(url)
    features['sensitive_words'] = contains_sensitive_words(url)
    return features


def clean_url(url: str) -> str:
    url = re.sub(r'[^\x00-\x7F]', '', url)
    url = url.strip()
    return url.lower()


def get_url_components(url: str):
    domain: str = ''
    query: str = ''
    path: str = ''
    tld: str = ''
    try:
        res = get_tld(url, fail_silently=True,
                      fix_protocol=True, as_object=True)
        parsed_url = res.parsed_url
        domain = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query
        tld = res.tld
    except:
        pass
    return {
        'domain': domain,
        'path': path,
        'query': query,
        'tld': tld
    }


def special_characters_count(url: str) -> int:
    pattern = r'[@%=+&#]|%[0-9A-Fa-f]{2}'
    special_characters = re.findall(pattern, url)
    return len(special_characters)


def is_common_tld(tld) -> int:
    '''
    Checks if the tld is a common tld e.g com
    '''
    if not tld:
        return 0
    with open('../data/common_tlds.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == tld:
                return 1
    return 0


def contains_sensitive_words(url: str) -> int:
    '''
    Malicious URLs contain sensitive words
    '''
    words = 0
    with open('../data/sensitive_words.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] in url:
                words += 1
    return words


def contains_suspicious_query(queries: str) -> int:
    if not queries:
        return 0

    with open('../data/suspicious_queries.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] in queries:
                return 1
    return 0


def is_https(url: str) -> int:
    return 1 if 'https://' in url else 0


def is_http(url: str) -> int:
    return 1 if 'http://' in url else 0


def entropy(url: str) -> float:
    '''
    Calculates the entropy of a url
    - URLs with high entropy are significant indicators of malicious behavior
    - where H(x) is the Shannon entropy of string x, b is the base of the logarithm used, and p(x) is the probability mass function.
    source: https://www.mdpi.com/1099-4300/23/2/182
    '''
    if not url:
        return 0
    length = len(url) if url else 0
    counts = Counter(url)
    return -sum((count/length) * math.log2(count/length)
                for count in counts.values())


def shortening_service(url) -> int:
    '''
    Checks if the url is a shortening service 
    '''
    with open('../data/shorturl-services-list.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] in url:
                return 1
    return 0


def get_ext(path) -> int:
    root, ext = splitext(path)
    ext = ext[1:].lower() if ext else ''
    return categorize_file_ext(ext)


def categorize_file_ext(ext: str) -> int:
    media = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
             'mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav', 'aac']
    doc = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
    web = ['html', 'htm', 'php', 'asp', 'js', 'css', 'aspx', 'json', 'xml']
    archive = ['zip', 'rar', 'tar', 'gz', '7z']
    executables = {'exe', 'bat', 'cmd', 'sh', 'msi', 'scr', 'vbs', 'pif', 'com', 'ps1',
                   'app', 'jar', 'py', 'dll', 'lnk'}
    ext = ext.lower().strip()
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
    elif ext in web:
        return 5
    else:
        return 6


# print(get_domain_info(
#    'https://x.com'))
