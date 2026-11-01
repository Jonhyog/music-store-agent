import pytest

from music_store.utils import is_numeric


@pytest.mark.parametrize("value", ["0", "42", "007"])
def test_digits_are_numeric(value):
    assert is_numeric(value)


@pytest.mark.parametrize("value", ["", "abc", "1.5", "-1", "1 2", "١٢"])
def test_everything_else_is_not(value):
    assert not is_numeric(value)
