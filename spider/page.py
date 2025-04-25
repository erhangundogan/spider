from url_set import URL_Set
from uuid import uuid4

class Page():
    id: str = uuid4()
    key: str = ''
    base_url: str = ''
    file_name: str = ''
    request_date_time: str = ''
    meta_tags: dict = {}
    text_content: list = []
    html_content: str = ''
    response_headers: dict = {}
    duration: float = 0.0
    content_length: int = 0
    links_internal: URL_Set = URL_Set()
    links_external: URL_Set = URL_Set()
    links_skipped: URL_Set = URL_Set()
    links_exposed: URL_Set = URL_Set()

    def __repr__(self):
        count = 0
        internal_links = ''
        for link in self.links_internal:
            internal_links += f'{count}: {link}'
            count += 1

        count = 0
        external_links = ''
        for link in self.links_external:
            external_links += f'{count}: {link}'
            count += 1

        count = 0
        skipped_links = ''
        for link in self.links_skipped:
            skipped_links += f'{count}: {link}'
            count += 1

        count = 0
        exposed_links = ''
        for link in self.links_exposed:
            exposed_links += f'{count}: {link}'
            count += 1

        result = f'''
id: {self.id}
key: {self.key}
file_name: {self.file_name}
base_url: {self.base_url}
response_headers: {self.response_headers}
request_date_time: {self.request_date_time}
duration: {self.duration} secs
content_length: {self.content_length}
meta_tags: {self.meta_tags}
text_content: {' '.join(self.text_content)}
links_internal: {self.links_internal}
links_external: {self.links_external}
links_skipped: {self.links_skipped}
links_exposed: {self.links_exposed}
        '''
        return result
