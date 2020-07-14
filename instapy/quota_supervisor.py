""" Realtime and sophisticated quota supervising mechanisms """
import time as epoch_time
from datetime import time, timedelta, date, datetime
import random
from sys import platform
import sqlite3
from plyer import notification
from pkg_resources import resource_filename as get_pkg_resource_path

from .time_util import sleep_actual
from .time_util import get_time
from .database_engine import get_database
from .settings import Settings
from .settings import Storage


def quota_supervisor(job, update=False):
    """ Supervise activity flow through action engines and take measures"""
    # --ACTION----------ENGINE--------------FILE--------------OPTION--- #
    #   Like         `like_image`       [like_util.py]      jump|sleep  #
    #   Comment      `comment_image`    [comment_util.py]   jump|sleep  #
    #   Follow       `follow_user`      [unfollow_util.py]  jump|sleep  #
    #   Unfollow     `unfollow_user`    [unfollow_util.py]  jump|sleep  #
    #  *Server call  `update_activity`  [util.py]           exit|sleep  #
    # ----------------------------------------------------------------- #

    global configuration
    configuration = Settings.QS_config

    if configuration and configuration["state"] is True:
        # in-file global variables for the QS family
        global records, logger, this_minute, this_hour, today

        records = Storage.record_activity
        logger = Settings.logger
        this_minute, this_hour, today = get_time(["this_minute", "this_hour", "today"])
        if update:  # update the action's record in global storage
            update_record(job)

        else:  # inspect and control the action's availability
            quota_state = controller(job)
            return quota_state


def controller(job):
    """ Control and supervise """
    if not records:
        load_records()

    sleep_after = configuration["sleep_after"]
    sleepyhead = configuration["sleepyhead"]
    notify = configuration["notify"]
    peaks = configuration["peaks"]

    if configuration["stochasticity"]["enabled"] is True:
        stochasticity(peaks)

    # inspect
    supervise, interval, target = inspector(job, peaks)

    if supervise:
        if (
            any(
                e in [job, job + ("_h" if interval == "hourly" else "_d")]
                for e in sleep_after
            )
            and target != "lc_extra"
        ):
            nap = remaining_time(sleepyhead, interval)
            send_message(job, "sleep", interval, nap)

            toast_notification(notify, "sleep", job, interval)
            sleep_actual(nap)
            toast_notification(notify, "wakeup", job, interval)

        else:
            if job == "server_calls":
                send_message(job, "exit", interval, None)
                toast_notification(notify, "exit", job, interval)

                logger.warning(
                    "You're about to leave the session. " "InstaPy will exit soon!"
                )
                exit()

            else:
                send_message(job, "jump", interval, None)
                return "jump"

    return "available"


def inspector(job, peaks):
    """ Inspect action and return end result """
    lc_extra_check_h, lc_extra_check_d = False, False

    hourly_peak = peaks[job]["hourly"]
    daily_peak = peaks[job]["daily"]

    # if like record exceeds its peak value, no comment will not also be sent
    if job == "comments":
        hourly_like_peak = peaks["likes"]["hourly"]
        daily_like_peak = peaks["likes"]["daily"]

        # interesting catch: use `>` instead of '>=' here :D
        if hourly_like_peak is not None:
            hourly_like_record = get_record("likes", "hourly")
            lc_extra_check_h = hourly_like_record > hourly_like_peak

        if daily_like_peak is not None:
            daily_like_record = get_record("likes", "daily")
            lc_extra_check_d = daily_like_record > daily_like_peak

    # inspect
    if hourly_peak is not None:
        hourly_record = get_record(job, "hourly")

        if hourly_record >= hourly_peak:
            return True, "hourly", "job"

    if daily_peak is not None:
        daily_record = get_record(job, "daily")

        if daily_record >= daily_peak:
            return True, "daily", "job"

    # extra like & comment inspection
    if lc_extra_check_h:
        return True, "hourly", "lc_extra"

    elif lc_extra_check_d:
        return True, "daily", "lc_extra"

    # inspection completed without a quotient breach
    return False, None, None


