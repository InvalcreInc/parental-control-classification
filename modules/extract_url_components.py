from tld import get_tld
from os.path import splitext
from urllib.parse import urlparse, parse_qs
from requests import head
import csv
import random


class UrlComponents:
    '''
    This class is used to store the url components
    '''

    def __init__(self, is_https: bool, url: str):
        self.file_extension = ''
        self.domain = url
        self.path = ''
        self.tld = ''
        self.scheme = ''
        self.subdomain = ''
        self.query = ''
        self.has_redirect: bool = False
        self.is_https = is_https

    def set_extension(self, ext):
        if ext:
            self.file_extension = ext

    def set_domain(self, domain):
        if domain:
            self.domain = domain

    def set_path(self, path):
        if path:
            self.path = path

    def set_tld(self, tld):
        if tld:
            self.tld = tld

    def set_scheme(self, scheme):
        if scheme:
            self.scheme = scheme

    def set_subdomain(self, subdomain):
        if subdomain and subdomain != 'www':
            self.subdomain = subdomain

    def set_query(self, query):
        if query:
            self.query = query

    def set_redirect(self, has_redirect):
        self.has_redirect = has_redirect


def get_url_components(url: str, is_https: bool | None = None):
    '''
    This takes a url as input and returns a dictionary of url components
    '''
    is_https = check_https(url) if is_https is None else is_https
    components = UrlComponents(is_https, url=url)

    # normalise the url
    url = normalise_url(url, protocol=is_https and 'https' or 'http')
    components.set_extension(get_ext(url))

    # make a request to the url

    try:
        res = get_tld(url, as_object=True)
        components.set_subdomain(res.subdomain)
        components.set_domain(res.domain)
        components.set_tld(res.tld)

        # parse the response
        parsed_url = res.parsed_url
        components.set_scheme(parsed_url.scheme)
        components.set_path(parsed_url.path)
        components.set_query(parsed_url.query)
    except Exception as e:
        comps = use_url_parser(url)
        components.set_scheme(comps['scheme'])
        components.set_query(comps['query'])
        components.set_path(comps['path'])
        pass
    redirect = check_redirect(components.query)
    components.set_redirect(redirect)
    return components


def use_url_parser(url):
    scheme: str = ''
    query: str = ''
    params: str = ''
    path: str = ''
    try:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        query = parsed_url.query
        params = parsed_url.params
        path = parsed_url.path
    except:
        pass
    return {
        'scheme': scheme,
        'query': query,
        'params': params,
        'path': path
    }


def get_ext(url, path: str | None = None) -> str:
    '''
    This takes a url as input and returns the file extension
    '''
    try:
        url = url.lstrip("/")
        if url.startswith('//'):
            url = 'http:' + url
        elif not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        if not path:
            parsed_url = urlparse(url)
            path = parsed_url.path
        _, ext = splitext(path)
        ext = ext[1:].lower() if ext else ''
        return ext
    except:
        return ''


def safe_http_request(url):
    '''
    Safe http request, return None if there is an error.
    '''
    try:
        agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36']
        headers = {
            'User-Agent': random.choice(agents), }
        return head(url, headers=headers, allow_redirects=False, timeout=2)
    except Exception as e:
        return None


def check_redirect(query) -> bool:
    '''
    This takes a url as input and returns True if the url has a redirect
    '''
    if not query:
        return False
    try:
        res = parse_qs(query)
        for _, v in res.items():
            any_url = any([is_valid_url(url) for url in v])
            if any_url:
                return True
    except:
        pass
    return False


def check_https(url) -> bool:
    '''
    This takes a url as input and returns True if the url is https
    '''
    try:
        url = normalise_url(url, protocol='https')
        res = safe_http_request(url)
        return res.ok
    except:
        return False


def get_query(url):
    '''
    This takes a url as input and returns the query
    '''
    try:
        url = normalise_url(url)
        parsed_url = urlparse(url)
        query = parsed_url.query
        return query
    except:
        return ''


def normalise_url(url: str, protocol: str = 'http'):
    '''
    This takes a url as input and returns a normalised url
    '''
    try:
        url = url.strip()
        url.lower()
        url = url.lstrip("/")
        if url.startswith('//'):
            url = f'{protocol}:' + url
        elif not url.startswith(('http://', 'https://')):
            url = f'{protocol}://' + url
    except:
        pass
    return url


def is_valid_url(url):
    try:
        url = normalise_url(url)
        result = urlparse(url)
        if not result.netloc or '.' not in result.netloc:
            return False

        tld = result.netloc.split('.')[-1]
        return all([result.scheme, result.netloc, len(tld) > 1])
    except:
        return False


if __name__ == '__main__':
    with open("../data/mp_malicious_normalised.csv", 'r') as f:
        reader = csv.reader(f)
        next(reader)
        count = 0
        for row in reader:
            if random.choice([False, False, True, False]):
                continue
            url = row[0]
            print(get_url_components(url).__dict__)
            count += 1
            if count > 10:
                break
