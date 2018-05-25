import random 
from instapy import InstaPy
import os
import multiprocessing
import datetime
import time

instaUser = ['catalinbardas', 'mircea_dragomir']
instaPass = ['atitudinE22c', 'NOEMIaviMircea651']
tags=[['surf','music','beachtime'],['beverlyhills','gourmet','beachlife']]

def worker(selection):
    
    print("MULTI - Started as",instaUser[selection],"at",datetime.datetime.now().strftime("%H:%M:%S"))

    session = InstaPy(username=instaUser[selection], password=instaPass[selection], headless_browser=True,bypass_suspicious_attempt=True, multi_logs=True)
    session.login()

    session.like_by_tags(tags[selection], amount=30)
    session.end()
    print("MULTI -",instaUser[selection],"finished run at",datetime.datetime.now().strftime("%H:%M:%S"))

if __name__ == '__main__':        
    print("MULTI -","Starting at",datetime.datetime.now().strftime("%H:%M:%S"))
    jobs = []
    for i in range(len(instaUser)):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
        time.sleep(3)#no delay cause some instances of chrome to give errors and stop