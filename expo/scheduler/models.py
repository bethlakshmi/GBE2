from django.db import models
from gbe.expomodelfields import DurationField
from django.core.validators import RegexValidator
from datetime import timedelta
from model_utils.managers import InheritanceManager
from gbetext import *


##  Object classes for the scheduler and calendar portions of the
##  GBE web app


class Schedulable(models.Model):
    '''
    Interface for an item that can appear on a conference schedule - either an 
    event or a resource allocation. (resource allocations can include, eg, volunteer 
    commitments for a particular person, or for a particular event, or for a block
    of time - so this is a pretty flexible idea)
    '''
    objects = InheritanceManager()
    @property 
    def duration(self):
        return self._duration

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self.start_time + self.duration

    



class ResourceItem (models.Model):
    '''
    The payload for a resource
    '''
    objects = InheritanceManager()
    @property 
    def _name(self):
        return self.sched_name

class Resource(models.Model):
    '''
    A person, place, or thing that can be allocated for an event. 
    A resource has a payload and properties derived from that payload. 
    '''
    objects = InheritanceManager()
    @property
    def item(self):
        return self._item
    @property
    def name(self):
        return self.item.sched_name
    
class LocationItem(ResourceItem):
    '''
    A wrapper class for a conference location
    '''
    objects = InheritanceManager()
    pass

class Location(Resource):
    '''
    A resource which is a location. 
    '''
    objects = InheritanceManager()
    _item = models.ForeignKey(LocationItem)

class WorkerItem(ResourceItem):
    '''
    Wrapper class for a person as resource (staff/volunteer/teacher)
    '''
    objects = InheritanceManager()
    pass

class Worker (Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = models.ForeignKey(WorkerItem)

class EquipmentItem(ResourceItem):
    objects = InheritanceManager()
    pass

class Equipment(Resource):
    '''
    An allocatable thing
    '''
    objects = InheritanceManager()
    _item = models.ForeignKey(EquipmentItem)

class EventItem (models.Model):
    '''
    The payload for an event (ie, a class, act, show, or generic event)
    The EventItem MUST NOT impose any DB usage on its implementing model classes. 
    ALL requirements must be stated as properties.
    '''
    objects = InheritanceManager()
    @property 
    def duration(self):
        return self.sched_duration
        
class Event (Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload. 
    '''
    objects = InheritanceManager()
    @property
    def duration(self):
        return self.item._duration


    


class ResourceAllocation(Schedulable):
    '''
    Joins a particular Resource to a particular Event
    ResourceAllocations get their scheduling data from their Event. 
    '''
    objects = InheritanceManager()
    event = models.ForeignKey(Event, related_name="resources_allocated")
    resource = models.ForeignKey(Resource, related_name="allocations")

