from instapy import util


def get_data():
    return util


def has_any_letters(text):
    """ Check if the text has any letters in it """
    # result = re.search("[A-Za-z]", text)   # works only with english letters
    result = any(
        c.isalpha() for c in text
    )  # works with any letters - english or non-english

    return result


def test_has_any_letters(text):
    demo_data = {'Abcefg'}
    demo_data2 = {'15&593'}
    if has_any_letters(demo_data) == True:
        assert True
    if has_any_letters(demo_data2) == False:
        assert False


# print(has_any_letters('1234fasadadn'))



