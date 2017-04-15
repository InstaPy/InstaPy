"""Helper module to handle time related stuff"""
from random import gauss
from time import sleep as original_sleep


# Amount of variance to be introduced
# i.e. random time will be in the range: TIME +/- STDEV %
STDEV = 0.5

def randomize_time(mean):
  allowed_range = mean * STDEV
  stdev = allowed_range / 3  # 99.73% chance to be in the allowed range

  t = 0
  while abs(mean - t) > allowed_range:
    t = gauss(mean, stdev)

  return t


def sleep(t):
  original_sleep(randomize_time(t))
