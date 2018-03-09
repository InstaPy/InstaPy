import pytest

from instapy.util import format_number


@pytest.mark.parametrize('val,exp', [
    ('123', 123),
    ('1,234', 1234),
    ('12.3k', 12300),
    ('123k', 123000),
    ('12.3m', 12300000),
    ('123m', 123000000),
])
def test_format_number(val, exp):
    """parse representations to int"""
    assert format_number(val) == exp