def stochasticity(peaks):
    """ Generate casually chosen arbitrary peak values based on originals
    set by the user """
    # in future, stochasticity percentage can be added to th QS parameters
    # for users to define
    stoch_percent = random.randint(70, 85)  # over 70, below 85 would be good

    orig_peaks = configuration["stochasticity"]["original_peaks"]
    latesttime = configuration["stochasticity"]["latesttime"]
    latesttime_h = latesttime["hourly"]
    latesttime_d = latesttime["daily"]
    realtime = epoch_time.time()

    # renew peak values at relative range just after an hour
    hourly_cycle = (realtime - latesttime_h) >= 3750
    # about ~one day (most people will not reach 86400 seconds, so, smaller
    # is better)
    daily_cycle = (realtime - latesttime_d) >= 27144

    if hourly_cycle or daily_cycle:
        # simplify 2 (possible) STEPs into 1 sequenced loop
        while hourly_cycle or daily_cycle:
            interval = "hourly" if hourly_cycle else "daily"
            stochast_values(peaks, orig_peaks, interval, stoch_percent)
            # update the latest time of value renewal in the given interval
            latesttime[interval] = epoch_time.time()

            if hourly_cycle:
                logger.info(
                    "Quota Supervisor: just updated hourly peak rates in "
                    "stochastic probablity!"
                )
                # turn off hourly cycle to avoid recycling
                hourly_cycle = False

            elif daily_cycle:
                logger.info(
                    "Quota Supervisor: just updated daily peak rates in "
                    "stochastic probablity!"
                )
                # turn off daily cycle to avoid recycling
                daily_cycle = False


def stochast_values(peaks, orig_peaks, interval, percent):
    """ Return randomly generated stochastic peak values """
    for job in orig_peaks:
        job_data = orig_peaks[job]

        stochastic_peak = (
            None
            if job_data[interval] is None
            else stoch_randomizer(job_data[interval], percent)
        )

        # update the peaks object with a stochastic value for the given job
        peaks[job][interval] = stochastic_peak


def stoch_randomizer(value, percent):
    """ Value randomizer for stochastic flow """
    stochastic_value = random.randint(int((value + 1) * percent / 100), value)

    return stochastic_value


def remaining_time(sleepyhead, interval):
    """ Calculate wake up time and return accurate or close-range random
    sleep seconds """
    extra_sleep_percent = 140  # actually 114 also is not that bad amount

    if interval == "hourly":
        remaining_seconds = (61 - int(this_minute)) * 60

    elif interval == "daily":
        tomorrow = date.today() + timedelta(1)
        midnight = datetime.combine(tomorrow, time())
        now = datetime.now()
        remaining_seconds = (midnight - now).seconds

    if sleepyhead is True:
        remaining_seconds = random.randint(
            remaining_seconds, int(remaining_seconds * extra_sleep_percent / 100)
        )

    return remaining_seconds


def send_message(job, action, interval, nap):
    """ Send information messages about QS states """
    job = job.replace("_", " ")

    if action == "sleep":
        if interval == "hourly":
            quick_drink = random.choice(
                [
                    "lemon tea",
                    "black tea",
                    "green tea",
                    "grey tea",
                    "coffee mexicano",
                    "coffee colombia",
                    "fruit juice",
                ]
            )
            message = (
                "Quota Supervisor: hourly {} reached quotient!"
                "\t~going to sleep {} minutes long\n\ttake a {} "
                "break? :>".format(job, "%.0f" % (nap / 60), quick_drink)
            )

        elif interval == "daily":
            message = (
                "Quota Supervisor: daily {} reached quotient!"
                "\t~going to sleep {} hours long\n"
                "\ttime for InstaPy to take a big good nap :-)".format(
                    job, "%.1f" % (nap / 60 / 60)
                )
            )

    elif action == "exit":
        message = (
            "Quota Supervisor: {} {} reached quotient!"
            "\t~exiting\n\tfor *non-stop botting use `sleep_after` "
            "parameter on the go! ;)".format(interval, job)
        )

    elif action == "jump":
        message = (
            "Quota Supervisor: jumped a {} out of {} quotient!\t~be fair "
            "with numbers :]\n".format(job[:-1], interval)
        )

    logger.info(message)


