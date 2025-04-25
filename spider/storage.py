import valkey
from abc import abstractmethod
from page import Page
from datetime import datetime, timezone
from connection import ValkeyConnection

class ValkeyStorage(ValkeyConnection):
    client: valkey.Valkey

    def __init__(self, connection: ValkeyConnection):
        if connection.valkey_client is None:
            print(f"[{datetime.now(timezone.utc)}] Valkey client is not initialized.")
            raise Exception("Valkey client is not initialized.")
        else:
          self.client = connection.valkey_client

    @abstractmethod
    def save(self, page: Page):
        print(f"[{datetime.now(timezone.utc)}] Saving page with key: {page.key}")
        pass

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
