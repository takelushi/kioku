"""Lock Cache."""

import time
from types import TracebackType
from typing import Any, Optional, Type

from kioku.cache import Cache
from kioku.file_locker import FileLocker


class LockCache(Cache):
    """Lock Cache."""

    def __init__(self, path: str, lock_path: str, after_load=True) -> None:
        """Initialize object.

        Args:
            path (str): Cache file path.
            lock_path (str): Lock file path.
            after_load (bool): Don't load cache on initialize.
        """
        self.locker = FileLocker(lock_path)
        self.path = path
        self.auto_reload = False
        if after_load:
            self.cache = {}
        else:
            try:
                self.load_file()
            except FileNotFoundError:
                self.cache = {}

    def __enter__(self) -> 'LockCache':
        """Enter with statement.

        Returns:
            LockCache: LockCache.
        """
        for _ in range(100):
            self.locker.wait_unlock()
            try:
                self.locker.lock()
            except FileExistsError:
                time.sleep(0.1)
            else:
                break
        for _ in range(100):
            try:
                self.load_file()
            except FileNotFoundError:
                self.cache = {}
                break
            except EOFError:
                time.sleep(0.1)
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Exit with statement.

        Args:
            exc_type (Optional[Type[BaseException]]): Exception type.
            exc_value (Optional[BaseException]): Exception.
            traceback (Optional[TracebackType]): Traceback.
        """
        self.write_to_file()
        try:
            self.locker.unlock()
        except FileNotFoundError:
            pass

    def set(self, key: str, value: Any) -> None:  # noqa: A003
        """Set cache value.

        Args:
            key (str): Key name.
            value (Any): Value.
        """
        self.cache[key] = value
