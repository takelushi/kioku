"""File Locker."""

import datetime
import os
import time
from types import TracebackType
from typing import Optional, Type


class FileLocker:
    """File locker."""

    def __init__(self, path: str, max_wait=60) -> None:
        """Initialize object.

        Args:
            path (str): Lock file path.
            max_wait (int): Max wait seconds. Default to 60.
        """
        self.path = path
        self.max_wait = max_wait

    def __enter__(self) -> 'FileLocker':
        """Enter with statement.

        Returns:
            FileLocker: FileLocker.
        """
        self.wait_unlock()
        self.lock()
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
        self.unlock()

    def wait_unlock(self) -> None:
        """Wait unlock.

        Raises:
            RuntimeError: Reached max wait time.
        """
        start_time = time.monotonic()
        duration = 0.1
        while True:
            if not os.path.exists(self.path):
                break
            time.sleep(duration)

            if time.monotonic() - start_time > self.max_wait:
                raise RuntimeError('Reached max time to wait unlock.')

    def lock(self) -> None:
        """Lock.

        Raises:
            FileExistsError: Lock file already exist.
        """
        if os.path.exists(self.path):
            raise FileExistsError('Cannot lock. Lock file already exist.')
        dt_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        with open(self.path, 'w', encoding='UTF-8') as f:
            f.write(dt_str)

    def unlock(self) -> None:
        """Unlock.

        Raises:
            FileNotFoundError: Lock file was not found.  # noqa: DAR402
        """
        # raise FileNotFoundError
        os.remove(self.path)
