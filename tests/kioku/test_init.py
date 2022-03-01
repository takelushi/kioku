"""Test init."""

import os

import toml

import kioku


def test_version() -> None:
    """Test __version__."""
    pyproject_path = os.path.realpath(
        '{0}/../../../pyproject.toml'.format(__file__))
    with open(pyproject_path, 'r') as f:
        pyproject = toml.load(f)
    assert kioku.__version__ == pyproject['tool']['poetry']['version']
