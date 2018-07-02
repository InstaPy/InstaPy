"""
    All methods must return media_ids that can be
    passed into e.g. like() or comment() functions.
"""

import time
from datetime import *
from random import randint

from api_db import *

#dumb function
def randomizeValue(value, randomizePercent, direction="random"):
    originalValue = value

    randomizeValue = randomizePercent * value // 100

    if direction == "up":
        value = value + randomizeValue
        if value == originalValue:
            value = value + randint(1,3)


    elif direction == "down":
        value = value - randomizeValue
        if value == originalValue:
            value = value - randint(1,3)

    else:
        randomDirection = randint(1, 100)
        if randomDirection >= 50:
            value = value + randomizeValue
            if value == originalValue:
                value = value + randint(1,3)
        else:
            value = value - randomizeValue
            if value == originalValue:
                value = value - randint(1, 3)

    if value < 0:
        return originalValue

    return value


def getIfUserWantsToUnfollow(id_campaign):
    query = 'select _key,value from  campaign_config join campaign_config_parameters using (id_config) where configName="unfollow"  and id_campaign= %s and _key="after_x_hours" and campaign_config.enabled=1'

    result = fetchOne(query, id_campaign)
    if not result:
        return False

    return result


def isOperationEnabled(operationName, id_campaign, logger):
    operations = getBotOperations(id_campaign, logger)

    logger.info("isOperationEnabled: Checking if operation %s is enabled", operationName)

    for operation in operations:

        if operationName in operation['configName']:
            logger.info("isOperationEnabled: Operation %s is available", operationName)
            return operation

    logger.info("isOperationEnabled: Operation %s is not available", operationName)
    return False


def getOperationByName(operations, name):
    for operation in operations:
        if name in operation['configName']:
            return operation

    return False


def getBotOperations(id_campaign, logger):
    totalLikePercentage = 0
    totalFollowPercentage = 0
    totalLikeOperations = 0
    totalFollowOperations = 0

    operations = select(
        "SELECT configName, id_config, enabled, like_post, follow_user, percentageAmount FROM campaign_config where id_campaign=%s and enabled=1",
        id_campaign)
    for operation in operations:

        if 'engagement_by_hashtag' in operation['configName']:
            tags = select("select * from instagram_hashtags where id_config=%s and enabled=1", operation['id_config'])
            operation['list'] = tags

        if 'engagement_by_location' in operation['configName']:
            locations = select("select * from instagram_locations where id_config=%s and enabled=1", operation['id_config'])
            operation['list'] = locations


    # apply percentage
    # if totalLikePercentage<100 and totalLikePercentage>0:
    #     self.logger.info("BOTUTIL: Unused LIKE percentage is %s, going to distribute it to %s like operations" % (100-totalLikePercentage, totalLikeOperations))
    #     remainingLikePercentage = math.ceil (math.ceil(100-totalLikePercentage) / math.ceil(totalLikeOperations))
    #     self.logger.info("BOTUTIL: Each operation will receive %s extra percentage !", remainingLikePercentage)
    #
    #     for operation in operations:
    #         if 'like' in operation['configName']:
    #             operation['percentageAmount']+=remainingLikePercentage

    # if totalFollowPercentage<100 and totalFollowPercentage>0:
    #
    #     self.logger.info("BOTUTIL: Unused follow percentage is %s, going to distribute it to %s follow operations" % (100- totalFollowPercentage, totalFollowOperations))
    #
    #     if totalFollowOperations==0:
    #       self.logger.info("BOTUTIL: no available operations of type follow. Probably it is set the unfollow operation with fixed percentage !")
    #     else:
    #       remainingFollowPercentage = math.ceil(math.ceil(100 - totalFollowPercentage) / math.ceil(totalFollowOperations))
    #       self.logger.info("BOTUTIL: Each operation of type follow will receive %s extra percentage !", remainingFollowPercentage)
    #
    #       for operation in operations:
    #           if  str(operation['configName']).startswith("follow") and operation['configName']!="unfollow":
    #               operation['percentageAmount'] += remainingFollowPercentage
    #
    # for op in operations:
    #     self.logger.info("Percentage: %s , Amount: %s" % (op['percentageAmount'], op['configName']))

    logger.info("getBotOperations: Found %s operations", len(operations))
    return operations


