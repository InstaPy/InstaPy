import re

def read_whole_file(logfile):
    whole_file = ''
    
    with open(logfile, 'r') as read_file:
        for line in read_file:
            if not line.startswith('[') and not '(' in line:
                #whole_file += line
                print(line)
            
    return whole_file

whole_file = read_whole_file('logFile.txt')



session_start = 'started - (20[\d]{2}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2})'

tags = 'Tag \[\d\/\d\]--> (\w+)'

liked = 'Liked: (\d+)\nA'

commented = 'Commented: (\d+)'