# 
# brown_paper.py - Contains Functions for Integration with Brown Paper Tickets
# edited by mdb 5/25/2014
#
# 9MLmigzTE2
# marcus.deboyz@gmail.com
# 2014-01-01 00:00:00
#
# 704952
#

import urllib2
from django.utils import timezone
import xml.etree.ElementTree as et
from ticketing.models import *

    
def perform_bpt_api_call(api_call):
    '''
    Used to make various calls to the Brown Paper Tickets API system.
    
    event_call - the API call to be performed.
    Returns: a Simple XML element tree or None for an error.
    '''
    try:
        req = urllib2.Request(api_call)
        req.add_header('Accept', 'application/json')
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        res = urllib2.urlopen(req)
        xml_tree = et.fromstring(res.read())  
    except urllib2.URLError as io_error:
        print 'Could not perform BPT call:  %s' % io_error.reason
        return None
    except:
        print 'Could not perform BPT call.  Reason unknown.'
        return None        
    return xml_tree

def get_bpt_developer_id():
    '''
    Used to obtain the developer token to be used with Brown Paper Tickets.
 
    Returns: the developer token, or None if none exists.
    '''

    if (BrownPaperSettings.objects.count() <= 0):
        return None
    settings = BrownPaperSettings.objects.all()[0]     
    return settings.developer_token
    
def get_bpt_client_id():
    '''
    Used to obtain the client username to be used with Brown Paper Tickets.
 
    Returns: the client username, or None if none exists.
    '''

    if (BrownPaperSettings.objects.count() <= 0):
        return None
    settings = BrownPaperSettings.objects.all()[0]     
    return settings.client_username
  
def get_bpt_last_poll_time():
    '''
    Used to obtain the last time the system poled BPT for transactions.
 
    Returns: the last poll time, or None if it doesn't exist.
    '''

    if (BrownPaperSettings.objects.count() <= 0):
        return None
    settings = BrownPaperSettings.objects.all()[0]     
    return settings.last_poll_time
    
def set_bpt_last_poll_time():
    '''
    Used to set the last time the system poled BPT for transactions to current time.
 
    Returns: nothing.
    '''
    if (BrownPaperSettings.objects.count() <= 0):
        return None
    settings = BrownPaperSettings.objects.all()[0]  
    settings.last_poll_time = timezone.now()
    settings.save()
    
def get_bpt_event_date_list(event_id):
    '''
    Used to get the list of date identifiers from the BPT website for the given event.
 
    event_id - the event id for the event to query
    Returns: the date list requested, as a python list.
    '''
    
    date_call = 'https://www.brownpapertickets.com/api2/datelist?id=%s&event_id=%s' % \
        (get_bpt_developer_id(), event_id)
    date_xml = perform_bpt_api_call(date_call)
    
    date_list = []
    for date in date_xml.iter('date_id'):
        date_list.append(date.text)
    return date_list

def get_bpt_event_list():
    '''
    Used to obtain an array of the current events we watch on the BPT website.  This is taken
    from the database.  
    
    Returns: An array of BPT event numbers.
    '''
    
    if (BrownPaperEvents.objects.count() <= 0):
        return None
    settings = BrownPaperSettings.objects.all()[0]     
    return settings.last_poll_time
    

def get_bpt_price_list():
    '''
    Used to get the list of prices from BPT - which directly relates to ticket items on our system.

    Returns: the price list as an array of TicketItems.
    '''
    
    if (BrownPaperEvents.objects.count() <= 0):
        return []
        
    ti_list = []
           
    for event in BrownPaperEvents.objects.all():
        for date in get_bpt_event_date_list(event.bpt_event_id):
        
            price_call = 'https://www.brownpapertickets.com/api2/pricelist?id=%s&event_id=%s&date_id=%s' % \
                (get_bpt_developer_id(), event.bpt_event_id, date)           
            price_xml = perform_bpt_api_call(price_call)
            
            for price in price_xml.iter('price'):
                ti_list.append(bpt_price_to_ticketitem(event.bpt_event_id, price))
            
    return ti_list

def bpt_price_to_ticketitem(event_id, bpt_price):
    '''
    Function takes an XML price object from the BPT pricelist call and returns an
    equivalent TicketItem object.
    
    event_id - the Event ID associated with this price
    bpt_price - the price object from the BPT call
    Returns:  the TicketItem
    '''

    t_item = TicketItem()
    t_item.id = '%s-%s' % (event_id, bpt_price.find('price_id').text)
    t_item.title = bpt_price.find('name').text
    t_item.active = bpt_price.find('live').text
    t_item.cost = bpt_price.find('value').text
    t_item.description = '*** Auto-Import from BPT ***'    
    
    return t_item
   


        
  