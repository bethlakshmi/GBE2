# 
# brown_paper.py - Contains Functions for Integration with Brown Paper Tickets
# edited by mdb 5/25/2014
#
#

import urllib2
from django.utils import timezone
import xml.etree.ElementTree as et
from ticketing.models import *
import HTMLParser

    
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

def get_bpt_event_description(event_id):
    '''
    Used to get the description of the event as given in BPT.
 
    event_id - the event id for the event to query
    Returns: the description.
    '''
    
    event_call = 'http://www.brownpapertickets.com/api2/eventlist?id=%s&client=%s&event_id=%s' % \
        (get_bpt_developer_id(), get_bpt_client_id(), event_id)    
    event_xml = perform_bpt_api_call(event_call)
    
    if (event_xml == None):
        return None
    
    h = HTMLParser.HTMLParser()
    descr = h.unescape(event_xml.find('.//e_description').text)
    return descr
    
def get_bpt_event_date_list(event_id):
    '''
    Used to get the list of date identifiers from the BPT website for the given event.
 
    event_id - the event id for the event to query
    Returns: the date list requested, as a python list.
    '''
    
    date_call = 'http://www.brownpapertickets.com/api2/datelist?id=%s&event_id=%s' % \
        (get_bpt_developer_id(), event_id)
    date_xml = perform_bpt_api_call(date_call)
    
    if (date_xml == None):
        return None
    
    date_list = []
    for date in date_xml.findall('.//date_id'):
        date_list.append(date.text)
    return date_list

def get_bpt_price_list():
    '''
    Used to get the list of prices from BPT - which directly relates to ticket items on our system.

    Returns: the price list as an array of TicketItems.
    '''
    
    if (BrownPaperEvents.objects.count() <= 0):
        return []
        
    ti_list = []
           
    for event in BrownPaperEvents.objects.all():
        event_text = get_bpt_event_description(event.bpt_event_id)
        
        for date in get_bpt_event_date_list(event.bpt_event_id):
        
            price_call = 'http://www.brownpapertickets.com/api2/pricelist?id=%s&event_id=%s&date_id=%s' % \
                (get_bpt_developer_id(), event.bpt_event_id, date)           
            price_xml = perform_bpt_api_call(price_call)
            
            for price in price_xml.findall('.//price'):
                ti_list.append(bpt_price_to_ticketitem(event.bpt_event_id, price, event_text))
            
    return ti_list

def bpt_price_to_ticketitem(event_id, bpt_price, event_text):
    '''
    Function takes an XML price object from the BPT pricelist call and returns an
    equivalent TicketItem object.
    
    event_id - the Event ID associated with this price
    bpt_price - the price object from the BPT call
    event_text - Text that describes the event from BPT
    Returns:  the TicketItem
    '''

    t_item = TicketItem()
    t_item.ticket_id = '%s-%s' % (event_id, bpt_price.find('price_id').text)
    t_item.title = bpt_price.find('name').text
    t_item.active = False
    t_item.cost = bpt_price.find('value').text
    t_item.description = event_text    
    t_item.modified_by = 'BPT Auto Import'
    
    return t_item
    
    
def process_bpt_order_list():
    '''
    Used to get the list of current orders in the BPT database and update the 
    transaction table accordingly.  

    "Well, let the record show that this is one of many corrections that have now been made accordingly. "
        -- Sue Harrington, 'How's Your News?'         
    
    Returns: the number of transactions imported.
    '''
    
    if (BrownPaperEvents.objects.count() <= 0):
        return 0
    
    count = 0
    
    for event in BrownPaperEvents.objects.all():
        order_list_call = 'http://www.brownpapertickets.com/api2/orderlist?id=%s&event_id=%s&account=%s&includetracker=1' % \
            (get_bpt_developer_id(), event.bpt_event_id, get_bpt_client_id())           
        order_list_xml = perform_bpt_api_call(order_list_call)
        
       
        for bpt_order in order_list_xml.findall('.//item'):
            ticket_number = bpt_order.find('ticket_number').text
            
            if not (transaction_reference_exists(ticket_number)):
                bpt_save_order_to_database(event.bpt_event_id, bpt_order)
                count += 1
            
      
    set_bpt_last_poll_time()
    return count
    

