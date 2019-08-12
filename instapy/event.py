class Event:
    """Event Singleton Class

    How to use example:
    from .event import Event
    Event().profile_data_updated(400, 312)
    """

    singleton = None
    callbacks = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = object.__new__(Event)
        return cls.singleton

    def __init__(self):
        pass

    def fire_callbacks(self, function_name, *args, **kwargs):
        if function_name not in self.callbacks:
            return
        for callback in self.callbacks[function_name]:
            callback(*args, **kwargs)

    def add_callback(self, function_name, callback):
        if function_name not in self.callbacks:
            self.callbacks[function_name] = []

        self.callbacks[function_name].append(callback)

    # place custom events below
    def profile_data_updated(self, username, followers_count, following_count):
        self.fire_callbacks(
            self.profile_data_updated.__name__,
            username,
            followers_count,
            following_count,
        )

    def commented(self, username):
        self.fire_callbacks(self.commented.__name__, username)

    def liked(self, username):
        self.fire_callbacks(self.liked.__name__, username)

    def followed(self, username):
        self.fire_callbacks(self.followed.__name__, username)

    def unfollowed(self, username):
        self.fire_callbacks(self.unfollowed.__name__, username)
