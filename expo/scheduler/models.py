from django.db import models
from gbe.expomodelfields import DurationField
from django.core.validators import RegexValidator
from datetime import timedelta

# all literal text including option sets lives in gbetext.py
from gbetext import *


##  Object classes for the scheduler and calendar portions of the
##  GBE web app

class Properties(models.Model):
    '''
    What properties an item or room has.
    '''

    property_name = models.CharField(max_length = 256)

    def __unicode__(self):
        return self.property_name

class RoomTypes(models.Model):
    '''
    The Types of Rooms available to be scheduled.
    '''

    type = models.CharField(max_length=64)        
    descriptions = models.TextField()

    def __unicode__(self):
        return self.type

class Locations(models.Model):
    '''
    The types of locations available at the event site.  Has
    Properties for the various qualities of the space (has carpet
    or no, has movement space, has tables and chairs, etc).
    '''

    name = models.CharField(max_length=64)
    description = models.TextField()

    room_type = models.ForeignKey(RoomTypes)
    room_properties = models.ForeignKey(Properties)

    def __unicode__(self):
        return self.name

class EventTypes(models.Model):
    '''
    Choice List of Event Types, included in the Events to control
    what kind of an event an Event is.
    '''

    type = models.CharField(max_length=64)
    description = models.TextField()

    def __unicode__(self):
        return self.type

class MasterEvent(models.Model):
    '''
    A container object, within which event objects and item resources
    can be assigned.  Requires a start and stop date/time to be created.
    Properties:
        blocking - False, Hard, or Soft - issues warnings over conflicts
        start_sime - Date and Time the Event begins
        stop_time - Date and Time the Event ends
        item_type - List of the types of items the MasterEvent can
            contain.  Aay include Event, Users, Locations, or any type
            of table that can be scheduled.  Can include a subtype.
        viewable - Defines who can view the event on the schedule.
        event_type - The types of events the MasterEvent can contain.
    '''

    name = models.CharField(max_length = 128)
    description = models.TextField()
    start_time = models.DateTimeField(time_text[0])
    stop_time = models.DateTimeField(time_text[1])
    blocking = models.CharField(max_length=8, choices = blocking_text,
                                default = 'False')

    viewable = models.CharField(max_length = 2048)
    event_types = models.ManyToManyField(EventTypes)

    def __unicode__(self):
        return self.name

class Schedulable(models.Model):
    '''
    Handles the schedulability information for class that can be scheduled.
    Add this class to any class that you want to have inherit the ability
    to be scheduled as an event.
    '''

    @property
    def availability(self):
        '''
    Returns the availability of the object as a dictionary.
        '''
        return self.availability

    @property 
    def duration(self):
        '''
    Returns the duration of the event as a DurationField.
        '''
        return datetime.timedelta(0)

    @property
    def is_event(self):
        '''
    Returns True if this is an event.
        '''
        return True

    @property
    def viewability(self):
        '''
    Returns a list of people who are able to view the event on a calendar
    or schedule.
        '''
        return self.viewability

    @property
    def location(self, check_time):
        '''
    Return the location is scheduled to occur at.  Return void or null
    if the location is not set yet.
        '''
        return self.location

    @property
    def __unicode__(self):
        return self.name  

class Resource(models.Model):
    '''
    Inheritable class that makes things into resources that be scheduled.
    '''

    @property
    def availability(self):
        '''
    Returns the availability of the object as a dictionary.
        '''
        return self.availability

    @property
    def at_event(self, check_time):
        '''
    Returns the event_id of the event this resources is scheduled to be at.
        '''
        return self.at_event

##  This program has been brought to you by the language c and the number F.
