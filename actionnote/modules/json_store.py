"""
JSON Store Module
Shared, thread-safe, atomic-write access to a JSON-backed data file.
"""
import json
import os
import tempfile
import threading
from contextlib import contextmanager
from typing import Callable, Dict


class JSONStore:
    """Thread-safe read/write access to a single JSON file.

    Locks are keyed by absolute path so multiple JSONStore instances
    pointing at the same file still serialize their access. This only
    guards against races within a single process (the storage model here
    doesn't support multiple processes writing the same file safely).
    """

    _locks_guard = threading.Lock()
    _locks: Dict[str, threading.Lock] = {}

    def __init__(self, path: str, default_factory: Callable[[], dict]):
        self.path = os.path.abspath(path)
        self.default_factory = default_factory
        self._ensure_exists()

    @classmethod
    def _lock_for(cls, path: str) -> threading.Lock:
        with cls._locks_guard:
            return cls._locks.setdefault(path, threading.Lock())

    def _ensure_exists(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path) or '.', exist_ok=True)
            self._atomic_write(self.default_factory())

    def _read_unlocked(self) -> dict:
        try:
            with open(self.path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_factory()

    def _atomic_write(self, data: dict) -> bool:
        dir_ = os.path.dirname(self.path) or '.'
        fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix='.tmp_', suffix='.json')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.path)
            return True
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def read(self) -> dict:
        """Read the current contents under the file's lock."""
        with self._lock_for(self.path):
            return self._read_unlocked()

    def write(self, data: dict) -> bool:
        """Overwrite the file's contents under the file's lock."""
        with self._lock_for(self.path):
            return self._atomic_write(data)

    @contextmanager
    def modify(self):
        """Read, yield the data for in-place mutation, then write it back --
        all under one lock acquisition, closing the read-then-write race that
        separate read()/write() calls leave open under concurrent access."""
        with self._lock_for(self.path):
            data = self._read_unlocked()
            yield data
            self._atomic_write(data)
