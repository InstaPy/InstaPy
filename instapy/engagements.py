import time
import bot_util
from random import randint

from selenium.common.exceptions import NoSuchElementException

from .api_db import *
from .bot_util import getOperationByName, isOperationEnabled, getIfUserWantsToUnfollow
from .like_util import get_links_for_tag, check_link, get_links_for_location
from .like_util import like_image
from .unfollow_util import custom_unfollow, follow_user
from .util import validate_username
from .util import web_adress_navigator


def perform_engagement(self, operation, likeAmount, followAmount, engagement_by):
    self.logger.info("perform_engagement: STARTED operation. Going to perform %s likes, %s follow/unfollow," % (
    likeAmount, followAmount))

    iteration = 0
    likePerformed = 0
    followPerformed = 0

    likeAmountForEachTag = splitTotalAmount(self, likeAmount, len(operation['list']))
    followAmountForEachTag = splitTotalAmount(self, followAmount, len(operation['list']))

    # run while we have hashtags and the amount of likes and follow is not exceeded
    while shouldContinueLooping(self, operation, likePerformed, followPerformed, likeAmount, followAmount,iteration) is True:

        likeAmountForeachRandomized = randint(likeAmountForEachTag,
                                              bot_util.randomizeValue(likeAmountForEachTag, 10, "up"))
        followAmountForeachRandomized = randint(followAmountForEachTag,
                                                bot_util.randomizeValue(followAmountForEachTag, 10, "up"))

        engagementValue = getItemToProcess(operation, engagement_by)

        self.logger.info("perform_engagement: Going to perform %s amount of likes and %s of follow/unfollow for hashtag %s" % (likeAmountForeachRandomized, followAmountForeachRandomized, engagementValue))

        numberOfPostsToExtract = likeAmountForeachRandomized if likeAmountForeachRandomized >= followAmountForeachRandomized else followAmountForeachRandomized

        links = get_links(self=self, numberOfPostsToExtract=numberOfPostsToExtract, engagementBy=engagement_by,
                          engagementByValue=engagementValue)

        if len(links)==0:
            self.logger.info('perform_engagement: Too few images, skipping this tag:  %s', engagementValue)
            continue

        result = engage(self, links, engagementValue=engagementValue,
                        likeAmountToPerform=likeAmountForeachRandomized,
                        followAmountToPerform=followAmountForeachRandomized,
                        numberOfPostsToExtract=numberOfPostsToExtract,
                        engagement_by=engagement_by)

        likePerformed = likePerformed + result['likePerformed']
        followPerformed = followPerformed + result['followPerformed']

        iteration = iteration + 1

    return likePerformed


def shouldContinueLooping(self, operation, likePerformed, followPerformed, likeAmountExpected, followAmountExpected,iteration):
    securityBreak = 10

    if iteration > securityBreak:
        self.logger.info("shouldContinueLooping: Loop should stop: Security break, iteration: %s", iteration)
        return False

    if len(operation['list']) < 1:
        self.logger.info("shouldContinueLooping: Loop should stop: no more hashtags in the list")
        return False

    if likePerformed >= likeAmountExpected and followPerformed >= followAmountExpected:
        self.logger.info("shouldContinueLooping: Loop should stop: LP: %s, FP: %s, LE: %s, FE: %s" % (
            likePerformed, followPerformed, likeAmountExpected, followAmountExpected))
        return False

    return True


