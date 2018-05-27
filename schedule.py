import json
import sys
import codecs
import os
import argparse
import logging
import time
import subprocess
from random import randint

stdout = sys.stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.path.append(os.path.join(sys.path[0], '../'))
fileName = "start_bot_" + time.strftime("%d.%m.%Y") + ".log"
logging.basicConfig(format='%(asctime)s %(message)s', filename='/home/instapy-log/campaign/logs/' + fileName, level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger('[schedule]')
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-angie_campaigns', type=str, help="angie_campaigns")
args = parser.parse_args()

campaigns = json.loads(args.angie_campaigns)

logger.info("schedule_bot: Starting the scheduler script")
logger.info("schedule_bot: Received the following campaigns %s", campaigns)

DEVNULL = open(os.devnull, 'wb')
waitDelay = randint(10, 40)

logger.info("The bots will be started in %s minutes", waitDelay)
time.sleep(waitDelay * 60)

logger.info("Going to start bots for each user...")

for campaign in campaigns:
    logger.info("schedule_bot: Starting bot for campaign %s", campaign)
    processName = "angie_instapy_idc" + str(campaign)
    subprocess.Popen(
        "bash -c \"exec -a " + processName + " /usr/bin/python /home/InstaPy/start.py -angie_campaign=" + str(
            campaign) + "\"", stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, shell=True)
    logger.info("schedule_bot: Done staring campaign for %s", campaign)
    pause=randint(1,3)
    logger.info("schedule_bot: Going to sleep %s minutes",pause)
    time.sleep(pause * 60)

logger.info("schedule_bot: Done running the script")
