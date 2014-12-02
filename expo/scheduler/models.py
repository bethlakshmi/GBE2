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
    resourceitem_id = models.AutoField(primary_key=True)
    @property
    def payload(self):
        return self._payload

    @property 
    def _name(self):
        return self.sched_name
    
    @property
    def describe(self):
        child = ResourceItem.objects.get_subclass(resourceitem_id=self.resourceitem_id)
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
    
class ActItem(ResourceItem):
    '''
    Payload object for an Act
    '''
    objects = InheritanceManager()

    @property
    def bio(self):
        return ActItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).bio

    @property
    def visible(self):
        return ActItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).visible

    def get_resource(self):
        '''
        Return the resource corresonding to this item
        To do: find a way to make this work at the Resource level
        '''
        try:
            loc = ActResource.objects.select_subclasses().get(_item=self)
        except:
            loc =  ActResource(_item=self)
            loc.save()
        return loc


    @property
    def describe (self):
        return ActItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).title

    def __str__(self):
        return str(self.describe)

    def __unicode__(self):
        return unicode(self.describe)

class ActResource(Resource):
    '''
    A schedulable object wrapping an Act
    '''
    objects = InheritanceManager()
    _item = models.ForeignKey(ActItem)
    
    def __str__(self):
        try:
            return self.item.describe
        except:
            return "No Act Item"

    def __unicode__(self):
        try:
            return self.item.describe
        except:
            return "No Act Item"    



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
        try:
            loc = Location.objects.select_subclasses().get(_item=self)
        except:
            loc =  Location(_item=self)
            loc.save()
        return loc

    @property
    def describe(self):
        return LocationItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).name

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
        child = WorkerItem.objects.get_subclass(resourceitem_id=self.resourceitem_id)
        
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)
    
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

    @property
    def bios(self):
        people = WorkerItem.objects.filter(worker__allocations__event__eventitem=self.eventitem_id,
                                           worker__role__in=['Teacher','Panelist','Moderator']).distinct().select_subclasses('performer')
        if people.count() == 0:
            people = self.bio_payload
        return people

    def set_duration(self, duration):
        child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
        child.duration = duration
        child.save(update_fields=('duration',))

        
    @property
    def payload(self):
        return self.sched_payload


    @property 
    def duration(self):
        child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
        return child.sched_duration
    
    @property
    def describe(self):
        try:
            child = EventItem.objects.filter(eventitem_id=self.eventitem_id).select_subclasses()[0]
            '''
            ids = "event - " + str(child.event_id)
            try:
                ids += ', bid - ' + str(child.id)
            except:
                ids += ""
            '''
            return str(child.sched_payload.get('title')) 
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
    max_volunteer = models.IntegerField(default=0)

    def set_location(self, location):
        '''
        location is a LocationItem or a Location resource
        '''
        if isinstance(location, LocationItem):
            location = location.get_resource()
        if self.location == location:
            pass   # already set
        elif self.location == None:
            ra = ResourceAllocation(resource=location, event=self)
            ra.save()
        else:
            allocations = ResourceAllocation.objects.filter(event=self)
            for allocation in allocations:
                if isinstance(allocation.resource.location, Location):
                    allocation.resource=location
                    allocation.save(update_fields=('resource',))


                
    def set_duration(self, duration):
        '''
        duration should be a gbe.Duration or a timedelta
        
        '''
        self.eventitem.set_duration(duration)

    @property
    def duration(self):
        return self.eventitem.duration

    # for a long list of bios, right now, that is acts in shows.
    @property
    def bio_list(self):
        bio_list = []
        last_perf = False
#        acts = ActResource.objects.filter(allocations__event=self, _item__act__accepted=3).order_by('_item__act__performer')
        acts = ActResource.objects.filter(allocations__event=self, _item__act__accepted=3)
        # BB - this is a very cheesy way of doing select distinct on performer
        # problem is - SQL lite doesn't support select distinct on
        bio_list = list(set([act._item.bio for act in acts]))
        bio_list = sorted(bio_list, key = lambda bio:bio.name)
#        for act in acts:
#            if not last_perf:
#                bio_list += [act._item.bio]
#            elif last_perf != act._item.bio:
#                bio_list += [act._item.bio]
#            last_perf=act._item.bio
        return bio_list

    # for a shorter list of bios - 1-2 or so, as with Workeritems

         
        
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
