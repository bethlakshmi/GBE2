##  Wrapper and skeleton for logging messages to a log file

from logging import *

try:
    from expo.local_settings import LOG_FILE
except:
    from expo.settings import LOG_FILE

try:
    from expo.local_settings import LOG_LEVEL
except:
    from expo.settings import LOG_LEVEL
try:
    from expo.local_settings import LOG_FORMAT
except:
    from expo.settings import LOG_FORMAT

logger = getLogger(__name__)
basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=LOG_FORMAT)

def log_func(funct):
    '''
    Use as a decorator to log a function call or similar on the info level.
    '''
    
    def __call__(*args, **kwargs):
        if LOG_LEVEL in ('debug', 'error', 'critical'):

            out_text = funct.func_name+' - args :\n'+str(args)+'\n---------\nkwargs:\n'+str(kwargs)+'\n---------\n'
        else:
            out_text = funct.func_name
        logger.info(out_text)
        return funct(*args, **kwargs)
    return __call__

def procinfo(proc_value = False):
    '''
    Returns information from the proc status file.  Uses the headers from the file to determine
    what gets returned.  See the proc man page for more info.  Very Linux specific.
    '''

    procfile = open('/proc/self/status', 'r')
    procdict = {}

    for line in procfile.readlines():
        text = line.split()
        procdict[text[0][:-1]] = text[1]

    if proc_value:
        tmp_dict = {}
        if type(proc_value) == type(''):
            return procdict[proc_value]
        elif type(proc_value) in [type([]), type({})]:
            for pval in proc_value:
                tmp_dict[pval] = procdict[pval]
        return tmp_dict
    else:
        return procdict

def memusage():
    '''
    Returns the memory footprint of the current instance, in kilobytes.
    '''

    from resource import getrusage, RUSAGE_SELF
    return getrusage(RUSAGE_SELF).rumaxrss
