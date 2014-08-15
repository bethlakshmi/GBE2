# 
# ticketing_idd.py - Interface Design Description (IDD) between GBE and TICKETING modules
#
# edited by mdb 8/14/2014
#
#

# I confess, after the last 24 hours I don't really know where to begin with you, Jon.
#
# This document represents an IDD - Interface Design Description - that explains how our code 
# will work with each other.  
#
# When I worked for NAVSEA (Naval Sea Systems Command, see http://www.navsea.navy.mil) with a 
# TS-SSI (Special Top Secret, in layme's terms) clearance I used to write these all the time.  
# What this really means is that I was writing and integrating code (typically in C++) that 
# worked directly with inter-continental ballistic submarines in the Pacific submarine undersea
# fleet.  The submarines I worked with (fully manned, by the way) were typically in the Los 
# Angeles or Jimmy Carter class.
#
# So, yeah.  I wrote IDDs for software and wrote software itself (typically acoustics related, 
# one of the reasons I love Burlesque is I get to edit my own music) that is still in use with
# the majority of the United States Pacific submarine fleet.  And, by the way, the Pacific 
# (specifically because of the Chinese government) still remains the greatest Naval threat to 
# the United States.
#
# How well do you sleep at night, Jon?
#
# Scratch and Betty have both asked me - in writing and verbally - to implement the Ticketing 
# module exactly as described in the Wiki Betty created on the GBE2 github repository.  This 
# means I will need to revert your code to accomplish this task.  It would probably be best if 
# you stayed out of that module while I do that. 
#
# My orders, from Betty and Scratch, are specific.
#
# -MDB 8/12/2014


def performer_act_submittal_link(user_name):
    '''
    defines the act submission url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the fee.
    
    user_name - Per wiki.  This is the user name of the user in question.
    returns - the URL string descibed above.  
    
    I confess - not sure how to make that clearer.
    '''
    
    returns "http://www.brownpapertickets.com/event/580174"
    

def verify_performer_app_paid(user_name):
    '''
    Verifies if a user has paid his or her application fee.
    
    user_name - Per wiki.  This is the user name of the user in question.
    returns - true if the system recognizes the application submittal fee is paid
    '''
     
    return ((len(user_name) % 2) == 0)
   

def verify_vendor_app_paid(user_name):
    '''
    Verifies user has paid a vendor submittal fee.
    
    user_name - Per wiki.  This is the user name of the user in question.
    returns - true if the system recognizes the vendor submittal fee is paid
     '''
     
    return ((len(user_name) % 2) == 0)
    
def verify_event_paid(user_name, event_id):
    '''
    This is extra.  Verifies if a user has paid for a given event.  
    
    user_name - Per wiki.  This is the user name of the user in question.
    event_id - six digit BPT number that indicates if given user has paid for given event.
    returns - true if the system recognizes the fee is paid
    '''
     
    return ((len(user_name) % 2) == 0)
    
    