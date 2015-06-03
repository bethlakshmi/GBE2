##  Wrapper and skeleton for logging messages to a log file

from logging import *

try:
    from expo.localsettings import log_file
except:
    from expo.settings import log_file

try:
    from expo.localsettings import log_level
except:
    from expo.settings import log_level
try:
    from expo.localsettings import log_format
except:
    from expo.settings import log_format

logger = getLogger(__name__)
basicConfig(filename=log_file, level=log_level, format=log_format)

def log_func(object):
    '''
    Use as a decorator to log a function call or similar on the info level.
    '''
    
    def __call__(*args, **kwargs):
        if log_level == 'debug':

            out_text = object.func_name+' - args :\n'+str(args)+'\n---------\nkwargs:\n'+str(kwargs)+'\n---------\n'
        else:
            out_text = object.func_name
        logger.info(out_text)
        return object(*args, **kwargs)
    return __call__

