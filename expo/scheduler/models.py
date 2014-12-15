from django.db import models
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from model_utils.managers import InheritanceManager
from gbetext import *
from gbe.expomodelfields import DurationField
from scheduler.functions import set_time_format

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
        child = Schedulable.objects.get_subclass(id=self.id)
        try:
            return child.starttime
        except:
            return None
    
    @property
    def end_time(self):
        return self.starttime + self.duration
    
    def __unicode__(self):
        if self.start_time:
            return "Start: " + str(self.start_time.astimezone(pytz.timezone('America/New_York')))
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
    def contact_email(self):
        return ResourceItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).contact_email


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
    def type(self):
        child = Resource.objects.get_subclass(id=self.id)
        return child.type

    @property
    def item (self):

        child = Resource.objects.get_subclass(id=self.id)
        return child._item
    
    def __str__(self):
        allocated_resource = Resource.objects.get_subclass(id=self.id)
        if allocated_resource:
            return str(allocated_resource)
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
    def get_performer_profiles(self):
        return ActItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).get_performer_profiles()

    @property
    def contact_email(self):
        return ActItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).contact_email

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
    
    @property
    def type(self):
        return "act"

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
    
    @property
    def contact_email(self):
        return ""

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

    @property
    def type(self):
        return "location"
    
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
    def contact_email(self):
        return WorkerItem.objects.get_subclass(resourceitem_id=self.resourceitem_id).contact_email

    
    @property
    def describe(self):
        child = WorkerItem.objects.get_subclass(resourceitem_id=self.resourceitem_id)
        
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)
        
    def __unicode__(self):
        return unicode(self.describe)

    '''
    should remain focused on the upward connection of resource allocations, and avoid being sub
    class specific
    '''    
    def get_bookings(self, role):
        from scheduler.models import Event
        events = Event.objects.filter(resources_allocated__resource__worker___item=self,
                                      resources_allocated__resource__worker__role=role)
        return events
    
    '''
    way of getting the schedule nuances of GBE-specific logic by calling the subclasses
    for their specific schedule
    '''
    def get_schedule(self):
        child = WorkerItem.objects.get_subclass(resourceitem_id=self.resourceitem_id)
        return child.get_schedule()

    '''
       Looks at all current bookings and returns all conflicts.
       Best to do *before* allocating as a resource.
       Returns = a list of conflicts.  And empty list means no conflicts.  Any conflict listed overlaps
          with the new_event that was provided.
    '''
    def get_conflicts(self, new_event):
        conflicts = []
        for event in self.get_schedule():
            if event.check_conflict(new_event):
               	conflicts += [event]
        return conflicts

    
class Worker (Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = models.ForeignKey(WorkerItem)
    role = models.CharField(max_length=50,
                                    choices=role_options, 
                                    blank=True)
    
    @property
    def type(self):
        return self.role

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
    def contact_email(self):
        return ""

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

    @property
    def type(self):
        return "equipment"


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
    max_volunteer = models.PositiveIntegerField(default=0)

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
                if isinstance(allocation.resource, Location):
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
        
        
    '''
    The difference between the max suggested # of volunteers and the actual number
     > 0 if there are too many volunteers for the max - the number will be the # of people over booked
        (if there are 3 spaces, and 4 volunteers, the value returned is 1)
     = 0 if it is at capacity
     < 0 if it is fewer than the max, the abosolute value is the amount of space remaining
        (if there are 4 spaces, and 3 volunteers, the value will be -1)
    '''
    def extra_volunteers(self):
        return  Worker.objects.filter(allocations__event=self, role='Volunteer').count() - self.max_volunteer



    '''
       Check this event vs. another event to see if the times conflict.
       Useful whenever we want to check on shared resources.
       - if they start at the same time, it doesn't matter how long they are
       - if this event start time is after the other event, but the other event ends *after* this
             event starts - it's a conflict
       - if this event starts first, but bleeds into the other event by overlapping end_time - it's a conflict
    '''
    def check_conflict(self, other_event):
        is_conflict = False
        if self.start_time == other_event.starttime:
            is_conflict = True
        elif self.start_time > other_event.start_time and self.start_time < other_event.end_time:
            is_conflict = True
        elif self.start_time < other_event.start_time and self.end_time > other_event.start_time:
            is_conflict = True
        return is_conflict

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
            

class Ordering(models.Model):
    '''
    A decorator for Allocations to allow representation of orderings
    Attaches to an Allocation. No effort is made to ensure uniqueness or 
    completeness of an ordering, this is handled later in the business 
    logic. 
    Orderings are assumed to sort from low to high. Negative ordering
    indices are allowed. 
    '''
    order = models.IntegerField(default=0)
    allocation = models.OneToOneField(ResourceAllocation)
