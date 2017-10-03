from .time_util import sleep
from random import randint
from random import choice


def delete_line_from_file(filepath, lineToDelete):
    try:
        f = open(filepath, "r")
        lines = f.readlines()
        f.close()
        f = open(filepath, "w")

        for line in lines:

            if line != lineToDelete:
                f.write(line)
        f.close()
    except BaseException as e:
        print("delete_line_from_file error \n", str(e))


def scroll_bottom(browser, element, range_int, full_scroll = False):
    # put a limit to the scrolling
    sleep_time = 1
    if range_int > 50 and full_scroll == False:
        range_int = 50
    else:
        sleep_time = randint(3, 7)

    for i in range(int(range_int / 2)):
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        sleep(sleep_time)

    return

def formatNumber(number):
    formattedNum = number.replace(',', '').replace('.', '')
    formattedNum = int(formattedNum.replace('k', '00').replace('m', '00000'))
    return formattedNum
