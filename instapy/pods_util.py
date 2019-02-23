import requests
from .settings import Settings

def get_recent_posts_from_pods(logger):
    params = {'category' : 'general'}
    r = requests.get(Settings.pods_server_endpoint + '/getRecentPosts', params=params)
    try:
        logger.info("Downloaded postids from Pods:")
        logger.info(r.json())
        return r.json()
    except Exception as err:
        logger.error(err)
        return None

def share_my_post_with_pods(postid, logger):
    """ share_my_post_with_pod """
    logger.info("Publishing to Pods {}".format(postid))
    params = {'postid' : postid, 'category' : 'general'}
    r = requests.get(Settings.pods_server_endpoint + '/publishMyLatestPost', params=params)
    try:
        logger.info(r)
        logger.info(r.json())
        return True
    except Exception as err:
        logger.error(err)
        return False
