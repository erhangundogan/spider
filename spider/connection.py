import valkey
import os
import signal
import sys
import time
from valkey.cluster import ValkeyCluster
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class ValkeyConnection:
    """
    Valkey storage abstraction.
    """
    valkey_client: Optional[valkey.Valkey] = field(default=None)
    pubsub: Optional[valkey.client.PubSub] = field(default=None)
    running: bool = field(default=True)

    def __post_init__(self) -> None:
        """Initialize signal handlers and Valkey connection after instance creation."""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        self.connect()

    def connect(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        retry_count = 0
        while retry_count < max_retries and self.running:
            try:
                print(f"[{datetime.now(timezone.utc)}] Attempting to connect to Valkey (attempt {retry_count + 1}/{max_retries})...")

                self.valkey_client = ValkeyCluster(host='valkey', port=6379, password='bitnami', protocol=3)
                self.valkey_client.ping()
                self.pubsub = self.valkey_client.pubsub(ignore_subscribe_messages=True)
                print(f"[{datetime.now(timezone.utc)}] Successfully connected to Valkey")
                return True
            except (valkey.ConnectionError, ConnectionResetError) as e:
                retry_count += 1
                if retry_count < max_retries and self.running:
                    print(f"[{datetime.now(timezone.utc)}] Failed to connect to Valkey: {str(e)}")
                    print(f"[{datetime.now(timezone.utc)}] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"[{datetime.now(timezone.utc)}] Failed to connect to Valkey after {max_retries} attempts.")
                    return False
            except Exception as e:
                print(f"[{datetime.now(timezone.utc)}] Unexpected error while connecting to Valkey: {str(e)}")
                return False
            
    def _cleanup(self) -> None:
        """Clean up Valkey connections."""
        if self.valkey_client:
            try:
                self.valkey_client.close()
            except:
                pass

    def _handle_shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print(f"\n[{datetime.now(timezone.utc)}] Received shutdown signal. Cleaning up...")
        self.running = False
        self._cleanup()
        sys.exit(0)