
from datetime import timedelta

class Duration(timedelta):
    def __init__ (self, *args, **kwargs):
        super(timedelta, self)
    

    def __str__(self):
        return ':'.join(map(str, [self.seconds/60,self.seconds%60]))
