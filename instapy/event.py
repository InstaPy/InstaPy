class Event:  
    '''Event Singleton Class

    How to use:
    from .event import Event
    Event().image_liked(image)
    '''

    singleton = None 
   
    def __new__(cls, *args, **kwargs):  
        if not cls.singleton:  
            cls.singleton = object.__new__(InfluxDBLog)  
        return cls.singleton  
   
    def __init__(self):
        pass

    def image_liked(self, image):
        pass
