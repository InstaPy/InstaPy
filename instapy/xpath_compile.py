#!/usr/bin/env python
# -*- coding: utf-8 -*-

xpath = {}

xpath['bypass_suspicious_login'] = []
xpath['bypass_suspicious_login'].append({
    "bypass_with_mobile_choice":"//label[@for='choice_0']",
    "bypass_with_mobile_button":"//label[@for='choice_0']",
    "choice":"//label[@for='choice_1']",
    "choice_no_such_element":"//label[@class='_q0nt5']",
    "choice_exception":"//label[@class='_q0nt5 _a7z3k']",
    "close_button":"[text()='Close']",
    "security_code_field":"//input[@id='security_code']",
    "send_security_code_button":"//button[text()='Send Security Code']",
    "submit_security_code_button":"//button[text()='Submit']",
    "this_was_me_button":"//button[@name='choice'][text()='This Was Me']",
    "wrong_login":["//p[text()='Please check the code we sent you and try ","again.']"]
}) #multiline:  wrong login

xpath['class_selectors'] = []
xpath['class_selectors'].append({
    "likes_dialog_body_xpath":"//h1[text()='Likes']/../../following-sibling::div/div",
    "likes_dialog_close_xpath":"//span[contains(@aria-label, 'Close')]"
})

xpath['confirm_unfollow'] = []
xpath['confirm_unfollow'].append({
    "button_xp": "//button[text()='Unfollow']"
})

xpath['dialog_username_extractor'] = []
xpath['dialog_username_extractor'].append({
    "person":"../../../*"
})

xpath['dismiss_get_app_offer'] = []
xpath['dismiss_get_app_offer'].append({
    "offer_elem": "//*[contains(text(), 'Get App')]",
    "dismiss_elem": "//*[contains(text(), 'Not Now')]"
})

xpath['dismiss_notification_offer'] = []
xpath['dismiss_notification_offer'].append({
    "offer_elem_loc": "//div/h2[text()='Turn on Notifications']",
    "dismiss_elem_loc": "//button[text()='Not Now']"
})

xpath['extract_information'] = []
xpath['extract_information'].append({
    "close_overlay":"//div/div[@role='dialog']",
    "one_pic_elem":["//section/main/article/div[1]/div/div[10]/div[",
                    "3]/a/div"],
    "like_element":"//a[@role='button']/span[text()='Like']/.."
}) #multiline:  one_pic_elem

xpath['extract_post_info'] = []
xpath['extract_post_info'].append({
    "comment_list":"//div/ul",
    "comments":"li",
    "load_more_comments_element":"//div/ul/li[2]/button",
    "load_more_comments_element_alt":"//div/ul/li[1]/button"
})

xpath['find_user_id'] = []
xpath['find_user_id'].append({
    "meta_XP":"//meta[@property='instapp:owner_user_id']"
})

xpath['get_active_users'] = []
xpath['get_active_users'].append({
    "latest_posts":"//div[contains(@class, '_9AhH0')]",
    "likers_count":"//div[contains(@class,'Nm9Fw')]/child::button/span",
    "likes_button":"//div[contains(@class,'Nm9Fw')]/child::button",
    "next_button":  ["//a[contains(@class, 'HBoOv')]",
                    "[text()='Next']"],
    "topCount_elements":"//span[contains(@class,'g47SY')]"
}) #multiline:  next_button

xpath['get_buttons_from_dialog'] = []
xpath['get_buttons_from_dialog'].append({
    "follow_button":"//button[text()='Follow']",
    "unfollow_button":"//button[text() = 'Following']"
})

xpath['get_comment_input'] = []
xpath['get_comment_input'].append({
    "comment_input": '//textarea[@placeholder = "Add a comment…"]',
    "placeholder": '//input[@placeholder = "Add a comment…"]'
})

xpath['get_comments_on_post'] = []
xpath['get_comments_on_post'].append({
    "commenter_elem":"//h3/a",
    "comments_block":"//div/div/h3/../../../..",
    "like_button_full_XPath":"//div/span/button/span[@aria-label='Like']",
    "unlike_button_full_XPath":"//div/span/button/span[@aria-label='Unlike']"
})

