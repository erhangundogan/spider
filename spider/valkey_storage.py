import valkey
from abc import abstractmethod
from datetime import datetime, timezone
from enum import Enum
from .page import Page
from .connection import ValkeyConnection

class ValkeyType(Enum):
    HASH = 1
    LIST = 2
    SET = 3
    ZSET = 4
    STRING = 5

class ValkeyStorage:
    fields: dict = {
        'id': ValkeyType.STRING,
        'key': ValkeyType.STRING,
        'base_url': ValkeyType.STRING,
        'file_name': ValkeyType.STRING,
        'utc_date_time': ValkeyType.STRING,
        'meta_tags': ValkeyType.HASH,
        'texts': ValkeyType.LIST,
        'response_headers': ValkeyType.HASH,
        'duration': ValkeyType.STRING,
        'content_length': ValkeyType.STRING,
        'links_internal': ValkeyType.SET,
        'links_external': ValkeyType.SET,
        'links_skipped': ValkeyType.SET
    }

    def save(self, client, page: Page):
        if client is None:
            raise ValueError("Client is not connected to Valkey")
        
        for key, value in self.fields.items():
            storage_key = f"{page.key}:{key}"
            data = getattr(page, key)
            if data is None:
                continue
            match value:
                case ValkeyType.STRING:
                    client.set(storage_key, data)
                case ValkeyType.HASH:
                    client.hset(storage_key, mapping=data)
                case ValkeyType.LIST:
                    if len(data) > 0:
                        client.rpush(storage_key, *data)
                case ValkeyType.SET:
                    if len(data) > 0:
                        client.sadd(storage_key, *data)
                case ValkeyType.ZSET:
                    if len(data) > 0:
                        client.zadd(storage_key, *data)
                
        print(f"[{datetime.now(timezone.utc)}] Page saved with the key: {page.key}")

    @abstractmethod
    def get(self, id: str) -> Page:
        pass

    @abstractmethod
    def find(self, criteria: str, value: str) -> list[Page]:
        pass

    @abstractmethod
    def delete(self, id: str):
        pass

    @abstractmethod
    def update(self, id: str, page: Page):
        pass

    @abstractmethod
    def get_all(self, count: int, page: int) -> list[Page]:
        pass

    @abstractmethod
    def get_count(self) -> int:
        pass
