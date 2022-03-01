"""Test init."""

import pkg_name


def test_say_hello():
    """Test say_hello()."""
    assert pkg_name.say_hello() == 'Hello, world!'
