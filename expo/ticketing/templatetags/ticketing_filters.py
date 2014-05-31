# 
# ticketing_filers.py - Contains Django Custom Template Filters for Ticketing
# edited by mdb 5/30/2014
#

from django import template
import re
register = template.Library()

@register.filter(name='bpt_event')
def bpt_event(ticket_item_id):
    '''
    This is a custom template filter to obtain the BPT Event ID from
    a ticket id created automatically from the BPT website.
    '''
    
    return re.split(r'-', ticket_item_id)[0]
    
    