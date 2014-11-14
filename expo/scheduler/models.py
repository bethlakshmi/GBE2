from django.db import models
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from model_utils.managers import InheritanceManager
from gbetext import *
from gbe.expomodelfields import DurationField

import pytz


##  Object classes for the scheduler and calendar portions of the
##  GBE web app


class Schedulable(models.Model):
    '''
    Interface for an item that can appear on a conference schedule - either an 
    event or a resource allocation. (resource allocations can include, eg, volunteer 
    commitments for a particular person, or for a particular event, or for a block
    of time - so this is a pretty flexible idea)
    Note that conference models should NEVER inherit this directly or indirectly. This is why we use the 
    indirection model: we don't want to store scheduler data in the conference model. 
    '''
    objects = InheritanceManager()


    @property 
    def duration(self):
        return self._duration

    @property
    def start_time(self):
        return self.starttime
    
    @property
    def end_time(self):
        return self.starttime + self.duration
    
    def __unicode__(self):
        if self.start_time:
            return "Start: " + str(self.starttime.astimezone(pytz.timezone('America/New_York')))
        else:
            return "No Start Time"

    def __str__(self):
        if self.start_time:
            return "Start: " + str(self.starttime.astimezone(pytz.timezone('America/New_York')))
        else:
            return "No Start Time"

    class Meta:
        verbose_name_plural='Schedulable Items'
    
class ResourceItem (models.Model):
    '''
    The payload for a resource
    '''
    objects = InheritanceManager()

    @property
    def payload(self):
        return self._payload

    @property 
    def _name(self):
        return self.sched_name
    
    @property
    def describe(self):
        child = ResourceItem.objects.get_subclass(id=self.id)
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)
    
    pass

class Resource(models.Model):
    '''
    A person, place, or thing that can be allocated for an event. 
    A resource has a payload and properties derived from that payload. 
    This is basically a tag interface, allowing us to select all resources. 
    '''
    objects = InheritanceManager()


    @property
    def item (self):
        return self._item

    def __str__(self):
        allocated_resource = Resource.objects.get_subclass(id=self.id)
        if allocated_resource:
            return "Resource Allocation: "+str(allocated_resource)
        else:
            return "Error in resource allocation, no resource"
            
    def __unicode__(self):
        return self.__str__()
    

    
class LocationItem(ResourceItem):
    '''
    "Payload" object for a Location
    '''
    objects = InheritanceManager()
    

    def get_resource(self):
        '''
        Return the resource corresonding to this item
        To do: find a way to make this work at the Resource level
        '''
        l = Location.objects.select_subclasses().get(_item=self)
        if len(l) == 0:
            loc =  Location(_item=self)
            loc.save()
            return loc
        else:
            return l[0]
            # to do: log an error if len (l) >1

    @property
    def describe(self):
        return LocationItem.objects.get_subclass(id=self.id).name

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)

class Location(Resource):
    '''
    A resource which is a location. 
    '''
    objects = InheritanceManager()
    _item = models.ForeignKey(LocationItem)
    
    def __str__(self):
        try:
            return self.item.describe
        except:
            return "No Location Item"

    def __unicode__(self):
        try:
            return self.item.describe
        except:
            return "No Location Item"

class WorkerItem(ResourceItem):
    '''
    Payload object for a person as resource (staff/volunteer/teacher)
    '''
    objects = InheritanceManager()
    
    @property
    def describe(self):
        child = WorkerItem.objects.get_subclass(id=self.id)
        
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)
    
    pass

class Worker (Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = models.ForeignKey(WorkerItem)
    role = models.CharField(max_length=50,
                                    choices=role_options, 
                                    blank=True)
    
    def __str__(self):
        try:
            return self.item.describe
        except:
            return "No Worker Item"

    def __unicode__(self):
        try:
            return self.item.describe
        except:
            return "No Worker Item"

class EquipmentItem(ResourceItem):
    '''
    Payload object for an allocatable item
    Not currently used
    '''
    objects = InheritanceManager()
    
    @property
    def describe(self):
        return "Equipment Item"

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)
    
    pass

class Equipment(Resource):
    '''
    An allocatable thing
    Not currently used. Probably needs a good bit of development before we can really use it
    (we'd like to be able to allocate single objects, sets of objects, and quantities of objects
    at the very least - this requires a bit of design)
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
    eventitem_id = models.AutoField(primary_key=True)

    def set_duration(self, duration):
        child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
        child.duration = duration
        child.save(update_fields=('duration',))

    @property
    def payload(self):
        return self.sched_payload

    @property
    def bios(self):
        return self.bio_payload

    @property 
    def duration(self):
        child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
        return child.sched_duration
    
    @property
    def describe(self):
        try:
            child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
            ids = "event - " + str(child.event_id)
            try:
                ids += ', bid - ' + str(child.id)
            except:
                ids += ""
            return child.type + ":  " + str(child.sched_payload.get('title')) + "; ids: " + ids
        except:
            return "no child"

    


    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)

    

class Event (Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload. 
    '''
    objects = InheritanceManager()
    eventitem = models.ForeignKey(EventItem, related_name = "scheduler_events")                             
    starttime = models.DateTimeField(blank=True)


    def set_location(self, location):
        '''
        location is a LocationItem, not a Location resource
        '''
        if isinstance(location, Location):
            location = location._item
        if self.location == location:
            pass   # already set
        elif self.location == None:
            loc_resource = location.get_resource()
            ra = ResourceAllocation(location=location, event=self)
            ra.save()
        else:
            allocations = ResourceAllocation.objects.select_subclasses().filter(event=self).filter(location=location)
            if len (allocations) >0:
                allocation = [a for a in allocations if type(a.resource)=='Location'][0]  
                ## Probably should log an error if there is more than one location allocated for this event
                allocation.resource=location.get_resource()
                allocation.save()
        
    def set_duration(self, duration):
        '''
        duration should be a gbe.Duration or a timedelta
        
        '''
        self.eventitem.set_duration(duration)

    @property
    def duration(self):
        return self.eventitem.duration

    def __str__(self):
        try:
            return self.eventitem.describe
        except:
            return "No Event Item"

    def __unicode__(self):
        try:
            return self.eventitem.describe
        except:
            return "No Event Item"
        
    @property
    def location(self):
        l = Location.objects.filter(allocations__event=self)
        if len(l) > 0:
            return l[0]._item
        else:
            return None  # or what??

        

class ResourceAllocation(Schedulable):
    '''
    Joins a particular Resource to a particular Event
    ResourceAllocations get their scheduling data from their Event. 
    '''
    objects = InheritanceManager()
    event = models.ForeignKey(Event, related_name="resources_allocated")
    resource = models.ForeignKey(Resource, related_name="allocations")

    @property 
    def start_time(self):
        return self.event.starttime

    def __str__(self):
        try:
            return str(self.start_time.astimezone(pytz.timezone('America/New_York'))) + \
                   " :: Event: " + str(self.event) + " == " + \
                   str(Resource.objects.get_subclass(id=self.resource.id).__class__.__name__) + \
                   ": " + str(Resource.objects.get_subclass(id=self.resource.id))
        except:
            return "Missing an Item"

    def __unicode__(self):
        try:
            return unicode(self.start_time.astimezone(pytz.timezone('America/New_York'))) + \
                   " :: Event: " + unicode(self.event) + " == " + \
                   unicode(Resource.objects.get_subclass(id=self.resource.id).__class__.__name__) + \
                   ": " + unicode(Resource.objects.get_subclass(id=self.resource.id))
        except:
            return "Missing an Item"
