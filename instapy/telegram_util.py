#install python module with command
# pip install python-telegram-bot

import telegram
from telegram.error import NetworkError, Unauthorized

insta_username = None
bot = telegram.Bot('<bot father token>')


def start_telegram(insta_username):
    """Run the bot."""
    # Telegram Bot Authorization Token
    bot.send_message(-1001000000702, insta_username + ' started botting!')
    
def finish_telegram(insta_username):
    """Run the bot."""
    bot.send_message(-1001000000702, insta_username + ' finished botting!')
    
def pause_telegram(insta_username):
    """Run the bot."""
    # Telegram Bot Authorization Token
    bot.send_message(-1001000000702, insta_username + ' is pretending to be human and is idle for 1 hour. You can logon for an hour if you want.')
   #bot.send_message(<Channel ID>, what_ever_you_want_it_to_echo)
	
#To Create a bot on Telegram follow these steps: https://core.telegram.org/bots#6-botfather (https://telegram.me/botfather)
#Yes, you actually have to go into Telegram and talk to a Bot to create a bot. The Father of Bots that is...
#Then create a channel with your real account (not the bot account)
#Add the bot to the channel and to find the channel ID you will need to use this API Call (VERY IMPORANT THE BOT IS ADDED TO YOUR CHANNEL)
#https://api.telegram.org/bot<token>/getUpdates
#The Channel ID will start with a '-' (minus sign)
