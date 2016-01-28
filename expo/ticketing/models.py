# 
# models.py - Contains Django Database Models for Ticketing - Defines Database Schema
# edited by mdb 8/18/2014
#

from django.db import models
from django.contrib.auth.models import User
from gbe.models import Conference
from gbetext import role_options

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
    class Meta:
        verbose_name_plural='Brown Paper Settings'
    
class BrownPaperEvents(models.Model):
    '''
    This class is used to hold the BPT event list.  It defines with Brown Paper
    Ticket Events should be queried to obtain information on the Ticket Items
    above.  This information mainly remains static - it is set up info for the
    interface with BPT.
    
      - include_conferece = if True this event provides tickets for all parts
            of the conference - Classes, Panels, Workshops - but not Master
            Classes
      - include_most = includes everything EXCEPT Master Classes
      
    '''
    bpt_event_id = models.CharField(max_length=10)
    primary = models.BooleanField(default=False)  
    act_submission_event = models.BooleanField(default=False,
                                               verbose_name='Act Fee')
    vendor_submission_event = models.BooleanField(default=False,
                                                  verbose_name='Vendor Fee')
    linked_events = models.ManyToManyField('gbe.Event',
                                           related_name='ticketing_item',
                                           blank=True)
    include_conference = models.BooleanField(default=False)
    include_most = models.BooleanField(default=False)
    badgeable = models.BooleanField(default=False)
    ticket_style = models.CharField(max_length=50, blank=True)
    conference = models.ForeignKey('gbe.Conference',
                                   related_name='ticketing_item',
                                   default=lambda: Conference.objects.filter(status="upcoming").first())
    
    def __unicode__(self):
        return self.bpt_event_id
    class Meta:
        verbose_name_plural='Brown Paper Events'
        
class TicketItem(models.Model):
    '''
    This class represents a type of ticket.  There is one ticket per price point,
    so an event like the Whole Shebang can have 10 or so different ticket - early bird,
    various discount codes, full price, etc.
      - active = whether the ticket should be actively displayed on the website.  Manually
          set
      - ticket_id = is calculated to conjoin event and ticket identifiers from BPT
    '''    
    ticket_id = models.CharField(max_length=30)
    title = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    datestamp = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=30)
    bpt_event = models.ForeignKey(BrownPaperEvents,
                                  related_name="ticketitems",
                                  blank=True) 
   
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
        try:
            return str(self.matched_to_user)
        except:
            return "USER ERROR: "+self.email+' - id: '+str(self.id)
        
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
    
class CheckListItem(models.Model):
    '''
    This is a physical item that we can give away at the registration desk
    Examples:  a badge, a wristband, a goodie bag, a guidebook, a release
    form, etc.  It may or may not be labeled for a specific users (for example,
    a badge has a name on it)
    '''
    description = models.CharField(max_length=50, unique=True)

class EligibilityCondition(models.Model):
    '''
    This is the paremt class connecting the conditions under which a
    CheckListItem can be given to the conditions themselves.
    
    Conditions are logically additive unless eliminated by exclusions.
    So if 3 conditions give an item with no exclusion, then the individual
    gets 3 items.
    
    TO Discuss (post expo) - consider making this abstract and using content 
    types to link the exclusion foreign key to abstract cases of this class.
    '''
    checklist_item = models.ForeignKey(
        CheckListItem,
        related_name="%(app_label)s_%(class)s")


class TicketingEligibilityCondition(EligibilityCondition):
    '''
    This is the implementation of the condition under which we give a
    checklist item to a purchaser because they have purchased a ticket
    Tickets are realized as BPT Events, the various tickets within an
    event do not qualify a user for anything more.
    
    Ticket conditions are additive.  X purchases = X items given to the
    buyer
    '''
    bpt_event = models.ForeignKey(BrownPaperEvents,
                                  blank=False) 

    class Meta:
        abstract = True


class RoleEligibilityCondition(EligibilityCondition):
    '''
    This is the implementation of the condition under which we give a
    checklist item to a person because they fulfill an assigned role.
    
    Roles are given once per person per conference - being a role
    gets exactly 1 of the item.
    '''
    role = models.CharField(max_length=25,
                            choices=role_options)

    class Meta:
        abstract = True

class Exclusion(models.Model):
    '''
    This is the abstract class connecting the cases under which a
    CheckListItem should be assigned, even when it meets the current
    condition.  Exclusions are combined in many to 1 conditions as
    logical OR cases - any case being true negates the condition.
    '''
    condition = models.ForeignKey(
        EligibilityCondition,
        related_name="%(app_label)s_%(class)s")

    class Meta:
        abstract = True


class TicketingExclusion(Exclusion):
    '''
    This is the implementation of the case when the presence of a ticket
    purchase eliminates the eligibility of the individual for getting the
    checklist item under the given condition.  The usual case is that a
    person purchased a ticket that includes an equivalent to the current
    item and maybe more.
    '''
    bpt_event = models.ForeignKey(BrownPaperEvents,
                                  blank=False) 

    class Meta:
        abstract = True


class RoleExclusion(Exclusion):
    '''
    This is the implementation of the case under which we don't give a ticket
    because of the event that the person is participating in.  This is largely
    because we know the person will not be able to participate in an event
    they are contributing to - for example a performer in a show.
    
    If no event, then the implication is that being this role for ANY event
    means the exclusion takes effect
    '''
    role = models.CharField(max_length=25,
                            choices=role_options)
    event = models.ForeignKey('gbe.Event', blank=True)

    class Meta:
        abstract = True

