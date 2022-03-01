"""Test cache."""

import pathlib
import pickle
import threading
from typing import NoReturn
from unittest.mock import MagicMock

import pytest

from kioku.cache import Cache


class TestCache:
    """Test Cache class."""

    def test_init(self, tmp_path: pathlib.PosixPath) -> None:
        """Test __init__().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        _ = Cache(cache_path)

    def test_init_exist_cache(self, tmp_path: pathlib.PosixPath) -> None:
        """Test __init__().

        Cache file already exist.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        key, value = 'test', 123
        with open(cache_path, 'wb') as f:
            pickle.dump({key: value}, f)

        cache = Cache(cache_path)
        assert cache.get(key) == value

    @pytest.mark.skip(reason='Test on test_init_exist_cache().')
    def test_load_file(self) -> NoReturn:
        """Test load_file()."""

    def test_write_to_file(self, tmp_path: pathlib.PosixPath) -> None:
        """Test write_to_file().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        key, value = 'test', 123

        cache = Cache(cache_path)
        cache.set(key, value)
        cache.write_to_file()

        new_cache = Cache(cache_path)
        assert new_cache.get(key) == value

    @pytest.mark.skip(reason='Test on test_write_to_file().')
    def test_set(self) -> NoReturn:
        """Test set()."""

    @pytest.mark.skip(reason='Test on test_write_to_file().')
    def test_get(self) -> NoReturn:
        """Test get()."""

    def test_clear(self, tmp_path: pathlib.PosixPath) -> None:
        """Test clear().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        key, value = 'test', 123

        cache = Cache(cache_path)
        cache.set(key, value)
        cache.clear(key)

        assert cache.get(key) is None

    def test_clear_unexist_key(self, tmp_path: pathlib.PosixPath) -> None:
        """Test clear().

        Clear unexist key.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        key = 'test'

        cache = Cache(cache_path)
        cache.clear(key)

        assert cache.get(key) is None

    def test_use(self, tmp_path: pathlib.PosixPath) -> None:
        """Test use().

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        cache = Cache(cache_path)
        return_value = 123

        call = MagicMock()

        @cache.use()
        def f():
            call()
            return return_value

        assert f() == return_value
        assert cache.get('f') == return_value
        assert f() == return_value
        assert cache.get('f') == return_value
        assert f() == return_value
        assert cache.get('f') == return_value

        assert call.call_count == 1

    def test_use_name(self, tmp_path: pathlib.PosixPath) -> None:
        """Test use().

        With name argument.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        cache = Cache(cache_path)
        key, value = 'test', 123

        call = MagicMock()

        @cache.use(name=key)
        def f():
            call()
            return value

        assert f() == value
        assert cache.get(key) == value
        assert f() == value
        assert cache.get(key) == value
        assert f() == value
        assert cache.get(key) == value

        assert call.call_count == 1

    def test_use_clear(self, tmp_path: pathlib.PosixPath) -> None:
        """Test use().

        Call clear and recall.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        cache = Cache(cache_path)
        return_value = 123

        call = MagicMock()

        @cache.use()
        def f():
            call()
            return return_value

        assert f() == return_value
        cache.clear('f')
        assert f() == return_value
        cache.clear('f')
        assert f() == return_value

        assert call.call_count == 3

    def test_auto_reload(self, tmp_path: pathlib.PosixPath) -> None:
        """Test auto_reload.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        cache_1 = Cache(cache_path, auto_reload=True)
        cache_2 = Cache(cache_path, auto_reload=True)
        key, value = 'test', 123

        cache_1.set(key, value)
        assert cache_2.get(key) == value
        cache_2.clear(key)
        assert cache_1.get(key) is None

    @pytest.mark.skip(reason='Not implemented')
    def test_multithread(self, tmp_path: pathlib.PosixPath) -> None:
        """Test multithread.

        Args:
            tmp_path (pathlib.PosixPath): Temporary path.
        """
        cache_path = tmp_path / 'cache.pkl'
        cache = Cache(cache_path, auto_reload=True)

        v_li = list(range(100))
        key_li = [str(i) for i in v_li]

        def f(k, v):
            cache.set(k, v)

        thread_li = [
            threading.Thread(target=f, args=(k, v))
            for k, v in zip(key_li, v_li)
        ]

        for thread in thread_li:
            thread.start()

        for thread in thread_li:
            thread.join()

        cache.load_file()
        result = cache.cache
        assert len(result.keys()) == len(key_li)
        assert result == {k: v for k, v in zip(key_li, v_li)}
