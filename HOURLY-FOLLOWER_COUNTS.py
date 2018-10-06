""" This is a cheap way to get follower and follwing count updates on a scheduled basis.
     The same format can be used to schedule tasks like getting follower lists etc
     the tags and credentials are loaded in from .env file to keep it scalable
"""

"""
ISSUES:
This has a LOT of extra code in it, but it was built more for testing originally. 
decided to use a basic logger set in this file instead of the main instapy logger.
also could have used built in funcion to return follower count, but ended up writing test
function in this script and using them as a standalone was of getting the count and parsing the data.

Need to add any pip requirements into requirements.txt
Could convert over to instapy logging
NO need for reading .env tag vars in here, just did it for testing.
No log rotation built in yet
Need to look at the logfolder variable. Probably wont work for anyone else because I had code dir added
Havent tested what this does in a random subdir under instapy dir
Default settings is every hour
"""

""".env files can hold sensitive data. 
pip install -U python-dotenv
https://github.com/theskumar/python-dotenv
"""

# imports
from instapy import InstaPy
from instapy.util import smart_run
import os
from settings import Settings
import logging
import schedule
import time
from dotenv import load_dotenv

# load_dotenv()
# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# use this to load TAGS into LIST.
# these must match keys in .env file
major_tag_list = os.getenv("major_tag_list").split(",")
minor_tag_list = os.getenv("minor_tag_list").split(",")
interact_list = os.getenv("interact_list").split(",")
insta_username = os.getenv('insta_username')
insta_password = os.getenv('insta_password')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# quickfix, shouldnt require this on server.
BASE_DIR = os.path.join(BASE_DIR, "code")
logfolder = BASE_DIR + os.path.sep + 'logs' + os.path.sep + insta_username + os.path.sep

# create logger
logger = logging.getLogger('stats_logger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

fh = logging.FileHandler(filename='{}Follower_Count_Status.log'.format(logfolder))
fh.setLevel(logging.DEBUG)

MYUSER = '[' + os.getenv('insta_username') + ']'


class ContextFilter(logging.Filter):
    """
    This is a filter that puts our username in the log line.
    """

    def filter(self, record):
        record.MYUSER = MYUSER
        return True


formatter = logging.Formatter('%(asctime)s - %(MYUSER)s- %(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M')
logger.addFilter(ContextFilter())
# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)

# Settings.profile["name"] = username

# check if logfolder exists
if os.path.exists(logfolder):
    logger.debug('LogFolder Exists!')
if not os.path.exists(logfolder):
    logger.debug('LogFolder DOES NOT Exists!')
    logfolder = BASE_DIR + os.path.sep + 'logs' + os.path.sep + insta_username + os.path.sep
    if os.path.exists(logfolder):
        logger.debug('LogFolder RESET!')
    else:
        logger.critical('LOG FOLDER NOT FOUND')
        exit(1)

logger.debug('Base_Dir={}'.format(BASE_DIR))
# logfolder = Settings.log_location + os.path.sep +  insta_username + os.path.sep

logger.debug('LOGFOLDER: {}'.format(logfolder))
countFollowerNum = 0
countFollowingNum = 0
followerlist = []
followinglist = []

""" *****************Loading ENV Variables into SESSION ****************"""
logger.info('Loading Session Variables into Memory : ({})'.format(os.getenv('insta_username')))
logger.debug('Loaded {} Major Tags into Memory'.format(len(major_tag_list)))
logger.debug('Loaded {} Minor Tags into Memory'.format(len(minor_tag_list)))
logger.debug('Loaded {} Interaction Tags into Memory'.format(len(interact_list)))
logger.debug('Get Follow Data From IG Every {} Minutes'.format(os.getenv('GetFollowDataEveryXMin')))


def doFollowAnalysis(type, logfolder):
    followList = []
    if type == 'Followers':
        logger.info('Getting Followers Count for {}'.format(insta_username))
        logger.debug('getting file: {}followerNum.txt'.format(logfolder))
        if not os.path.exists('{}followerNum.txt'.format(logfolder)):
            logger.critical('FOLLOWER FILE DOESNT EXIST')
            exit(1)
        with open('{}followerNum.txt'.format(logfolder), 'r') as numFile:
            for line in numFile:
                followList.append(line)
        followList.sort(reverse=True)
        logger.debug('{} entries in Followers File'.format(len(followList)))
        lastestlogline = followList[0]
        lastestlogline = lastestlogline.rstrip()
        lastcount = lastestlogline.split(' ')[2]
        return lastcount
    if type == 'Following':
        logger.info('Getting Following Count for {}'.format(insta_username))
        logger.debug('getting file: {}followingNum.txt'.format(logfolder))
        if not os.path.exists('{}followingNum.txt'.format(logfolder)):
            logger.critical('FOLLOWING FILE DOESNT EXIST')
            exit(1)
        with open('{}followingNum.txt'.format(logfolder), 'r') as numFile:
            for line in numFile:
                followList.append(line)
        followList.sort(reverse=True)
        logger.debug('{} entries in Following File'.format(len(followList)))
        lastestlogline = followList[0]
        lastestlogline = lastestlogline.rstrip()
        lastcount = lastestlogline.split(' ')[2]
        return lastcount


def job():
    try:
        logger.info('Instapy Status Script has started!')
        # get an InstaPy session!
        # set headless_browser=True to run InstaPy in the background
        session = InstaPy(username=insta_username,
                          password=insta_password,
                          headless_browser=True)

        with smart_run(session):
            """ Activity flow """
            # settings
            session.set_relationship_bounds(enabled=True,
                                            delimit_by_numbers=True,
                                            max_followers=9999,
                                            min_followers=45,
                                            min_following=77)
            session.set_quota_supervisor(enabled=True,
                                         sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
                                         sleepyhead=True, stochastic_flow=True, notify_me=True,
                                         peak_likes=(57, 585),
                                         peak_comments=(21, 182),
                                         peak_follows=(48, None),
                                         peak_unfollows=(35, 402),
                                         peak_server_calls=(None, 4700))
            logger.info("Hourly Stats have been Saved!")
            logger.info(
                '{} currently has {} followers'.format(insta_username, doFollowAnalysis('Followers', logfolder)))
            logger.info('{} is currently following {} accounts'.format(insta_username,
                                                                       doFollowAnalysis('Following', logfolder)))

            logger.info('Instapy Status Script has completed!')
    except OSError as err:
        logger.error("OS error: {0}".format(err))
    except ValueError:
        logger.error("Could not convert data to an integer.")
    except (KeyboardInterrupt, SystemExit):
        logger.warning('OK OK OK!!! We Quit! Ctl-C Detected')
    except:
        import traceback
        logger.critical('JOB FAILED:  {}'.format(traceback.format_exc()))
        exit(1)


def main():
    # schedule.every().day.at("20:50").do(job)
    # schedule.every().hour.do(job)
    # os.getenv('GetFollowDataEveryXMin') MUST BE SET. DEFAULT=60
    schedule.every(int(os.getenv('GetFollowDataEveryXMin'))).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
