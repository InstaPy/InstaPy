#!/bin/bash

# This is a script to mitigate possibility of multiple parallel cron jobs being triggered(discussed here: https://github.com/timgrossmann/InstaPy/issues/1235)
# The following is example of a cron scheduled every 10 mins
# */10 * * * * bash /path/to/InstaPy/scripts/run_instapy_only_once_for_mac.sh target_followers_of_similar_accounts_and_influencers.py

TEMPLATE_NAME=$1
if ps aux | grep $TEMPLATE_NAME | awk '{ print $11 }' | grep python
then
   echo $TEMPLATE_NAME" is already running"
else
   echo "Starting "$TEMPLATE_NAME
   /Users/ishandutta2007/.pyenv/shims/python `dirname "$0"`/../quickstart_templates/$TEMPLATE_NAME -u myuser -p mypwd --headless-browser --disable_image_load
fi

