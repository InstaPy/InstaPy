from instapy import InstaPy

session = InstaPy(username='test', password='test')
session.login()

for liked_image_page in session.like_by_feed_generator():
    username_of_image_poster = liked_image_page.browser.find_element_by_xpath('//article/header/div[2]/div[1]/div/a')\
        .get_attribute("title")

    # click likes of image
    liked_image_page.browser.find_element_by_xpath(
        "//main//div//div//article//div[2]/section[2]/div/a"
    ).click()

    # find likers
    likers = [
        liker.get_attribute('title')
        for liker in liked_image_page.browser.find_elements_by_xpath(
            "//div[@class='_ntka7']//li/div/div/div/div/a"
        )
    ]

    # like some posts of likers
    for liker in likers:
        if liker not in [username_of_image_poster, session.username]:
            liked_image_page.like_by_users([liker], randomize=True)

session.end()
