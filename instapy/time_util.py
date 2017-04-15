"""Helper module to handle time related stuff"""
import random
import time


# Amount of variance to be introduced
# i.e. random time will be in the range: TIME +/- STDEV %
STDEV = 0.5

def randomize_time(mean):
  allowed_range = mean * STDEV
  stdev = allowed_range / 3  # 99.73% chance to be in the allowed range

  t = 0
  while abs(mean - t) > allowed_range:
    t = random.gauss(mean, stdev)

  return t


def sleep(t):
  time.sleep(randomize_time(t))
