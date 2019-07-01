from instapy.blacklist import Blacklist
from instapy import InstaPy
import os
import unittest
import shutil
from instapy import set_workspace
from instapy import file_manager

class TestBlacklist(unittest.TestCase):
    """Update user name and password below. Tests run in PyCharm CE, but I can't seem to get them working from the command line at the moment"""
    @classmethod
    def setUpClass(cls):
        username = ''
        password = ''
        cls.test_dir =  "{}/_instapy_test".format(file_manager.get_home_path())
        cls.test_dir = file_manager.slashen(cls.test_dir, 'native')
        set_workspace(path=cls.test_dir)
        cls.session = InstaPy(username=username, password=password, bypass_suspicious_attempt=True, headless_browser=True)
        cls.blacklist = Blacklist(
            enabled=True, campaign="test",
            logfolder=cls.session.logfolder, logger=cls.session.get_instapy_logger(show_logs=False))

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_a_blacklist_csv_creation(self):
        self.blacklist.init()
        csv = "{}blacklist.csv".format(TestBlacklist.session.logfolder)
        self.assertTrue(os.path.isfile(csv))

    def test_b_add_and_get_entries(self):
        for x in  range(0,10):
            TestBlacklist.blacklist.add_entry(username="pressplay", action="liked")
            TestBlacklist.blacklist.add_entry(username="pressplay", action="followed")
        users = TestBlacklist.blacklist.get_users('test')
        self.assertIn('pressplay', users)

    def test_c_entry_exists(self):
        self.assertFalse(TestBlacklist.blacklist.entry_exists(username="pressplay", action="commented"))
        self.assertTrue(TestBlacklist.blacklist.entry_exists(username="pressplay", action="followed"))
        TestBlacklist.blacklist.add_entry(username="pressplay", action="commented")
        self.assertTrue(TestBlacklist.blacklist.entry_exists(username="pressplay", action="commented"))