def engage(self, links, engagementValue, likeAmountToPerform, followAmountToPerform, numberOfPostsToExtract,
           engagement_by):
    result = {"likePerformed": 0, "followPerformed": 0}

    self.logger.info("engagement_by_tags: Received %s link, going to iterate through them", len(links))

    for i, link in enumerate(links):
        self.logger.info('engagement_by_tags: TAG {}, [{}/{}]'.format(engagementValue, i + 1, len(links)))

        try:
            # todo: check if this function is needed
            linkValidationDetails = canInteractWithLink(self, link)

            if linkValidationDetails is not False:

                # navigate to url ! (previously it was on user profile page)
                web_adress_navigator(self.browser, link)

                # TODO: create a method for the like code
                if likeAmountToPerform > 0:
                    liked = like_image(self.browser,
                                       linkValidationDetails['user_name'],
                                       self.blacklist,
                                       self.logger,
                                       self.logfolder)
                    if liked:
                        result['likePerformed'] += 1
                        self.logger.info(
                            "like_by_tags: Link %s was liked. User %s" % (link, linkValidationDetails['user_name']))

                        insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                        None, None, linkValidationDetails['user_name'],
                                        None, None, None,
                                        link, engagement_by, 'like_'+engagement_by, self.id_log)

                if followAmountToPerform > 0:
                    status = performFollowUnfollow(self, numberOfPostsToExtract, followAmountToPerform, link, engagementValue, linkValidationDetails['user_name'], engagement_by)
                    result['followPerformed'] += 1

        except NoSuchElementException as err:
            self.logger.error('Invalid Page: {}'.format(err))
            continue

    return result


def performFollowUnfollow(self, numberOfPostsToInteract, followAmount, link, tag, user_name, engagement_by):
    probabilityPercentage = followAmount * 100 // numberOfPostsToInteract

    calculatedProbability = randint(1, 100)

    self.logger.info(
        "performFollowUnfollow: Number of posts to interact: %s, followAmount: %s, probability: %s. Calculated probability: %s" % (
            numberOfPostsToInteract, followAmount, probabilityPercentage, calculatedProbability))

    if calculatedProbability < probabilityPercentage:
        calculatedFollowUnfollowProbability = randint(1, 100)
        if calculatedFollowUnfollowProbability <= 50:
            self.logger.info("performFollowUnfollow: calculatedFollowUnfollowProbability: %s, going to follow...",
                             calculatedFollowUnfollowProbability)

            # follow
            # todo: operation follow_users_by_hashtag is deprecated
            if isOperationEnabled("follow_users_by_hashtag", self.campaign['id_campaign'], self.logger):
                # try to folllow
                self.logger.info("performFollowUnfollow: Trying to follow user %s", user_name)

                # todo: follow_user method is overengineered , try to simplify it
                followed = follow_user(self.browser,
                                       self.follow_restrict,
                                       self.username,
                                       user_name,
                                       self.blacklist,
                                       self.logger,
                                       self.logfolder)


                if followed:
                    insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                    None, None, user_name,
                                    None, None, None,
                                    link, 'follow_'+engagement_by, tag, self.id_log)

            else:
                self.logger.info(
                    "performFollowUnfollow: Tried to follow, but follow is not enabled ! ... going to continue")

        else:
            # unfollow

            self.logger.info("performFollowUnfollow: calculatedFollowUnfollowProbability: %s, going to unfollow...",
                             calculatedFollowUnfollowProbability)
            # check if user wants to unfollow
            userWantsToUnfollow = getIfUserWantsToUnfollow(self.campaign['id_campaign'])
            if userWantsToUnfollow == False:
                self.logger.info("performFollowUnfollow: User does not want to unfollow, going to continue !")

            else:
                self.logger.info(
                    "performFollowUnfollow: User wants to unfollow after %s hours" % userWantsToUnfollow['value'])

                selectFollowings = "select * from bot_action where  bot_operation like %s and timestamp< (NOW() - INTERVAL %s HOUR) and id_user= %s and bot_operation_reverted is null order by timestamp asc limit %s"

                recordToUnfollow = fetchOne(selectFollowings, 'follow' + '%', userWantsToUnfollow['value'],self.campaign['id_user'], 1)

                if recordToUnfollow:
                    status = custom_unfollow(self.browser, recordToUnfollow['username'], self.logger)
                    lastBotAction = insertBotAction(self.campaign['id_campaign'], self.campaign['id_user'],
                                                    None, None, recordToUnfollow['username'],
                                                    None, None, None, None, 'unfollow_'+engagement_by, None,
                                                    self.id_log)

                    insert("update bot_action set bot_operation_reverted=%s where id=%s", lastBotAction, recordToUnfollow['id'])
                else:
                    self.logger.info("performFollowUnfollow: No user found in database to unfollow...")
    return True


