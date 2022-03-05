"""Test file locker."""

from multiprocessing import Process
import os
import pathlib
import time
from typing import Union

import pytest

from kioku.file_locker import FileLocker


def create_lock_file(path: Union[str, pathlib.PosixPath]) -> None:
    """Create lock file.

    Args:
        path ( Union[str, pathlib.PosixPath]): File path.
    """
    with open(path, 'w', encoding='UTF-8') as f:
        f.write('lock')


class TestFileLocker:
    """Test FileLocker."""

    def test_init(self) -> None:
        """Test __init__()."""
        locker = FileLocker('path.txt')
        assert isinstance(locker, FileLocker)

    def test_with(self, tmp_path: pathlib.PosixPath) -> None:
        """Test with statement.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'
        with FileLocker(path) as locker:
            assert isinstance(locker, FileLocker)
            assert os.path.exists(path)
        assert not os.path.exists(path)

    def test_wait_unlock(self, tmp_path: pathlib.PosixPath) -> None:
        """Test wait_unlock().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'

        create_lock_file(path)

        def target():
            time.sleep(1)
            os.remove(path)

        locker = FileLocker(path)

        p = Process(target=target)
        p.start()

        locker.wait_unlock()

    def test_wait_unlock_over_max_wait(self,
                                       tmp_path: pathlib.PosixPath) -> None:
        """Test wait_unlock().

        When over max wait time.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'

        create_lock_file(path)

        locker = FileLocker(path, max_wait=1)
        with pytest.raises(RuntimeError):
            locker.wait_unlock()

    def test_lock(self, tmp_path: pathlib.PosixPath) -> None:
        """Test lock().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'
        locker = FileLocker(path)
        locker.lock()
        assert os.path.exists(path)

    def test_lock_file_exists(self, tmp_path: pathlib.PosixPath) -> None:
        """Test lock().

        When lock file already exists.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'
        create_lock_file(path)
        locker = FileLocker(path)

        with pytest.raises(FileExistsError):
            locker.lock()

    def test_unlock(self, tmp_path: pathlib.PosixPath) -> None:
        """Test unlock().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'
        locker = FileLocker(path)
        locker.lock()
        locker.unlock()
        assert not os.path.exists(path)

    def test_unlock_file_not_exists(self, tmp_path: pathlib.PosixPath) -> None:
        """Test unlock().

        When lock file is not exists.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        path = tmp_path / '.lock'
        locker = FileLocker(path)

        with pytest.raises(FileNotFoundError):
            locker.unlock()()
