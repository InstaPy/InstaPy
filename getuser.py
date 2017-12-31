import csv
from random import randint

def get_one_user():
    users_array = []
    filename = 'setup.csv'
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = reader.next()
        for row in reader:
            users_array.append(row)

    selected_user = None
    picked_user = None
    attempts = 10000
    while selected_user == None and attempts > 0:
        random_user = randint(0, len(users_array) - 1)
        if(int(users_array[random_user][len(users_array[random_user])-1]) == 0):
            selected_user = users_array[random_user]
            picked_user = reduce_user(headers, selected_user)

        # Making sure I don't have an infinite loop
        attempts -= 1

    return picked_user


def reduce_user(headers, selected_user):
    if(selected_user == None):
        return
    user = dict(zip(headers, selected_user))

    try:
        user['username'] = user['username'].strip()
    except:
        print("reduce rebound")

    try:
        user['password'] = user['password'].strip()
    except:
        print("reduce rebound")

    try:
        user['tags'] = user['tags'].split(", ")
    except:
        print("reduce rebound")

    try:
        user['like_by_tags'] = int(user['like_by_tags'])
    except:
        print("reduce rebound")

    try:
        user['dont_like'] = user['dont_like'].split(", ")
    except:
        print("reduce rebound")

    try:
        user['do_follow'] = int(user['do_follow'])
        if user['do_follow'] == 1:
            user['do_follow'] = True
        else:
            user['do_follow'] = False
    except:
        print("reduce rebound")

    try:
        user['follow_percentage'] = int(user['follow_percentage'])
    except:
        print("reduce rebound")

    try:
        user['unfollow_count'] = int(user['unfollow_count'])
    except:
        print("reduce rebound")

    try:
        user['do_comment'] = int(user['do_comment'])
        if user['do_comment'] == 1:
            user['do_comment'] = True
        else:
            user['do_comment'] = False
    except:
        print("reduce rebound")

    try:
        user['comment_percentage'] = int(user['comment_percentage'])
    except:
        print("reduce rebound")

    try:
        user['comments'] = user['comments'].split(", ")
    except:
        print("reduce rebound")

    try:
        user['follower_upper_limit'] = int(user['follower_upper_limit'])
    except:
        print("reduce rebound")

    try:
        user['follower_lower_limit'] = int(user['follower_lower_limit'])
    except:
        print("reduce rebound")

    try:
        user['headless_browser'] = int(user['headless_browser'])
    except:
        print("reduce rebound")

    try:
        user['fans'] = user['fans'].split(", ")
    except:
        print("reduce rebound")

    return user

def lock_user(username):
    if(username == None):
        return
    filename = 'setup.csv'
    setup_file = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            setup_file.append(row)

    for i, row in enumerate(setup_file):
        if(row[0] == username):
            setup_file[i][len(setup_file[i])-1] = '1'

    with open(filename, mode='wb') as outfile:
        writer = csv.writer(outfile)
        for row in setup_file:
            writer.writerow(row)