def get_spam_delay(self):
    self.logger.info("get_spam_delay: Calculating the spam delay")
    self.logger.info("get_spam_delay: Getting amounts of times the user %s was blocked", self.web_application_id_user)
    result = fetchOne(
        "select count(*) as total from instagram_log where id_user=%s and details='spam' and date(timestamp)=curdate()",
        self.web_application_id_user)
    if result['total'] >= 12:
        self.logger.info("get_spam_delay: There were more than 12 blocks today, going to stop the bot")
        raise Exception("get_spam_delay: More than 12 blocks today")
    if result['total'] >= 4:
        sleep = randint(60, 90)
        self.logger.info("get_spam_delay: There were more than 4 blocks today, going to pause for %s minutes ", sleep)
        return sleep
    else:
        sleep = randint(10, 25)
        self.logger.info("get_spam_delay: There were less than 4 blocks today, going to pause for %s minutes ", sleep)
        return sleep


def how_many_seconds_until_midnight():
    tomorrow = date.today() + timedelta(1)
    midnight = datetime.combine(tomorrow, time())
    now = datetime.now()
    return (midnight - now).seconds


def get_like_delay(self, likeAmount):
    if self.isAccountWarmingUp() or self.isAccountStartup() == True:
        percentageIncrease = 90
        self.like_delay = self.like_delay + int(round(self.like_delay * percentageIncrease / 100))
        self.logger.info(
            "get_like_delay: Account is warming up/startup, going to increase the like delay by %s percentage. Final delay %s seconds" % (
            percentageIncrease, self.like_delay))
        return self.like_delay
    else:
        self.logger.info("get_like_delay: The like delay is ~ %s seconds", self.like_delay)
        return self.like_delay

    # todo this code should be improved
    if likeAmount == 0:
        return self.like_delay

    secondsUntilMidnight = how_many_seconds_until_midnight()
    likeDelay = secondsUntilMidnight / likeAmount
    if likeDelay < self.like_delay:
        self.logger.info("get_like_delay: Calculated like delay is less than the original one... reseting to %s",
                         self.like_delay)
        return self.like_delay
    else:
        if likeDelay > 100:
            self.logger.info(
                "get_like_delay: like delay is %s, bigger than max limit 100, going to set it to 100 seconds")
            likeDelay = 100
        self.like_delay = likeDelay
        self.logger.info("get_like_delay: seconds until midnight:%s, like amount: %s, delay: %s" % (
        secondsUntilMidnight, likeAmount, likeDelay))
        return likeDelay


def get_follow_delay(self, followAmount):
    if self.isAccountWarmingUp() or self.isAccountStartup() == True:
        percentageIncrease = 90
        self.follow_delay = self.follow_delay + int(round(self.follow_delay * percentageIncrease / 100))
        self.logger.info(
            "get_follow_delay: Account is warming up/startup going to increase the follow delay by %s percentage. Final delay ~ %s seconds" % (
            percentageIncrease, self.follow_delay))
        return self.follow_delay
    else:
        self.logger.info("get_follow_delay: The follow delay is ~ %s seconds", self.follow_delay)
        return self.follow_delay

    return self.follow_delay

    # todo this code should be improved
    if followAmount == 0:
        return self.follow_delay
    secondsUntilMidnight = how_many_seconds_until_midnight()
    followDelay = secondsUntilMidnight / followAmount
    if followDelay < self.follow_delay:
        self.logger.info("get_follow_delay: Calculated follow delay is less than the original one... reseting to %s",
                         self.follow_delay)
        return self.follow_delay
    else:
        self.follow_delay = followDelay
        self.logger.info("get_follow_delay: seconds until midnight:%s, follow amount: %s, delay: %s" % (
        secondsUntilMidnight, followAmount, followDelay))
        return followDelay
