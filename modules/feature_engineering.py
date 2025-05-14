
from collections import Counter
import csv
import math
import re
import sys
import os
from urllib.parse import parse_qs
import random
# from tldextract import extract


sys.path.append(os.path.abspath(os.path.join('..')))
from modules.extract_url_components import get_url_components

def feature_engineering(url: str, is_https: bool | None = None):
    '''
    This function takes a url as input and returns a dictionary of features
    '''
    features = {}
    url = clean_url(url)
    components = get_url_components(url, is_https)

    #
    features['shortening_service'] = shortening_service(url)
    features['file_extension'] = categorize_file_ext(
        components.file_extension)
    features['domain_entropy'] = entropy(components.domain)
    features['redirects'] = 1 if components.has_redirect else 0

    features['subdomains_count'] = subdomains_count(components.subdomain)

    features['digits_count'] = digits_count(url)
    features['queries_count'] = query_counts(components.query)
    features['special_characters_count'] = special_characters_count(url)
    features['suspicious_query'] = contains_suspicious_query(components.query)
    features['is_common_tld'] = is_common_tld(components.tld)

    features['domain_length'] = len(components.domain)
    features['url_length'] = len(url)
    features['is_https'] = 1 if components.is_https else 0
    features['sensitive_words'] = contains_sensitive_words(url)
    return features


def clean_url(url: str) -> str:
    url = re.sub(r'[^\x00-\x7F]', '', url)
    url = url.strip()
    return url.lower()


def subdomains_count(subdomains: str) -> int:
    if not subdomains:
        return 0
    subdomains_parts = subdomains.strip().split('.')
    return len(subdomains_parts)


def special_characters_count(url: str) -> int:
    pattern = r'[@%$*=+&#_-]|%[0-9A-Fa-f]{2}'
    special_characters = re.findall(pattern, url)
    return len(special_characters)


def is_common_tld(tld: str | None) -> int:
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


def digits_count(url: str) -> int:
    '''
    Counts the number of digits in a url
    '''
    return len(re.findall(r'\d', url))


def query_counts(query_str: str) -> int:
    '''
    Counts the number of queries in a url.
    - Malicious URLs contain more queries
    '''
    return len(parse_qs(query_str).keys())


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


def entropy(domain: str) -> float:
    '''
    Calculates the entropy of a url
    - URLs with high entropy are significant indicators of malicious behavior
    - where H(x) is the Shannon entropy of string x, b is the base of the logarithm used, and p(x) is the probability mass function.
    source: https://www.mdpi.com/1099-4300/23/2/182
    '''
    if not domain:
        return 0
    length = len(domain) if domain else 0
    counts = Counter(domain)
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


def categorize_file_ext(ext: str) -> int:
    media = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
             'mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav', 'aac']
    doc = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
    web = ['html', 'htm', 'php', 'asp', 'js', 'css', 'aspx', 'json', 'xml']
    archive = ['zip', 'rar', 'tar', 'gz', '7z']
    executables = {'exe', 'bat', 'cmd', 'sh', 'msi', 'scr', 'vbs', 'pif', 'com', 'ps1',
                   'app', 'jar', 'py', 'dll', 'lnk', 'bin'}
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


if __name__ == '__main__':
    with open("../data/mp_malicious_normalised.csv", 'r') as f:
        reader = csv.reader(f)
        next(reader)
        count = 0
        for row in reader:
            if random.random() < 0.55:
                continue
            url = row[0]
            print(url, feature_engineering(url))
            count += 1
            if count > 10:
                break
