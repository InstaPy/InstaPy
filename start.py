import argparse
import codecs
import os
import sys
import traceback
from time import sleep
from instapy import InstaPy
from instapy.bot_action_handler import getAmountDistribution, getLikeAmount, getFollowAmount, getActionAmountForEachLoop
from instapy.bot_util import *


stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaign', type=str, help="angie_campaign")
args = parser.parse_args()

#args.angie_campaign='3'

if args.angie_campaign is None:
    exit("dispatcher: Error: Campaign id it is not specified !")

try:


    campaign = fetchOne("select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",args.angie_campaign)

    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=False,
                      bypass_suspicious_attempt=False,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True)

    calculatedAmount = getAmountDistribution(session, args.angie_campaign)

    totalExpectedLikesAmount = int(getLikeAmount(session, args.angie_campaign, calculatedAmount))
    totalExpectedFollowAmount = int(getFollowAmount(session, args.angie_campaign, calculatedAmount))

    operations = getBotOperations(campaign['id_campaign'], session.logger)

    session.set_relationship_bounds(enabled=True, potency_ratio=0.01, max_followers=999999, max_following=99999, min_followers=100, min_following=50)

    session.logger.info("start: Instapy Started for account %s, using proxy: %s" % ( campaign['username'], campaign['ip']))
    session.canBotStart(args.angie_campaign)

    status = session.login()
    if status == False:
        exit("Could not  login")

    noOfLoops = randint(5,7)

    session.logger.info("start: Bot started going to perform %s likes, %s follow/unfollow during %s loops" % (totalExpectedLikesAmount, 0, noOfLoops))

    for loopNumber in range(0, noOfLoops):

        likeAmountForEachLoop = getActionAmountForEachLoop(totalExpectedLikesAmount, noOfLoops)
        followAmountForEachLoop = getActionAmountForEachLoop(totalExpectedFollowAmount, noOfLoops)

        session.logger.info("start: Starting loop number %s, goint to perform: likeAmount: %s, followAmount:%s" % (loopNumber, likeAmountForEachLoop, followAmountForEachLoop))

        session.executeAngieActions(operations, likeAmount=likeAmountForEachLoop, followAmount=followAmountForEachLoop)

        sleepMinutes = randint(40,120)
        session.logger.info("start: GOING TO SLEEP FOR %s MINUTES, LOOP NO %s" % (sleepMinutes, loopNumber))

        sleep(sleepMinutes*60)
        session.logger.info("start: Done sleeping going to continue looping...")

    session.logger.info("start: Angie loop completed , going to exit...")

except:
    exceptionDetail = traceback.format_exc()
    print(exceptionDetail)
    session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
finally:
    session.logger.info("start: Instapy ended for user: %s", campaign['username'])
