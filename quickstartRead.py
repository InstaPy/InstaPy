import shutil, errno
import os, sys
import pickle
import instapy

def read_likes_statistics():
    with open('./logs/likesLimitLogFile.pkl', 'rb') as input:
        likes = pickle.load(input)
    print('--\ntotal Likes', likes.total, 'from date:', likes.TOTAL_START_DAY)
    print('this Day Total Likes:', likes.thisDayTotal)
    print('this Hour Total Likes:', likes.thisHourTotal)
    print('Day Executed last Likes:', likes.lastDayExecuted)
    print('Hour Executed last Likes:', likes.lastHourExecuted)
    print('--')


def read_follows_statistics():
    with open('./logs/followsLimitLogFile.pkl', 'rb') as input:
        follows = pickle.load(input)
    print('MAX_PER_HOUR', follows.MAX_PER_HOUR, 'MAX_PER_DAY', follows.MAX_PER_DAY)
    print('--\ntotal follows', follows.total, 'from date:', follows.TOTAL_START_DAY)
    print('this Day Total follows:', follows.thisDayTotal)
    print('this Hour Total follows:', follows.thisHourTotal)
    print('Day Executed last follow:', follows.lastDayExecuted)
    print('Hour Executed last follow:', follows.lastHourExecuted)
	
read_likes_statistics()
read_follows_statistics()