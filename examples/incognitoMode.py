from instapy import InstaPy

insta_username = ''
insta_password = ''


session = InstaPy(username=insta_username, password=insta_password, incognito_mode=True)
session.login()


session.set_user_interact(amount=5, random=True, percentage=80, media='Photo')
session.set_do_like(enabled=True, percentage=80)
session.set_comments(["Nice!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_following(['world'], amount=100, random=True)

# end the bot session
session.end()