# TODO: the data model should be changed acoording to this structure !
def getOperationsInNewFormat(operations):
    newOperations = []
    locationEngagementAdded = False
    tagEngagementAdded = False

    for operation in operations:
        if 'like_posts_by_hashtag' == operation['configName'] or 'follow_users_by_hashtag' == operation['configName']:
            newOperation = getOperationByName(operations, 'like_posts_by_hashtag')
            if newOperation == False:
                newOperation = getOperationByName(operations, 'follow_users_by_hashtag')

            if tagEngagementAdded == False:
                newOperation['name'] = 'engagement_by_hashtag'
                newOperation['list'] = operation['list']
                newOperations.append(newOperation)
                tagEngagementAdded = True

        if 'like_posts_by_location' == operation['configName'] or 'follow_users_by_location' == operation['configName']:
            newOperation = getOperationByName(operations, 'like_posts_by_location')
            if newOperation == False:
                newOperation = getOperationByName(operations, 'follow_users_by_location')

            if locationEngagementAdded == False:
                newOperation['name'] = 'engagement_by_location'
                newOperation['list'] = operation['list']
                newOperations.append(newOperation)
                locationEngagementAdded = True

        if 'unfollow' == operation['configName']:
            newOperation = {}
            newOperation['name'] = 'unfollow'
            newOperations.append(newOperation)

    return newOperations


def canInteractWithLink(self, link):
    try:
        # TODO: i don't think this is required
        inappropriate, user_name, is_video, reason, scope = (
            check_link(self.browser,
                       link,
                       self.dont_like,
                       self.ignore_if_contains,
                       self.logger)
        )
        time.sleep(2)
        if not inappropriate and self.liking_approved:
            # validate user
            validation, details = validate_username(self.browser,
                                                    user_name,
                                                    self.username,
                                                    self.ignore_users,
                                                    self.blacklist,
                                                    self.potency_ratio,
                                                    self.delimit_by_numbers,
                                                    self.max_followers,
                                                    self.max_following,
                                                    self.min_followers,
                                                    self.min_following,
                                                    self.logger)
            if validation is True:
                return {'status': True, 'user_name': user_name}
            else:
                self.logger.info("canInteractWithLink: Error, link is not good %s", details)

    except NoSuchElementException as err:
        self.logger.error('canInteractWithLink: Invalid Page: {}'.format(err))
        return False

    return False


def splitTotalAmount(self, amount, noOfHashtags, divideAmountTo=4):
    if noOfHashtags < divideAmountTo:
        divideAmountTo = noOfHashtags

    self.logger.info("splitTotalAmount: Going to divide amount to %s:", divideAmountTo)
    return amount // divideAmountTo


def get_links(self, numberOfPostsToExtract, engagementBy, engagementByValue):
    if engagementBy == "engagement_by_hashtag":
        try:
            links = get_links_for_tag(browser=self.browser, amount=numberOfPostsToExtract, tag=engagementByValue,
                                      skip_top_posts=True, media=None, logger=self.logger)
        except NoSuchElementException:
            self.logger.info('get_links: Too few images, skipping this tag: %s', engagementByValue)
            return []

    elif engagementBy == "engagement_by_location":
        try:
            links = get_links_for_location(self.browser,
                                           amount=numberOfPostsToExtract,
                                           location=engagementByValue,
                                           logger=self.logger)

        except NoSuchElementException:
            self.logger.warning('Too few images, skipping this location: %s' % (engagementByValue))
            return []

    return links


def getItemToProcess(operation, engagement_by):
    # extract a random hashtag from the list
    itemIndex = randint(0, len(operation['list']) - 1)
    itemObject = operation['list'][itemIndex]

    if engagement_by == "engagement_by_location":
        itemValue = itemObject['id_location']

    if engagement_by == "engagement_by_hashtag":
        itemValue = itemObject['hashtag']

    del operation['list'][itemIndex]
    return itemValue