xpath['get_cord_location'] = []
xpath['get_cord_location'].append({
    "json_text":'//body'
})

xpath['get_following_status'] = []
xpath['get_following_status'].append({
    "follow_button_XP":"//button[text()='Following' or \
                                  text()='Requested' or \
                                  text()='Follow' or \
                                  text()='Follow Back' or \
                                  text()='Unblock']"
})

xpath['get_follow_requests'] = []
xpath['get_follow_requests'].append({
    "list_of_users":"//section/div",
    "view_more_button":"//button[text()='View More']"
})

xpath['get_given_user_followers'] = []
xpath['get_given_user_followers'].append({
    "followers_link":'//a[@href="/{}/followers/"]'
})

xpath['get_given_user_following'] = []
xpath['get_given_user_following'].append({
    "all_following":["//a[contains",
                    "(@href,'following')]/span"],
    "topCount_elements":"//span[contains(@class,'g47SY')]",
    "following_link":'//a[@href="/{}/following/"]'
}) #multiline:  all_following

xpath['get_photo_urls_from_profile'] = []
xpath['get_photo_urls_from_profile'].append({
    "photos_a_elems":"//div/a"
})

xpath['get_links_for_location'] = []
xpath['get_links_for_location'].append({
    "top_elements": "//main/article/div[1]",
    "main_elem": "//main/article/div[2]"
})

xpath['get_links_from_feed'] = []
xpath['get_links_from_feed'].append({
    "get_links": "//article/div[2]/div[2]/a"
})

xpath['get_links_for_tag'] = []
xpath['get_links_for_tag'].append({
    "top_elements": "//main/article/div[1]",
    "main_elem": "//main/article/div[2]",
    "possible_post": "//span[contains(@class, 'g47SY')]"
})

xpath['get_number_of_posts'] = []
xpath['get_number_of_posts'].append({
    "num_of_posts_txt":"//section/main/div/header/section/ul/li[1]/span/span",
    "num_of_posts_txt_no_such_element":"//section/div[3]/div/header/section/ul/li[1]/span/span"
})

xpath['get_relationship_counts'] = []
xpath['get_relationship_counts'].append({
    "following_count":  ["//a[contains",
                        "(@href,",
                        "'following')]/span"],
    "followers_count":  ["//a[contains",
                        "(@href,",
                        "'followers')]/span"],
    "topCount_elements":"//span[contains(@class,'g47SY')]"
}) #multiline: following_count, followers_count

xpath['get_source_link'] = []
xpath['get_source_link'].append({
    "image":'//img[@class="FFVAD"]',
    "image_alt": '//img[@class="_8jZFn"]',
    "video":'//video[@class="tWeCl"]'
})

xpath['get_users_through_dialog'] = []
xpath['get_users_through_dialog'].append({
    "find_dialog_box":"//body/div[3]/div/div[2]"
})

xpath['is_private_profile'] = []
xpath['is_private_profile'].append({
    "is_private":'//h2[@class="_kcrwx"]'
})

xpath['like_comment'] = []
xpath['like_comment'].append({
    "comments_block": "//div/div/h3/../../../..",
    "span_like_elements": "//span[@aria-label='Like']",
    "comment_like_button": ".."
})

xpath['like_image'] = []
xpath['like_image'].append({
    "like": "//section/span/button/span[@aria-label='Like']",
    "unlike": "//section/span/button/span[@aria-label='Unlike']"
})

xpath['like_from_image'] = []
xpath['like_from_image'].append({
    "main_article": "//main//article//div//div[1]//div[1]//a[1]"
})

xpath['login_user'] = []
xpath['login_user'].append({
    "input_password":"//input[@name='password']",
    "input_username_XP":"//input[@name='username']",
    "login_elem":"//a[text()='Log in']",
    "login_elem_no_such_exception":"//a[text()='Log In']",
    "nav":'//nav'
})

xpath['open_comment_section'] = []
xpath['open_comment_section'].append({
    "comment_elem":"//button/span[@aria-label='Comment']"
})

xpath['unfollow'] = []
xpath['unfollow'].append({
    "following_link":'//section//ul//li[3]',
    "find_dialog_box":"//div[text()='Following']/../../../following-sibling::div"
})