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

def saveLinearPlot(dates, followerNum):
    plt.figure(figsize=(50, 25))
    plt.xlabel('Date', fontsize=15)
    plt.ylabel('Number of Followers', fontsize=15)
    plt.grid(True)

    #plot the line
    plt.plot(range(len(dates)), followerNum, marker='o')

    #get the lowerbound "rounded down to 100"
    lowerbound = int(followerNum[0])
    lowerbound -= int(followerNum[0]) % 100

    #get the upperbound "rounded up to 100"
    upperbound = int(followerNum[-1])
    upperbound -= int(followerNum[-1]) % -100

    plt.xticks(range(len(dates)), dates, rotation='vertical')
    plt.yticks(range(lowerbound, upperbound + 1, 10))

    plt.savefig('eval.png')

def saveBarPlot(dates, followerNum):
    plt.figure(figsize=(20, 10))
    diffs = []
    for i in range(len(followerNum) - 1):
        diffs.append(followerNum[i + 1] - followerNum[i])
    
    plt.bar(range(len(dates) - 1), diffs, 1/1.5, color="blue")
    
    plt.savefig('bar.png')

with open('./followerNum.txt') as follFile:
    for line in follFile:
        information.append(extractInfo(line))
        
dates = [info[0] for info in information]
followerNum = [int(info[1]) for info in information]

saveLinearPlot(dates, followerNum)
saveBarPlot(dates, followerNum)