def bpt_save_order_to_database(event_id, bpt_order):
    '''
    Function takes an XML order object from the BPT order list call and returns an
    equivalent transaction object. 
        
    event_id - the ID of the event associated to this order
    bpt_order - the order object from the BPT call
    Returns:  the Transaction object.  May throw an exception.
    '''
    
    trans = Transaction()
   
    # Locate the TicketItem or throw exception if it doesn't exist.  
    
    ticket_item_id = '%s-%s' % (event_id, bpt_order.find('price_id').text)
    trans.ticket_item = TicketItem.objects.get(ticket_id=ticket_item_id)
    trans.amount = trans.ticket_item.cost
    
    # Build a purchaser object.
    
    purchaser = Purchaser()
    purchaser.first_name = str(bpt_order.find('fname').text)
    purchaser.last_name = str(bpt_order.find('lname').text)
    purchaser.address = str(bpt_order.find('address').text )
    purchaser.city = str(bpt_order.find('city').text)
    purchaser.state = str(bpt_order.find('state').text)
    purchaser.zip = str(bpt_order.find('zip').text)
    purchaser.country = str(bpt_order.find('country').text)
    purchaser.email = str(bpt_order.find('email').text)
    purchaser.phone = str(bpt_order.find('phone').text)
    
    # This is a little bit of a hack.. if we don't know who the user is that
    # purchased the ticket, we assign it to the admin user. 
    
    purchaser.matched_to_user = User.objects.get(username='admin')
    
    # Attempt to see if purchaser exists in database, otherwise it is new.
        
    pur_id = locate_matching_purchaser(purchaser)
    if (pur_id != -1):
        print "Found Purchaser"
        trans.purchaser = Purchaser.objects.get(id=pur_id)
    else:
        trans.purchaser = purchaser
        purchaser.save()
        
    # Build out the remainder of the transaction.
    
    trans.order_date = bpt_order.find('order_time').text
    trans.shipping_method = str(bpt_order.find('shipping_method').text)
    trans.order_notes = str(bpt_order.find('order_notes').text)
    trans.reference = bpt_order.find('ticket_number').text
    trans.payment_source = 'Brown Paper Tickets'    
    
    trans.save()

    
def locate_matching_purchaser(other_pur):
    '''
    Function returns a purchaser object ID if the given purchaser is equivalent
    to one found in the database.  Otherwise returns -1
    
    other_p - the purchaser to use for comparison.
    returns - the ID if it exists, otherwise -1
    '''
    
    for pur in Purchaser.objects.all():
        if (pur == other_pur):
            return pur.id
    return -1
    
    
def transaction_reference_exists(ref_id):
    '''
    Function checks to see if a transaction with the given reference ID exists
    in the database.  If so, we don't want to duplicat the information.
    
    ref_id - the reference id to check.
    returns - true if it exists, false if not.
    '''
    
    return (Transaction.objects.filter(reference=ref_id).count() > 0)
    
'''

/* function process_bpt_order_list
 * 
 * Used to get the list of current orders in the BPT database and update the 
 * transaction table accordingly.
 *
 * Returns: Number of transactions imported.
 */
function process_bpt_order_list()
{
	$count = 0;
	truncate_limbo_table();
	$event_array = get_bpt_event_list();
	
	
	foreach ($event_array as $event_id)
	{
		$order_list_call = sprintf("https://www.brownpapertickets.com/api2/orderlist?id=%s&event_id=%s&account=%s&includetracker=1", 
			get_bpt_developer_id(), $event_id, get_bpt_client_id());
		$order_list_xml = perform_bpt_api_call($order_list_call);
		
		foreach ($order_list_xml->item as $order)
		{		
			if (!transaction_reference_exists((string)$order->ticket_number))
			{
				create_trans_from_bpt_order($event_id, $order, $trans);
				if ($trans == null)
					continue;
				for ($i = 0; $i < (int)$order->quantity; $i++)
				{	
					$trans->save_to_db(true, false);
					$count++;
				}
			}
		}
	}
	set_bpt_last_poll_time();
	return $count;
}
   
'''   

        
  