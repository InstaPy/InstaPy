from .time_util import sleep
from random import randint
from random import choice

def average_sleep(average_sec):
  """Build a random millisecond wait based on average input"""

  random_sec = randint(int(average_sec//2),int(average_sec*1.5))
  random_milli = randint(0,9999)
  unique_sleep = float(str(random_sec) + "." + str(random_milli))
  sleep(unique_sleep)

  return


def delete_line_from_file(filepath, lineToDelete):
    try:
        f = open(filepath,"r")
        lines = f.readlines()
        f.close()
        f = open(filepath,"w")

        for line in lines:

          if line!= lineToDelete:
            f.write(line)
        f.close()
    except BaseException as e:
        print("delete_line_from_file error \n", str(e))

def scroll_bottom(browser, element, range_int):

    # put a limit to the scrolling 
    if range_int > 50: range_int = 50

    for i in range(int(range_int/2)):
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        average_sleep(1)

    return
