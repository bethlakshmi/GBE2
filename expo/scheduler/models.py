from django.db import models
from django.core.validators import RegexValidator

# all literal text including option sets lives in gbetext.py
from gbetext import *


##  Object classes for the scheduler and calendar portions of the
##  GBE web app

class Properties(models.Model):
    '''
    What properties an item has.  Include this class in the inheritance
    chain to give an object properties and property checking.
    '''

    property_name = models.CharField(max_length = 256)

    def __unicode__(self):
        return self.property_name

class Property(models.Model):
    '''
    Individual Property handler, allows a property to have multiple
    field values, such as True/False, Integer, Choice List, etc.
    '''

    property_info = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.property_info

class EventTypes(models.Model):
    '''
    Choice List of Event Types, included in the Events to control
    what kind of an event an Event is.
    '''

    type = models.CharField(max_length=256)

class MasterEvent(EventTypes, models.Model):
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
        item_list - List of items contained in the MasterEvent.  Each
            item corrosponds to an entry in DB for table for that
            items type, and is the index for that item.  SubTypes 
            corrospond to a subtype field on that table.
        event_type - The types of events the MasterEvent can contain.
    '''

    name = models.CharField(max_length = 128)
    description = models.TextField()
    start_time = models.DateTimeField(time_text[0])
    stop_time = models.DateTimeField(time_text[1])
    blocking = models.CharField(max_length=8, choices = blocking_text,
                                default = 'False')

    ###  These data object are stored as JSON object in the DB.
    ###  Gets packed into JSON objects in the forms file.
    item_list = models.CharField(max_length = 2048)
    viewable = models.CharField(max_length = 2048)
    ##event_type = models.CharField(max_length = 256, choices = event_types)

    def __unicode__(self):
        return self.name

class SchedEvent(models.Model):
    '''
    A container object to describe events on the timeline of the
    Master Event object.  Can be recursively assigned.
    Properties:
        hard_time, soft_time - Duration.  HardTime is the bounded
            time the event runs.  SoftTime is the combined times of all
            subevents and the local SoftTime.  A warning is given if
            total SoftTime is larger then the HardTime.  Setting 
            HardTime to 0 disables the warning, and causes the event
            to be scheduled for the total SoftTime.
        viewable - Defines who can view the event on the schedule.
        blocking - False, Hard, or Soft - issues warnings over conflicts
        item_type - List of the types of items the Event can
            contain.  Aay include Event, Users, Locations, or any type
            of table that can be scheduled.  Can include a subtype in the
            form of Type.Sub.
        item_list - List of items contained in the Event.
        event_type - The types of events this event can contain.
    '''

    name = models.CharField(max_length = 128)
    hard_time = models.TimeField(time_text[2])
    soft_time = models.TimeField(time_text[3])
    blocking = models.CharField(max_length=8, choices = blocking_text,
                                default = 'False')
    event_type = models.ForeignKey(EventTypes)

    ###  The below options are JSON object stored in the DB.
    ###  The are pack into JSON objects in the forms file.
    viewable = models.CharField(max_length=2048)
    ##event_type = models.CharField(max_length = 256, choices = event_types)
    item_list = models.CharField(max_length=2048)

    def __unicode__(self):
        return self.name  

class Schedulable(models.Model):
    '''
    Handles the schedulability information for class that can be scheduled.
    Add this class to any class that you want to have inherit the ability
    to be scheduled.
    Properties are:
        availability - DateTimes the item is available
        blocking - False, Hard, or Soft - issues warning for conflicts
    '''

    block = models.CharField(max_length=8, choices = blocking_text,
                                default = 'False')

    ###  Availability is a list of Start Date/Time | Stop Date/Time pairs
    ###  stored as a JSON object in the DB, set in the forms file.
    available = models.CharField(max_length = 2048)

    def availability(self):
        return self.available

    def blocking(self):
        return self.block


###  Object classes to manage locations and rooms.

class Locations(Schedulable, Properties, models.Model):
    '''
    The types of locations available at the event site.  Has
    Properties for the various qualities of the space (has carpet
    or no, has movement space, has tables and chairs, etc).
    '''

    name = models.CharField(max_length=32)
    description = models.TextField()

    ###  room_type is a choice from available room types,
    ###  which are stored as a JSON object containing 
    ###  a tuple of tuple pairs.  Can only have one type,
    ###  otherwise, is a type of property
    room_type = models.ForeignKey(RoomTypes)

    def __unicode__(self):
        return self.name

class RoomTypes(Properties, models.Model):
    '''
    The Types of Rooms available to be scheduled.
    '''

    type = models.CharField(max_length=64)

##  This program has been brought to you by the language c and the number F.
