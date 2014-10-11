# 
# models.py - Contains Django Database Models for Ticketing - Defines Database Schema
# edited by mdb 8/18/2014
#

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
    
class BrownPaperSettings(models.Model):
    '''
    This class is used to hold basic settings for the interface with BPT.  It should
    contain only one row and almost never changes.
    '''
    developer_token = models.CharField(max_length=15, primary_key=True)
    client_username = models.CharField(max_length=30)
    last_poll_time = models.DateTimeField()
    
    def __unicode__(self):
        return 'Settings:  %s (%s) - %s' % (self.developer_token, self.client_username, self.last_poll_time)
    
    
class BrownPaperEvents(models.Model):
    '''
    This class is used to hold the BPT event list.  It defines with Brown Paper Ticket
    Events should be queried to obtain information on the Ticket Items above.  This 
    information mainly remains static - it is set up info for the interface with BPT.
    '''
    bpt_event_id = models.CharField(max_length=10, primary_key=True)
    primary = models.BooleanField(default=False)  
    act_submission_event = models.BooleanField(default=False)
    vendor_submission_event = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.bpt_event_id
        
class TicketItem(models.Model):
    '''
    This class represents a type of ticket.  Examples include 'The Whole Shebang',
    'Fan Admission', 'The Main Event', and so forth.  A ticket may admit to multiple
    events.  
    '''    
    ticket_id = models.CharField(max_length=30)
    title = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    linked_events = models.ManyToManyField('gbe.Event', related_name='ticketing_item')
    datestamp = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=30)

    def __unicode__(self):
        return '%s %s' % (self.ticket_id, self.title)
        
class Purchaser(models.Model):
    '''
    This class is used to hold the information for a given person who has purchased 
    a ticket at BPT.  It has all the information we can gather from BPT about the
    user.  It is meant to be mapped to a given User in our system, if we can.
    
    These are pretty much all char fields since we don't know the format of what 
    BPT (or another system) will hand back.
    '''
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    
    # Note - if this is none, then we don't know who to match this purchase to in our
    # system.  This scenario will be pretty common. 
    
    matched_to_user = models.ForeignKey(User, default=None)
    
    def __unicode__(self):
        return '%s %s (%s) matched to user: %s' % (self.first_name, self.last_name, self.email, self.matched_to_user)
        
    def __eq__(self, other):
        if not isinstance(other, Purchaser):
            return False
        
        if ((self.first_name != other.first_name) or 
            (self.last_name != other.last_name) or 
            (self.address != other.address) or 
            (self.city != other.city) or 
            (self.state != other.state) or 
            (self.zip != other.zip) or 
            (self.country != other.country) or 
            (self.email != other.email) or 
            (self.phone != other.phone)):
            return False
        return True
    
    def __ne__(self, other):
        if not isinstance(other, Purchaser):
            return True
        return not self.__eq__(other)
        
    
class Transaction(models.Model):
    ''' 
    This class holds transaction records from an external source - in this case,
    Brown Paper Tickets.  Transactions are associated to a purchaser and a specific
    ticket item.
    '''
    
    ticket_item = models.ForeignKey(TicketItem)
    purchaser = models.ForeignKey(Purchaser)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    order_date = models.DateTimeField()
    shipping_method = models.CharField(max_length=50)
    order_notes = models.TextField()
    reference = models.CharField(max_length=30)
    payment_source = models.CharField(max_length=30)
    import_date = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return '%s (%s)' % (self.reference, self.purchaser)
    
