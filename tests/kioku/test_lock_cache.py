"""Test lock cache."""

import os
import pathlib
import threading

from kioku.lock_cache import LockCache


class TestLockCache:
    """Test LockCache."""

    def test_init(self, tmp_path: pathlib.PosixPath) -> None:
        """Test __init__().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        lock_path = tmp_path / '.lock'
        _ = LockCache(cache_path, lock_path)

    def test_with(self, tmp_path: pathlib.PosixPath) -> None:
        """Test with statement.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        lock_path = tmp_path / '.lock'
        with LockCache(cache_path, lock_path):
            assert os.path.exists(lock_path)

        assert not os.path.exists(lock_path)

    def test_multithread(self, tmp_path: pathlib.PosixPath) -> None:
        """Test multithread.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        lock_path = tmp_path / '.lock'

        v_li = list(range(100))
        key_li = [str(i) for i in v_li]

        def f(k, v):
            with LockCache(cache_path, lock_path) as cache:
                cache.set(k, v)

        thread_li = [
            threading.Thread(target=f, args=(k, v))
            for k, v in zip(key_li, v_li)
        ]

        for thread in thread_li:
            thread.start()

        for thread in thread_li:
            thread.join()

        cache = LockCache(cache_path, lock_path, after_load=False)
        result = cache.cache
        assert len(result.keys()) == len(key_li)
        assert result == {k: v for k, v in zip(key_li, v_li)}
