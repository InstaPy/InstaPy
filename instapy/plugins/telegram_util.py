"""
A fully functional TelegramBot to get info on an instapy run
or to control the instapy bot

you will need to create your token on the telegram app and speak with @botfather
you will need to have a username (go to settings -> profile -> Username
"""

from ..util import truncate_float
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.error import (
    TelegramError,
    Unauthorized,
    BadRequest,
    TimedOut,
    ChatMigrated,
    NetworkError,
)
import logging
import requests
import os


class InstaPyTelegramBot:
    """
    Class to handle the instapy telegram bot
    """

    def __init__(
        self,
        token="",
        telegram_username="",
        instapy_session=None,
        debug=True,
        proxy=None,
    ):
        # import pdb; pdb.set_trace()
        # private properties
        self.__logger = logging.getLogger()
        self.__chat_id = None
        self.__updater = None
        self.__context = None

        # public properties
        self.token = token
        self.telegram_username = telegram_username
        self.instapy_session = instapy_session
        self.debug = debug
        self.proxy = proxy
        # should be of type:
        # proxy = {
        #     'proxy_url': 'http://PROXY_HOST:PROXY_PORT/',
        #     # Optional, if you need authentication:
        #     'username': 'PROXY_USER',
        #     'password': 'PROXY_PASS',

        # see if we have a pre-existing chat_id from another run
        if self.instapy_session is not None:
            try:
                telegramfile = open(
                    "{}telegram_chat_id.txt".format(self.instapy_session.logfolder)
                )
            except OSError:
                self.__chat_id = None
            else:
                with telegramfile:
                    self.__chat_id = telegramfile.read()

        # launch the telegram bot already if everything is ready at init
        if (
            (self.token != "")
            and (self.telegram_username != "")
            and (self.instapy_session is not None)
        ):
            self.telegram_bot()

    @property
    def debug(self):
        """
        the debug parameter
        :return:
        """
        return self._debug

    @debug.setter
    def debug(self, value):
        """
        sets the debug if needed
        :param debug:
        :return:
        """
        self._debug = value
        if self._debug is True:
            if self.__logger is None:
                self.__logger = logging.getLogger()

            self.__logger.setLevel(logging.DEBUG)

    def telegram_bot(self):
        """
        Funtion to initialize a telegram bot that you can talk to and control your InstaPy Bot
        :return:
        """
        if self.token == "":
            self.__logger.warning(
                "You need to set token for InstaPyTelegramBot to work"
            )
            return
        if self.telegram_username == "":
            self.__logger.warning(
                "You need to set telegram_username for InstaPyTelegramBot to work"
            )
            return
        if self.instapy_session is None:
            self.__logger.warning(
                "You need to set instapy_session for InstaPyTelegramBot to work"
            )
            return

        self._clean_web_hooks()

        if self.proxy is not None:
            updater = Updater(
                token=self.token,
                use_context=True,
                user_sig_handler=self.end,
                request_kwargs=self.proxy,
            )
        else:
            updater = Updater(
                token=self.token, use_context=True, user_sig_handler=self.end
            )
        self.__updater = updater

        dispatcher = updater.dispatcher
        self.__context = dispatcher
        dispatcher.add_error_handler(self._error_callback)
        start_handler = CommandHandler("start", self._start)
        dispatcher.add_handler(start_handler)
        report_handler = CommandHandler("report", self._report)
        dispatcher.add_handler(report_handler)
        report_handler = CommandHandler("stop", self._stop)
        dispatcher.add_handler(report_handler)
        unknown_handler = MessageHandler(Filters.command, self._unknown)
        dispatcher.add_handler(unknown_handler)
        updater.start_polling()
        if self.__chat_id is not None:
            # session was restored, send a message saying that instapy session is starting
            self.__context.bot.send_message(
                self.__chat_id, text="Telegram session restored, InstaPy starting\n"
            )

    def send_message(self, text=""):
        """
        function to be able to send messages from anywhere else in the instapy code
        :param text: the text of the message you want to send
        remember we cannot send_messages if we don't have the chat_id
        to get the chat_id, user has to send at little one /start to the bot
        :return:
        """
        if (self.__chat_id is None) and (self.__context is None):
            raise TelegramError
        else:
            self.__context.bot.send_message(chat_id=self.__chat_id, text=text)

    @staticmethod
    def telegram_delete_session(session):
        """
        function to force delete the telegram_chat_id.txt file that is in the logs folder
        :param session: the instapy session
        :return:
        """
        os.remove("{}telegram_chat_id.txt".format(session.logfolder))

    def _start(self, update, context):
        """
        basic /start function
        :param update:
        :param context:
        :return:
        """
        self.__chat_id = update.message.chat_id
        if self._check_authorized(update, context):
            with open(
                "{}telegram_chat_id.txt".format(self.instapy_session.logfolder), "w"
            ) as telegramfile:
                telegramfile.write(str(self.__chat_id))

            context.bot.send_message(
                chat_id=update.message.chat_id, text="Bot initialized sucessfully!\n"
            )

    def _report(self, update, context):
        """
        report live statistics
        :param update:
        :param context:
        :return:
        """
        self.__chat_id = update.message.chat_id
        if self._check_authorized(update, context):
            context.bot.send_message(
                chat_id=update.message.chat_id, text=self._live_report()
            )

    def _stop(self, update, context):
        """
        should stop the bot
        :param update:
        :param context:
        :return:
        """
        self.__chat_id = update.message.chat_id
        if self._check_authorized(update, context):
            self.instapy_session.aborting = True
            context.bot.send_message(
                chat_id=update.message.chat_id, text="InstaPy session abort set\n"
            )

    def _unknown(self, update, context):
        """
        trap all others commands as unknown
        :return:
        """
        if self._check_authorized(update, context):
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Sorry I don't understand that command",
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=" Recognized actions are:\n"
                + "   - /start (initialize bot) \n"
                + "   - /report (a live report from the bot)\n"
                + "   - /stop (force stop the bot)\n",
            )

    def _check_authorized(self, update, context):
        """
        check if a user is authorized to use this bot
        :param update:
        :param context:
        :return:
        """
        if update.message.from_user.username != self.telegram_username:
            self.__logger.warning(
                "unauthorized access from {}".format(update.message.from_user)
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="You are not authorized to use this service \n",
            )
            return False
        else:
            return True

    def _clean_web_hooks(self):
        """
        make sure no web_hooks are configured already otherwise telegram
        will respond 409
        :return:
        """
        r = requests.get(
            "https://api.telegram.org/bot{}/deleteWebhook".format(self.token)
        )

        if r.json()["ok"] is not True:
            self.__logger.warning("unable to remove webhook! Wrong token?")

    def _error_callback(self, update, error):
        try:
            raise error
        except Unauthorized:
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
        except BadRequest:
            # handle malformed requests - read more below!
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
        except TimedOut:
            # handle slow connection problems
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
        except NetworkError:
            # handle other connection problems
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
        except ChatMigrated as _:
            # the chat_id of a group has changed, use e.new_chat_id instead
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
        except TelegramError:
            self.__logger.warning("TELEGRAM ERROR {} update={}".format(error, update))
            # handle all other telegram related errors

    def _live_report(self):
        """
        adapted version of instapy live report function for showing up on a telegram message
        :return:
        """
        stats = [
            self.instapy_session.liked_img,
            self.instapy_session.already_liked,
            self.instapy_session.commented,
            self.instapy_session.followed,
            self.instapy_session.already_followed,
            self.instapy_session.unfollowed,
            self.instapy_session.stories_watched,
            self.instapy_session.reels_watched,
            self.instapy_session.inap_img,
            self.instapy_session.not_valid_users,
        ]

        sessional_run_time = self.instapy_session.run_time()
        run_time_info = (
            "{} seconds".format(sessional_run_time)
            if sessional_run_time < 60
            else "{} minutes".format(truncate_float(sessional_run_time / 60, 2))
            if sessional_run_time < 3600
            else "{} hours".format(truncate_float(sessional_run_time / 60 / 60, 2))
        )
        run_time_msg = "[Session lasted {}]".format(run_time_info)

        if any(stat for stat in stats):
            return (
                "Sessional Live Report:\n"
                "|> LIKED {} images\n"
                "|> ALREADY LIKED: {}\n"
                "|> COMMENTED on {} images\n"
                "|> FOLLOWED {} users\n"
                "|> ALREADY FOLLOWED: {}\n"
                "|> UNFOLLOWED {} users\n"
                "|> LIKED {} comments\n"
                "|> REPLIED to {} comments\n"
                "|> INAPPROPRIATE images: {}\n"
                "|> NOT VALID users: {}\n"
                "|> WATCHED {} story(ies)\n"
                "|> WATCHED {} reel(s)\n"
                "\n{}".format(
                    self.instapy_session.liked_img,
                    self.instapy_session.already_liked,
                    self.instapy_session.commented,
                    self.instapy_session.followed,
                    self.instapy_session.already_followed,
                    self.instapy_session.unfollowed,
                    self.instapy_session.liked_comments,
                    self.instapy_session.replied_to_comments,
                    self.instapy_session.inap_img,
                    self.instapy_session.not_valid_users,
                    self.instapy_session.stories_watched,
                    self.instapy_session.reels_watched,
                    run_time_msg,
                )
            )
        else:
            return (
                "Sessional Live Report:\n"
                "|> No any statistics to show\n"
                "\n{}".format(run_time_msg)
            )

    def end(self):
        """
        tidy up things
        :return:
        """
        # keep the chat_id session for future reference
        # so we don't need to send a message each time InstaPy restart to the bot
        # and we can keep on getting messages when the sessions finishes

        # send one last message to the user reporting the session
        if (self.__chat_id is not None) and (self.__context is not None):
            self.__context.bot.send_message(
                chat_id=self.__chat_id, text=self._live_report()
            )
        self.__updater.stop()
        self.token = ""
        self.telegram_username = ""
        self.instapy_session = None
        self.__chat_id = None
        self.__context = None
