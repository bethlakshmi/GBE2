# 
# ticketing_idd.py - Interface Design Description (IDD) between GBE and TICKETING modules
#
# edited by mdb 8/14/2014
#
#

# See documentation in https://github.com/bethlakshmi/GBE2/wiki/Ticketing-To-Do
# section:  "By Friday - needed for integration"
# - Betty 8/15


def performer_act_submittal_link(user_name):
    '''
    defines the act submission url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the fee.
    
    user_name - This is the user name of the user in question.
    returns - the URL string descibed above.  
    
    '''
    
    returns "http://www.brownpapertickets.com/event/580174"
    

def verify_performer_app_paid(user_name):
    '''
    Verifies if a user has paid his or her application fee.
    
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the application submittal fee is paid
    '''
     
    return ((len(user_name) % 2) == 0)
   

def verify_vendor_app_paid(user_name):
    '''
    Verifies user has paid a vendor submittal fee.
    
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the vendor submittal fee is paid
     '''
     
    return ((len(user_name) % 2) == 0)
    
def verify_event_paid(user_name, event_id):
    '''
    This is extra.  Verifies if a user has paid for a given event.  
    
    user_name - This is the user name of the user in question.
    event_id - six digit BPT number that indicates if given user has paid for given event.
    returns - true if the system recognizes the fee is paid
    '''
     
    return ((len(user_name) % 2) == 0)
    
    