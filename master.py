#!/usr/bin/python
try:
    print("==Starts to follow")
    import follow
except Exception as e:
    print("==Starts to follow threw an exception: {}". format(e))

try:
    print("==Starts to unfollow")
    import unfollow
except Exception as e:
    print("==Starts to unfollow threw an exception: {}". format(e))

try:
    print("==Starts my statictics")
    import meinerttt
except Exception as e:
    print("==Starts my statictics threw an exception: {}". format(e))