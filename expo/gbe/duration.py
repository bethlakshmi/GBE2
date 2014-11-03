
from datetime import timedelta

class Duration(timedelta):
    '''
    Wraps a timedelta to produce a more useful representation of an extent of time. 
    Will probably get rid of the timedelta presently
    Can be initialized in two ways: either using timdelta syntax, in days and seconds, 
    or using keyword args hours, minutes, and seconds. If the latter sum to a positive 
    value in seconds, that value is what we'll use. (we do not currently represent 
    negative durations)
    '''
    def __init__ (self, days = 0, hours=0, minutes=0, seconds=0, **kwargs):
        self.total_secs = hours*3600 + minutes*60+seconds
        if hours * 3600 + minutes * 60 + seconds >0:
            total_seconds = hours*3600 + minutes * 60 * seconds
            timedelta.__init__(total_seconds)
        else:
            super(timedelta, self)
    def minutes(self):
        return (self.total_seconds()/60)%60
    def total_minutes (self):
        return self.total_seconds()/60
    def hours (self):
        return self.total_seconds()/3600
    

    def __str__(self):
        '''
        Default representation is hh:mm
        '''
        return '%02d:%02d:%02d' % (self.hours(), self.minutes(), self.seconds%60)
        
