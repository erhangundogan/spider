import os
import re
import ssl
import sys
import datetime
from url_set import URL_Set
from socket import timeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen, build_opener, install_opener
from bs4 import BeautifulSoup

class Spider:
    #<scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    #subdomain_links = set()
    links = {
        'internal': URL_Set(),
        'external': URL_Set(),
        'skipped': URL_Set(),
        'exposed': URL_Set()
    }
    html = ''
    meta = []
    content = []
    headers = {}
    request_time = 0
    duration = 0
    content_length = 0
    base_url = ''
    _parsed_url: () = ()

    def __init__(self, base_url):
        self.base_url = base_url
        self._parsed_url = urlparse(base_url)

    def is_internal_link(self, url):
        unknown_link = urlparse(url)
        return bool(self._parsed_url.netloc == unknown_link.netloc)
    
    def save_to_file(self, content):
        first_part = self._parsed_url.netloc.replace('.', '_')
        second_part = self._parsed_url.path.replace("/", "_")
        file_name = f'{first_part}{second_part}.html'
        with open(f'/tmp/{file_name}', 'w') as file:
            file.write(content)
            print(f"File saved as: /tmp/{file_name}")

    def extract_data(self, html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            self.meta = list(map(lambda m: m.attrs, soup.find_all('meta')))
            whole_text = filter(str.strip, soup.body.get_text(separator=' ').split('\n'))
            filtered_text_list = []
            for w in whole_text:
                filtered_text_list.append(str.strip(w))
            self.content = filtered_text_list
        except Exception as error:
            print(f"Error extracting meta/content: {error}")

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
            opener = build_opener()
            opener.headers = request_headers
            install_opener(opener)
            self.request_time = datetime.datetime.now()

            try:
                # set context to velaite SSL/TLS
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                # open the url
                result = urlopen(current_url, timeout=10.0, context=context)
                # read the content of the url and decode it
                self.html = result.read().decode('utf-8', errors='ignore')
                for header in result.info():
                    self.headers[header] = result.info()[header]
                self.content_length = self.headers.get('Content-Length') or len(self.html)
                self.extract_data(self.html)
                self.save_to_file(self.html)
                diff = datetime.datetime.now() - self.request_time
                self.duration = diff.total_seconds()

                return { 
                    'duration': self.duration, 
                    'headers': self.headers,
                    'size': self.content_length,
                    'meta': self.meta,
                    'content': self.content,
                    'links': self.links
                }

            except HTTPError as error:
                print(f'HTTPError fetching {current_url}: {error}')
            except URLError as error:
                if isinstance(error.reason, timeout):
                    print(f'Timeout Error: Data of {current_url} not retrieved because of error: {error}')
                else:
                    print(f'URLError fetching {current_url}: {error}')
            else:
                print(f'Crawling completed for {current_url}')
  
        except Exception as e:
            print(f"Error fetching {current_url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python spider.py <url>')
        sys.exit

    base_url = sys.argv[1]
    spider = Spider(base_url)
    result = spider.crawl()

    print(f'''
DURATION: {result['duration']} secs
---
HEADERS: {result['headers']}
---
CONTENT-LENGTH: {result['size']}
---
META: {result['meta']}
---
CONTENT: {' '.join(result['content'])}
---
    ''')

    count = 0
    print('INTERNAL LINKS')
    for link in result['links']['internal']:
        print(f'{count}: {link}')
        count += 1

    print('---')
    count = 0
    print('EXTERNAL LINKS')
    for link in result['links']['external']:
        print(f'{count}: {link}')
        count += 1

    print('---')
    count = 0
    print('SKIPPED LINKS')
    for link in result['links']['skipped']:
        print(f'{count}: {link}')
        count += 1

    print('---')
    if len(result['links']['exposed']) > 0:
        count = 0
        print('EXPOSED LINKS')
        for link in result['links']['exposed']:
            print(f'{count}: {link}')
            count += 1
