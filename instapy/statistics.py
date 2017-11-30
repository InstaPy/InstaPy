import datetime as _datetime
from .time_util import sleep

HOUR_START_DAY = 5
HOUR_END_DAY = 22

class InstaPyStorage(object):
    TOTAL_START_DAY = '16/10/2017'
    with open('./logs/maxday.txt', 'r') as file:
        MAX_PER_DAY = int(file.readline())
    with open('./logs/maxhour.txt', 'r') as file:
        MAX_PER_HOUR = int(file.readline())
    def __init__(self):
        self.total = 0
        self.thisDayTotal = 0
        self.thisHourTotal = 0
        self.lastDayExecuted = _datetime.date.today()
        self.lastHourExecuted = _datetime.datetime.now().hour
    def updateStatistics(self):
        # read today's date in 2008-11-22 format, and now time
        today = _datetime.date.today()
        now = _datetime.datetime.now()
        self.total += 1
        if self.lastDayExecuted == today:
            self.thisDayTotal += 1
            if self.lastHourExecuted == now.hour:
                self.thisHourTotal += 1
            else:
                self.lastHourExecuted = now.hour
                self.thisHourTotal = 1
        else:
            self.lastDayExecuted = today
            self.lastHourExecuted == now.hour
            self.thisHourTotal = 1
            self.thisDayTotal = 1

        # stop actions until time is
        if not (_datetime.time(HOUR_START_DAY, 0) <= now.time() <= _datetime.time(HOUR_END_DAY, 0)):
            # set the diff
            hoursTillNextStart = (HOUR_START_DAY-now.hour)
            # wrap around the hour
            if (_datetime.time(HOUR_END_DAY, 0) < now.time()):
                hoursTillNextStart += 24
                
            secsTillNextStart = (HOUR_START_DAY-self.lastHourExecuted)*3600
            print("hoursTillNextStart:", hoursTillNextStart)
            #sleep(secsTillNextStart)
            return 0
        else:
            # stop actions since the maximum actions per day reached
            if self.thisDayTotal >= self.MAX_PER_DAY:
                print('reached MAX_PER_DAY')
                sleep(3600)

            # stop actions since the maximum actions per this hour reached
            if self.thisHourTotal >= self.MAX_PER_HOUR:
                print('reached MAX_PER_HOUR')
                sleep(600)