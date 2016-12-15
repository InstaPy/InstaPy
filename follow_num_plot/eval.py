#!/usr/bin/env python3
import matplotlib.pyplot as plt

# contains information in format (date, followerNum)
information = []

def extractInfo(line):
    """Extracts information from line which is in format
    -> Data Time #follower 'followers'"""
    parts = line.split(' ')
    date = ' '.join(parts[:2])
    followerNum = parts[2]
    
    return (date, followerNum)

def savePlot(dates, followerNum):
    plt.figure(figsize=(50, 25))
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Number of Followers', fontsize=15)
    plt.grid(True)

    #plot the line
    plt.plot(range(0, len(dates)), followerNum, marker='o')

    #get the lowerbound "rounded down to 100"
    lowerbound = int(followerNum[0])
    lowerbound -= int(followerNum[0]) % 100

    #get the upperbound "rounded up to 100"
    upperbound = int(followerNum[-1])
    upperbound -= int(followerNum[-1]) % -100

    plt.xticks(range(0, len(dates) + 1), dates, rotation='vertical')
    plt.yticks(range(lowerbound, upperbound + 1, 10))

    plt.savefig('eval.png')

    
with open('./followerNum.txt') as follFile:
    for line in follFile:
        information.append(extractInfo(line))
        
dates = [info[0] for info in information]
followerNum = [info[1] for info in information]

savePlot(dates, followerNum)
