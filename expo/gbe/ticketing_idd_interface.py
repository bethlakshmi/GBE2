# 
# ticketing_idd.py - Interface Design Description (IDD) between GBE and TICKETING modules
#
# edited by mdb 8/14/2014
#
#

# See documentation in https://github.com/bethlakshmi/GBE2/wiki/Ticketing-To-Do
# section:  "By Friday - needed for integration"
# - Betty 8/15

from ticketing.models import *
from gbe.models import *
from ticketing.brown_paper import *
from gbetext import *   

def performer_act_submittal_link(username):
    '''
    defines the act submission url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the fee.
    
    I removed the argument for user_name as it is not used.  -mdb
      
    returns - the URL string described above.  
    '''
    
    act_sub_events = BrownPaperEvents.objects.filter(act_submission_event=True)
    if (act_sub_events.count() > 0):
        return 'http://www.brownpapertickets.com/event/ID-' + username + '/' + act_sub_events[0].bpt_event_id
    return None
    
    
def vendor_submittal_link():
    '''
    defines the vendor url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the fee.
    
    I forgot to add this function when I did the initial submit of this.  -mdb
    
    returns - the URL string described above.  
    '''
    
    vendor_events = BrownPaperEvents.objects.filter(vendor_submission_event=True)
    if (vendor_events.count() > 0):
        return 'http://www.brownpapertickets.com/event/ID-' + username + '/' + vendor_events[0].bpt_event_id
    return None
    

def verify_performer_app_paid(user_name):
    '''
    Verifies if a user has paid his or her application fee.

    NOTE:  This function assumes that there is a record of the application, saved in the database,
    with a status of "submitted", at the time the check is performed.  
    
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the application submittal fee is paid
    
    '''
        
    act_fees_purchased = 0
    acts_submitted = 0
    
    # First figure out how many acts this user has purchased
    
    for act_event in BrownPaperEvents.objects.filter(act_submission_event=True):
        for trans in Transaction.objects.all():
            trans_event = trans.ticket_item.ticket_id.split('-')[0]
            trans_user_name = trans.purchaser.matched_to_user.username

            if ((act_event.bpt_event_id == trans_event) and (unicode(user_name) == trans_user_name)):
                act_fees_purchased += 1

    # Then figure out how many acts have already been submitted.
                
    for act in Act.objects.filter(submitted=True):  
        act_user_name = None
   
        try:
            # I'm anticipating a user may not exist, so just skip for an exception   
            act_user_name = act.performer.contact.user_object.username
        except:
            pass
        
        if act_user_name == unicode(user_name):
            acts_submitted += 1
        
    #print "Purchased Count:  %s  Submitted Count:  %s" % (act_fees_purchased, acts_submitted)
    return act_fees_purchased >= acts_submitted
   

def verify_vendor_app_paid(user_name):
    '''
    Verifies user has paid a vendor submittal fee.
    
    NOTE:  This function assumes that there is a record of the application, saved in the database,
    with a status of "submitted", at the time the check is performed.  
    
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the vendor submittal fee is paid
    
    '''
        
    vendor_fees_purchased = 0
    vendor_apps_submitted = 0
    
    # First figure out how many vendor spots this user has purchased
    
    for vendor_event in BrownPaperEvents.objects.filter(vendor_submission_event=True):
        for trans in Transaction.objects.all():
            trans_event = trans.ticket_item.ticket_id.split('-')[0]
            trans_user_name = trans.purchaser.matched_to_user.username

            if ((vendor_event.bpt_event_id == trans_event) and (unicode(user_name) == trans_user_name)):
                vendor_fees_purchased += 1

    # Then figure out how many vendor applications have already been submitted.
                
    for vendor in Vendor.objects.filter(submitted=True):  
        vendor_user_name = None
   
        try:
            # I'm anticipating a user may not exist, so just skip for an exception   
            vendor_user_name = vendor.profile.user_object_username
        except:
            pass
        
        if vendor_user_name == unicode(user_name):
            vendor_apps_submitted += 1
        
    #print "Purchased Count:  %s  Submitted Count:  %s" % (vendor_fees_purchased, vendor_apps_submitted)
        
    return vendor_fees_purchased >= vendor_apps_submitted
    return False
    
def verify_event_paid(user_name, event_id):
    '''
    This is extra.  Verifies if a user has paid at least once for a given event.  
    
    user_name - This is the user name of the user in question.
    event_id - six digit BPT number that indicates if given user has paid for given event.
    returns - true if the system recognizes the fee is paid
    '''
     
    for trans in Transaction.objects.all():
        trans_event = trans.ticket_item.ticket_id.split('-')[0]
        trans_user_name = trans.purchaser.matched_to_user.username

        if ((unicode(event_id) == trans_event) and (unicode(user_name) == trans_user_name)):
            return True
            
    return False
 
    