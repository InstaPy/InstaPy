"""Helper module to handle time related stuff"""
from time import sleep as original_sleep
from datetime import datetime
from random import gauss
from random import uniform
from random import randint
from random import seed
from sys import path
from os import get_exec_path
from os import getpid
from os import times

# Amount of variance to be introduced
# i.e. random time will be in the range: TIME +/- STDEV %
STDEV = 0.5
sleep_percentage = 1
sleep_percentage = sleep_percentage * uniform(0.9, 1.1)

path_str = path[0] + get_exec_path()[0] + path[-1] + get_exec_path()[-1] + str(getpid())


def new_seed():
    seed(str(randint(0, 1_000_000)) + str(times()) + str(datetime.now()) + path_str)


def randomize_time(mean):
    allowed_range = mean * STDEV
    stdev = allowed_range / 3  # 99.73% chance to be in the allowed range

    t = 0
    while abs(mean - t) > allowed_range:
        t = gauss(mean, stdev)

    return t


def set_sleep_percentage(percentage):
    global sleep_percentage
    sleep_percentage = percentage / 100
    sleep_percentage = sleep_percentage * uniform(0.9, 1.1)


def sleep(t, custom_percentage=None):
    # new seed each time this function is called
    new_seed()
    
    if custom_percentage is None:
        custom_percentage = sleep_percentage
    time = randomize_time(t) * custom_percentage
    original_sleep(time)


def sleep_actual(t):
    original_sleep(t)


def get_time(labels):
    """ To get a use out of this helpful function
        catch in the same order of passed parameters """
    if not isinstance(labels, list):
        labels = [labels]

    results = []

    for label in labels:
        if label == "this_minute":
            results.append(datetime.now().strftime("%M"))

        if label == "this_hour":
            results.append(datetime.now().strftime("%H"))

        elif label == "today":
            results.append(datetime.now().strftime("%Y-%m-%d"))

    results = results if len(results) > 1 else results[0]

    return results
