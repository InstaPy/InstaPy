from instapy import InstaPy2
from instapy.engine import LegacyEngine

session = InstaPy2(driver_type="appium-driver")

LegacyEngine.follow_likers(session,
                           ["watermelodie"],
                           photos_grab_amount=2,
                           follow_likers_per_photo=10,
                           randomize=False,
                           interact=False)