def toast_notification(notify, alert, job, interval):
    """ Send toast notifications about supervising states directly to OS
    using 'plyer' module """
    platform_matches = platform.startswith(("win32", "linux", "darwin"))
    if notify is True and platform_matches:
        icons = get_icons()
        delay = 9 if alert == "exit" else 7
        label = job.replace("_", " ").capitalize()

        expr = (
            "Yawn! {} filled {} quotient!\t~falling asleep a little bit :>"
            if alert == "sleep"
            else "Yikes! {} just woke up from {} quotient bandage!\t~let's "
            "chill again wakey ;)"
            if alert == "wakeup"
            else "D'oh! {} finished {} quotient!\t~exiting ~,~"
        )

        try:
            notification.notify(
                title="Quota Supervisor",
                message=expr.format(label, interval),
                app_name="InstaPy",
                app_icon=icons[alert],
                timeout=delay,
                ticker="To switch supervising methods, please review "
                "quickstart script",
            )

        except Exception:
            # TypeError: out of 'plyer' bug in python 2 - INNER EXCEPTION
            # NotImplementedError: when 'plyer' is not supported
            # DBusException: dbus-display issue on linux boxes

            # turn off toast notification for the rest of the session
            configuration.update(notify=False)


def get_icons():
    """ Return the locations of icons according to the operating system """
    # get full location of icons folder inside package
    icons_path = get_pkg_resource_path("instapy", "icons/")

    windows_ico = [
        "Windows/qs_sleep_windows.ico",
        "Windows/qs_wakeup_windows.ico",
        "Windows/qs_exit_windows.ico",
    ]
    linux_png = [
        "Linux/qs_sleep_linux.png",
        "Linux/qs_wakeup_linux.png",
        "Linux/qs_exit_linux.png",
    ]
    mac_icns = [
        "Mac/qs_sleep_mac.icns",
        "Mac/qs_wakeup_mac.icns",
        "Mac/qs_exit_mac.icns",
    ]

    # make it full path now
    windows_ico = [icons_path + icon for icon in windows_ico]
    linux_png = [icons_path + icon for icon in linux_png]
    mac_icns = [icons_path + icon for icon in mac_icns]

    (sleep_icon, wakeup_icon, exit_icon) = (
        windows_ico
        if platform.startswith("win32")
        else linux_png
        if platform.startswith("linux")
        else mac_icns
        if platform.startswith("darwin")
        else [None, None, None]
    )

    icons = {"sleep": sleep_icon, "wakeup": wakeup_icon, "exit": exit_icon}

    return icons


def load_records():
    """ Load the data from local DB file """
    db, profile_id = get_database()
    conn = sqlite3.connect(db)

    # fetch live data from database
    with conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM recordActivity "
            "WHERE profile_id=:var AND "
            "STRFTIME('%Y-%m-%d', created) == "
            "STRFTIME('%Y-%m-%d', 'now', 'localtime')",
            {"var": profile_id},
        )
        daily_data = cur.fetchall()

    if daily_data:
        ordered_data = {today: {}}

        # iterate over hourly rows and re-order data in the required structure
        for hourly_data in daily_data:
            hourly_data = tuple(hourly_data)
            hour = hourly_data[-1][-8:-6]

            ordered_data[today].update(
                {
                    hour: {
                        "likes": hourly_data[1],
                        "comments": hourly_data[2],
                        "follows": hourly_data[3],
                        "unfollows": hourly_data[4],
                        "server_calls": hourly_data[5],
                    }
                }
            )

        # load data to the global storage
        records.update(ordered_data)


def get_record(job, interval):
    """ Quickly get and return daily or hourly records """
    try:
        if interval == "hourly":
            record = records[today][this_hour][job]

        elif interval == "daily":
            record = sum(i[1][job] for i in list(records[today].items()))

    except KeyError:
        # record does not yet exist
        record = 0

    return record


def update_record(job):
    """ Update the corresponding record stored in the global Storage class """
    # the order of the 2 conditional statements below is crucial
    if today not in records.keys():
        records.update({today: {this_hour: {}}})

    elif this_hour not in records[today].keys():
        records[today].update({this_hour: {}})

    # get live record
    live_rec = records[today][this_hour].get(job, 0) + 1

    # update records
    records[today][this_hour].update({job: live_rec})
