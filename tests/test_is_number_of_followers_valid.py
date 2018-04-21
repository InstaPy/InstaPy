from unittest import TestCase

from instapy.util import is_number_of_followers_valid


class TestIs_number_of_followers_valid(TestCase):
    def test_is_number_of_followers_valid_happy(self):
        number_followers = 300
        like_by_followers_upper_limit = 700
        like_by_followers_lower_limit = 100
        valid, text = is_number_of_followers_valid(number_followers,
                                     like_by_followers_upper_limit,
                                     like_by_followers_lower_limit)
        self.assertTrue(valid)
        self.assertIsNone(text)


    def test_is_number_of_followers_valid_too_low(self):
        number_followers = 99
        like_by_followers_upper_limit = 700
        like_by_followers_lower_limit = 100
        valid, text = is_number_of_followers_valid(number_followers,
                                                   like_by_followers_upper_limit,
                                                   like_by_followers_lower_limit)
        self.assertFalse(valid)
        self.assertEqual('Number of followers does not reach minimum', text)

    def test_is_number_of_followers_valid_lower_boundary_happy(self):
        number_followers = 100
        like_by_followers_upper_limit = 700
        like_by_followers_lower_limit = 100
        valid, text = is_number_of_followers_valid(number_followers,
                                                   like_by_followers_upper_limit,
                                                   like_by_followers_lower_limit)
        self.assertTrue(valid)
        self.assertIsNone(text)


    def test_is_number_of_followers_valid_too_high(self):
        number_followers = 701
        like_by_followers_upper_limit = 700
        like_by_followers_lower_limit = 100
        valid, text = is_number_of_followers_valid(number_followers,
                                                   like_by_followers_upper_limit,
                                                   like_by_followers_lower_limit)
        self.assertFalse(valid)
        self.assertEqual('Number of followers exceeds limit', text)

    def test_is_number_of_followers_valid_upper_boundary_happy(self):
        number_followers = 700
        like_by_followers_upper_limit = 700
        like_by_followers_lower_limit = 100
        valid, text = is_number_of_followers_valid(number_followers,
                                                   like_by_followers_upper_limit,
                                                   like_by_followers_lower_limit)
        self.assertTrue(valid)
        self.assertIsNone(text)
