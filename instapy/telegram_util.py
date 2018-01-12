#install python module with command
# pip install python-telegram-bot

import telegram
from telegram.error import NetworkError, Unauthorized

update_id = None
insta_username = ""


def start_telegram():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot('<token>')
    echo_start(bot)
    
def finish_telegram():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot('<token>')
    echo_finish(bot)
    
def pause_telegram():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot('<token>')
    echo_pause(bot)

def echo_start(bot):
	bot.send_message(-1001000003702, insta_username + ' started botting')
	
def echo_finish(bot):
	bot.send_message(-1001000003702, insta_username + ' finished botting')
	
def echo_pause(bot):
	bot.send_message(-10010000003702, insta_username + ' is pretending to be human and is idle for 1 hour. You can logon for an hour if you want.')
#bot.send_message(<Channel ID>, what_ever_you_want_it_to_echo)
	
#To Create a bot on Telegram follow these steps: https://core.telegram.org/bots#6-botfather (https://telegram.me/botfather)
#Yes, you actually have to go into Telegram and talk to a Bot to create a bot. The Father of Bots that is...
#Then create a channel with your real account (not the bot account)
#Add the bot to the channel and to find the channel ID you will need to use this API Call
# https://api.telegram.org/bot<token>/getUpdates
#The Channel ID will start with a '-' (minus sign)
