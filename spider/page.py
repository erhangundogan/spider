import json
from sqlmodel import Field
from uuid import uuid4
from .url_set import URL_Set, URL_Set_Encoder

class Page():
    id: str | None = Field(default=uuid4().hex, primary_key=True)

    def __init__(self):
        self.id: str = uuid4().hex
        self.key: str = ''
        self.base_url: str = ''
        self.file_name: str = ''
        self.utc_date_time: str = ''
        self.meta_tags: dict = {}
        self.texts: list = []
        self.markdown: str = ''
        self.response_headers: dict = {}
        self.duration: float = 0.0
        self.content_length: int = 0
        self.links_internal: URL_Set = URL_Set()
        self.links_external: URL_Set = URL_Set()
        self.links_skipped: URL_Set = URL_Set()

    def to_json(self):
        return json.dumps(self.__dict__, cls=URL_Set_Encoder)

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

        result = f'''
id: {self.id}

key: {self.key}

file_name: {self.file_name}

base_url: {self.base_url}

response_headers: {self.response_headers}

utc_date_time: {self.utc_date_time}

duration: {self.duration} secs

content_length: {self.content_length}

meta_tags: {self.meta_tags}

texts: {self.texts}

links_internal: {self.links_internal}

links_external: {self.links_external}

links_skipped: {self.links_skipped}
        '''
        return result
