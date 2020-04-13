from instapy import util


def test_has_any_letters():
    demo_data = {'Abcefg'}
    demo_data2 = {'15&593'}
    assert util.has_any_letters(demo_data) is True
    assert util.has_any_letters(demo_data2) is False


# print(has_any_letters('1234fasadadn'))



