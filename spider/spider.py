import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from dataclasses import dataclass
from socket import timeout
from page import Page
from typing import Any
from url_set import URL_Set
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen, build_opener, install_opener

VALKEY_CHAT_QUEUE_KEY = 'chat_queue'
VALKEY_CHAT_QUEUE_MESSAGE = 'chat_queue_updated'

def get_meta_dict(headers):
    out = {}
    for header in headers:
        if len(header) == 1:
            key = list(header.keys()).pop()
            value = header[key]
            out[key] = value
        else:
            keys = list(header.keys())
            keys.remove('content')
            key_name = keys.pop()
            key = header[key_name]
            value = header['content']
            out[key] = value
    return out

class Spider():
    #<scheme>://<netloc>/<path>;<params>?<query>#<fragment>

    def __init__(self, should_save=True):
        self.page = Page()
        self.should_save = bool(should_save or self.should_save)
        self.parsed_url = ()
        self.current_date_time = datetime.now(timezone.utc)
        self.current_html_content = ''

    def is_internal_link(self, url):
        unknown_link = urlparse(url)
        return bool(self.parsed_url.netloc == unknown_link.netloc)
    
    def save_to_file(self, content, path='/tmp'):
        first_part = self.parsed_url.netloc.replace('.', '_')
        second_part = self.parsed_url.path.replace("/", "_")
        file_name = f'{first_part}{second_part}.html'
        with open(f'{path}/{file_name}', 'w') as file:
            file.write(content)
            print(f"File saved at: {path}/{file_name}")
        return file_name
    
    def filter_word(self, word):
        lean_word = word.strip().lower()
        return re.sub(r'[^a-zA-Z]', '', lean_word)
    
    def extract_words(self):
        content = " ".join(self.page.texts)
        words = content.split(' ')
        filtered_words = map(self.filter_word, words)
        qualified_words = filter(lambda w: len(w) > 2, filtered_words)
        self.page.words = set(qualified_words)

    def extract_data(self, html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            meta_list = list(map(lambda m: m.attrs, soup.find_all('meta')))
            self.page.meta_tags = get_meta_dict(meta_list)
            whole_text = filter(str.strip, soup.body.get_text(separator=' ').split('\n'))
            filtered_text_list = []
            for w in whole_text:
                filtered_text_list.append(str.strip(w))
            self.page.texts = filtered_text_list
        except Exception as error:
            print(f"[{datetime.now(timezone.utc)}] Error extracting meta/content: {error}")

        links = soup.find_all('a', href=True)
        print(f"[{datetime.now(timezone.utc)}] Total links found: {len(links)}")

        for link in links:
            url = link['href'].lower().strip()

            if url == self.page.base_url or url == (self.page.base_url + '/'):
                continue

            # if it's malformed url or starts with other than http/https
            if not url or url.startswith('#') or url.startswith(('ftp','gopher', 'mailto', 'news', 'telnet', 'wais', 'file', 'prospero')):
                self.page.links_skipped.add(url)
                continue
            
            # if scheme is omitted
            if url.startswith('//'):
                url = url.replace('//', self.parsed_url.scheme + '://')
                if self.is_internal_link(url):
                    self.page.links_internal.add(url)
                else:
                    self.page.links_external.add(url)
            # if it starts with http/https
            elif url.startswith('http'):
                if self.is_internal_link(url):
                    self.page.links_internal.add(url)
                else:
                    self.page.links_external.add(url)
            else:
                if url.find('://') >= 0:
                    self.page.links_skipped.add(url)
                    continue

                # when it's an absolute path e.g. /path/to/resource
                if url.startswith('/'):
                    if self.page.base_url.endswith('/'):
                        url = self.page.base_url + url[1:]
                    else:
                        url = self.page.base_url + url
                # when it's a relative path e.g. path/to/resource
                # TODO: totally something else e.g. custom app protocol foo://
                else:
                    if self.page.base_url.endswith('/'):
                        url = self.page.base_url + url
                    else:
                        url = self.page.base_url + '/' + url
                
                if self.is_internal_link(url):
                    self.page.links_internal.add(url)
                else:
                    self.page.links_external.add(url)

    def crawl(self, base_url=None):
        if base_url is None:
            print(f"[{datetime.now(timezone.utc)}] Base URL is not set.")
            return

        self.page.base_url = base_url
        self.page.utc_date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        # etract url components
        self.parsed_url = urlparse(base_url)
        print(f"[{datetime.now(timezone.utc)}] Processing: {base_url}")

        try:
            request_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9,tr;q=0.8,ru;q=0.7,fr;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            # adjust headers for the request
            opener = build_opener()
            opener.headers = request_headers
            install_opener(opener)
            self.current_date_time = datetime.now(timezone.utc)

            try:
                # set context to validate SSL/TLS
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                result = urlopen(base_url, timeout=10.0, context=context)
                self.current_html_content = result.read().decode('utf-8', errors='ignore')

                if self.should_save:
                    # save the content to a file
                    print(f"[{datetime.now(timezone.utc)}] Saving content to the file.")
                    self.page.file_name = self.save_to_file(self.current_html_content)

                for header in result.info():
                    self.page.response_headers[header] = result.info()[header]
                self.page.content_length = self.page.response_headers.get('Content-Length') or len(self.html)
                self.extract_data(self.current_html_content)
                self.extract_words()
                diff = datetime.now(timezone.utc) - self.current_date_time
                self.page.duration = diff.total_seconds()
                print(f"[{datetime.now(timezone.utc)}] Crawling finished in {self.page.duration} seconds.")
                self.page.key = f'{{{self.parsed_url.netloc}}}:{self.parsed_url.path or "/"}'

                return self.page

            except HTTPError as error:
                print(f"[{datetime.now(timezone.utc)}] HTTPError fetching {base_url}: {error}")
            except URLError as error:
                if isinstance(error.reason, timeout):
                    print(f"[{datetime.now(timezone.utc)}] Timeout Error: Data of {base_url} not retrieved because of error: {error}")
                else:
                    print(f"[{datetime.now(timezone.utc)}] URLError fetching {base_url}: {error}")
            else:
                print(f"[{datetime.now(timezone.utc)}] Crawling completed for {base_url}")
  
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] Error fetching {base_url}: {e}")

    def run_playwright(self):      
        try:
            os.environ['SPIDER_PAGE_URL'] = self.page.base_url
            current_path = Path(__file__).resolve().parent.parent
            script_path = os.path.join(current_path, 'browser')
            print(f'Running browser script for {self.page.base_url} at {script_path}')
            os.chdir(script_path)
            scrap = subprocess.Popen(['yarn', 'start'], stdout=subprocess.PIPE)
            scrap.wait()
            file_path = scrap.stdout.read().decode('utf-8').strip()
            content = self.read_from_file(file_path)
            if content is None:
                print(f"Error: No content found in {file_path}")
                sys.exit(1)
            else:
                self.extract_data(content)
        except Exception as error:
            print(f"[{datetime.now(timezone.utc)}] Error running browser script: {error}")
            sys.exit(1)

if __name__ == "__main__":
    spider = Spider()
    page = spider.crawl("https://example.com")
    print(page)
