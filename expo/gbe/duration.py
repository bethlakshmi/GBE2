
from datetime import timedelta

class Duration(timedelta):
    '''Wraps a timedelta to produce a more useful representation of an
    extent of time.  Will probably get rid of the timedelta presently
    Can be initialized in two ways: either using timdelta syntax, in
    days and seconds, or using keyword args hours, minutes, and
    seconds. If the latter sum to a positive value in seconds, that
    value is what we'll use. (we do not currently represent negative
    durations) 
    Note that set_format specifies the default (__str__)
    representation of this duration. By default, it's hh:mm:ss, but
    this format string can also access the days and total seconds
    as positional arguments 0 and 4 of the output tuple to format. 
    
    ''' 
    def __init__ (self, days = 0, hours=0, minutes=0, seconds=0):
        self.format_str = format_str="{1:0>2}:{2:0>2}:{3:0>2}"
        self.total_secs = days *24*3600 +hours*3600 + minutes*60+seconds
        if hours * 3600 + minutes * 60 + seconds >0:
            total_seconds = hours*3600 + minutes * 60 * seconds
            timedelta.__init__(total_seconds)
        else:
            super(timedelta, self)

    def set_format(self, format_str="{1:0>2}:{2:0>2}:{3:0>2}"):
        self.format_str = format_str
        return self

    def minutes(self):
        return int((self.total_seconds()/60)%60)
    def total_minutes (self):
        return int(self.total_seconds()/60)
    def hours (self):
        return int(self.total_seconds()/3600)


    def __str__(self):
        '''
        Default representation is hh:mm:ss 
        Use set_format to change representation
        '''
        return self.format_str.format (self.days, self.hours(), self.minutes(), self.seconds%60, self.total_seconds())
        
