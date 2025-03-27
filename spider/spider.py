import re 
import sys
import datetime
import http.cookiejar
from socket import timeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen, build_opener, install_opener, HTTPCookieProcessor
from bs4 import BeautifulSoup

class Spider:
    #<scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    #subdomain_links = set()
    links = {
        'internal': set(),
        'external': set(),
        'skipped': set(),
        'exposed': set()
    }
    charset = ''
    title = ''
    author = ''
    canonical = ''
    cookies = {}
    headers = {}
    description = ''
    requested_time = 0
    process_time = 0
    content_length = 0
    base_url = ''
    _parsed_url: () = ()

    def __init__(self, base_url):
        self.base_url = base_url
        self._parsed_url = urlparse(base_url)

    def is_internal_link(self, url):
        unknown_link = urlparse(url)
        return bool(self._parsed_url.netloc == unknown_link.netloc)

    def extract_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        try:
            self.charset = soup.original_encoding
            self.title = soup.find('title').string
            self.description = soup.find('meta', attrs={'name': 'description'})['content']
            self.author = soup.find('link', attrs={'rel': 'author'}).string
            self.canonical = soup.find('link', attrs={'rel': 'canonical'}).string
        except Exception as error:
            print(f"Error extracting meta data: {error}")

        links = soup.find_all('a', href=True)
        print(f"Total links found: {len(links)}")

        for link in links:
            url = link['href'].lower().strip()
            # check for user:password@
            if re.search("://(.*):(.*)@", url):
                self.links['exposed'].add(url)
                continue

            if not url or url.startswith('#') or url.startswith(('ftp','gopher', 'mailto', 'news', 'telnet', 'wais', 'file', 'prospero')):
                self.links['skipped'].add(url)
                continue
            
            if url.startswith('//'):
                url = url.replace('//', self._parsed_url.scheme + '://')
                if self.is_internal_link(url):
                    self.links['internal'].add(url)
                else:
                    self.links['external'].add(url)
            elif url.startswith('http'):
                if self.is_internal_link(url):
                    self.links['internal'].add(url)
                else:
                    self.links['external'].add(url)
            else:
                if url.startswith('/'):
                    if self.base_url.endswith('/'):
                        url = self.base_url + url[1:]
                    else:
                        url = self.base_url + url
                else:
                    if self.base_url.endswith('/'):
                        url = self.base_url + url
                    else:
                        url = self.base_url + '/' + url
                
                if self.is_internal_link(url):
                    self.links['internal'].add(url)
                else:
                    self.links['external'].add(url)

    def crawl(self):
        current_url = self.base_url
        print(f"Processing: {current_url}")

        try:
            request_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9,tr;q=0.8,ru;q=0.7,fr;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            cookiejar = http.cookiejar.CookieJar()
            cookie_handler = HTTPCookieProcessor(cookiejar)
            opener = build_opener(cookie_handler)
            opener.headers = request_headers
            install_opener(opener)
            self.requested_time = datetime.datetime.now()

            try:
                result = urlopen(current_url, timeout=10.0)
                self.cookies = cookiejar
                self.headers = result.info()
                html_content = result.read().decode('utf-8', errors='ignore')
                self.content_length = self.headers.get('Content-Length') or len(html_content)

                self.extract_data(html_content)
                print(f'Crawling completed for {current_url}')

                diff = datetime.datetime.now() - self.requested_time
                self.process_time = diff.total_seconds()

            except HTTPError as error:
                print(f'HTTPError fetching {current_url}: {error}')
            except URLError as error:
                if isinstance(error.reason, timeout):
                    print(f'Timeout Error: Data of {current_url} not retrieved because of error: {error}')
            else:
                print('Access succesful')
            
            
        except Exception as e:
            print(f"Error fetching {current_url}: {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    base_url = sys.argv[1] or "https://www.bbc.com"
    spider = Spider(base_url)
    spider.crawl()

    print(f'''
Crawl results:
Headers: {spider.headers}
Cookies: {spider.cookies}
Content-Length: {spider.content_length}
Request Time: {spider.requested_time}
Process time: {spider.process_time}
Title: {spider.title}
Description: {spider.description}
Author: {spider.author}
Canonical: {spider.canonical}
    ''')

    count = 0
    print('Internal links')
    for link in spider.links['internal']:
        print(f'{count}: {link}')
        count += 1

    count = 0
    print('External links')
    for link in spider.links['external']:
        print(f'{count}: {link}')
        count += 1

    count = 0
    print('Skipped links')
    for link in spider.links['skipped']:
        print(f'{count}: {link}')
        count += 1

    count = 0
    print('Exposed links')
    for link in spider.links['exposed']:
        print(f'{count}: {link}')
        count += 1
