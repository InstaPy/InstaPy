import argparse
import codecs
import os
import sys
import traceback
from time import sleep
from instapy import InstaPy
from instapy.api_db import fetchOne
from random import randint
from instapy.bot_util import getBotOperations

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaign', type=str, help="angie_campaign")
args = parser.parse_args()

#args.angie_campaign = "1"

if args.angie_campaign is None:
    exit("dispatcher: Error: Campaign id it is not specified !")

try:


    campaign = fetchOne(
        "select ip,username,password,campaign.timestamp,id_campaign,id_user  from campaign left join ip_bot using (id_ip_bot) where id_campaign=%s",
        args.angie_campaign)
    if campaign['ip'] is None:
        exit("Invalid proxy")

    session = InstaPy(username=campaign['username'],
                      password=campaign['password'],
                      headless_browser=True,
                      bypass_suspicious_attempt=True,
                      proxy_address=campaign['ip'].replace("http://cata:lin@", ""),
                      campaign=campaign,
                      proxy_port="80",
                      multi_logs=True)

    session.set_relationship_bounds(enabled=True, potency_ratio=0.01, max_followers=999999, max_following=99999, min_followers=100, min_following=50)

    session.logger.info("start: Instapy Started for account %s, using proxy: %s" % ( campaign['username'], campaign['ip']))
    session.canBotStart(args.angie_campaign)

    status = session.login()
    if status == False:
        exit("Could not  login")

    noOfLoops = randint(5,7)
    #TODO: validate the amountForEachLoop, set a treshhold
    likeAmount = randint(200,350)
    session.logger.info("start: Bot started going to perform %s likes, %s follow/unfollow during %s loops" % (likeAmount, 0, noOfLoops))

    operations = getBotOperations(campaign['id_campaign'], session.logger)

    for loopNumber in range(0, noOfLoops):
        amountForEachLoop = randint(likeAmount // noOfLoops - 20, likeAmount // noOfLoops + 30)
        session.logger.info(
            "start: Starting loop number %s, likeAmount: %s, followAmount:%s" % (loopNumber, amountForEachLoop, 0))
        session.executeAngieActions(operations, likeAmount=amountForEachLoop, followAmount=0)

        sleepMinutes = randint(40,120)
        session.logger.info("start: GOING TO SLEEP FOR %s MINUTES, LOOP NO %s" % (sleepMinutes, loopNumber))

        #todo enable sleep
        sleep(sleepMinutes*60)
        session.logger.info("start: Done sleeping going to continue looping...")

    session.logger.info("start: Angie loop completed , going to exit...")

except:
    exceptionDetail = traceback.format_exc()
    print(exceptionDetail)
    session.logger.critical("start: FATAL ERROR: %s", exceptionDetail)
finally:
    session.logger.info("start: Instapy ended for user: %s", campaign['username'])
