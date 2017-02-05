from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from model_utils.managers import InheritanceManager
from gbetext import *
from gbe.expomodelfields import DurationField
from expo.settings import (
    DATETIME_FORMAT,
    DAY_FORMAT,)
from django.utils.formats import date_format
from django.core.exceptions import MultipleObjectsReturned
import pytz


class Schedulable(models.Model):
    '''
    Interface for an item that can appear on a conference schedule - either an
    event or a resource allocation. (resource allocations can include, eg,
    volunteer commitments for a particular person, or for a particular event,
    or for a block of time - so this is a pretty flexible idea)
    Note that conference models should NEVER inherit this directly or
    indirectly.
    This is why we use the indirection model: we don't want to store scheduler
    data in the conference model.
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
            return "Start: " + str(
                self.start_time.astimezone(pytz.timezone('UTC')))
        else:
            return "No Start Time"

    def __str__(self):
        if self.start_time:
            return "Start: " + str(
                self.starttime.astimezone(pytz.timezone('UTC')))
        else:
            return "No Start Time"

    class Meta:
        verbose_name_plural = 'Schedulable Items'


class ResourceItem(models.Model):
    '''
    The payload for a resource
    '''
    objects = InheritanceManager()
    resourceitem_id = models.AutoField(primary_key=True)

    @property
    def contact_email(self):
        return ResourceItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).contact_email

    @property
    def as_subtype(self):
        return ResourceItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)

    @property
    def payload(self):
        return self._payload

    @property
    def _name(self):
        return self.sched_name

    @property
    def describe(self):
        child = ResourceItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)
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
    def item(self):
        child = Resource.objects.get_subclass(id=self.id)
        return child._item

    @property
    def as_subtype(self):
        child = Resource.objects.get_subclass(id=self.id)
        return child

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

    def set_rehearsal(self, show, rehearsal):
        '''
        Assign this act to a rehearsal slot for this show
        '''
        resources = ActResource.objects.filter(_item=self)
        allocs = sum([list(res.allocations.all()) for res in resources], [])

        for a in allocs:
            is_rehearsal_for_this_show = (
                a.event.as_subtype.type == 'Rehearsal Slot' and
                a.event.container_event.parent_event == show)

            if is_rehearsal_for_this_show:
                a.delete()
                a.resource.delete()
        resource = ActResource(_item=self)
        resource.save()
        ra = ResourceAllocation(event=rehearsal, resource=resource)
        ra.save()

    @property
    def as_subtype(self):
        return self.act

    def get_resource(self):
        '''
        Deprecate this.
        Return the resource corresonding to this item
        To do: find a way to make this work at the Resource level
        '''
        return self.as_subtype

    @property
    def order(self):
        '''
        This is a little bit broken: assumes that an act is only
        scheduled for one show.
        This assumption pervades the current code, and will
        need to be removed for post 2015 use
        '''
        try:
            resource = ActResource.objects.filter(_item=self).first()
            return resource.order
        except:
            return -1

    def get_scheduled_shows(self):
        '''
        Returns a list of all shows this act is scheduled to appear in.
        '''
        resources = ActResource.objects.filter(_item=self)

        return filter(lambda i: i is not None,
                      [res.show for res in resources])

    def get_scheduled_rehearsals(self):
        '''
        Returns a list of all shows this act is scheduled to appear in.
        '''
        resources = ActResource.objects.filter(_item=self)

        return filter(lambda i: i is not None,
                      [res.rehearsal for res in resources])

    @property
    def get_performer_profiles(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_performer_profiles()

    @property
    def contact_email(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).contact_email

    @property
    def bio(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).bio

    @property
    def visible(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).visible

    @property
    def describe(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).title

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
    def show(self):
        ra = ResourceAllocation.objects.filter(resource=self).first()
        if ra and ra.event.event_type_name == 'Show':
            return ra.event
        else:
            return None

    @property
    def order(self):
        try:
            ra = ResourceAllocation.objects.filter(resource=self).first()
        except:
            return None
        if ra and ra.ordering:
            return ra.ordering.order
        else:
            return -1

    @property
    def rehearsal(self):
        ra = ResourceAllocation.objects.filter(resource=self).first()
        if ra and ra.event.event_type_name == 'GenericEvent':
            return ra.event
        else:
            return None

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

    @property
    def as_subtype(self):
        return self.room

    def get_resource(self):
        '''
        Return the resource corresonding to this item
        To do: find a way to make this work at the Resource level
        '''
        try:
            loc = Location.objects.select_subclasses().get(_item=self)
        except:
            loc = Location(_item=self)
            loc.save()
        return loc

    @property
    def get_bookings(self):
        '''
        Returns the events for which this LocationItem is booked.
        should remain focused on the upward connection of resource
        allocations, and avoid being subclass specific
        '''
        from scheduler.models import Event

        events = Event.objects.filter(
            resources_allocated__resource__location___item=self
        ).order_by(
            'starttime')
        return events

    @property
    def describe(self):
        return LocationItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).name

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
    def as_subtype(self):
        '''
        Returns this item as its underlying conference type.
        (either Performer or Profile)
        '''
        from django.core.exceptions import ObjectDoesNotExist
        try:
            p = self.performer
        except ObjectDoesNotExist:
            p = self.profile
        return p

    @property
    def contact_email(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).contact_email

    @property
    def badge_name(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).describe

    @property
    def contact_phone(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).contact_phone

    @property
    def describe(self):
        child = WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)
        return child.__class__.__name__ + ":  " + child.describe.encode('utf-8').strip()

    def __str__(self):
        return str(self.describe)

    def __unicode__(self):
        return unicode(self.describe)

    def get_bookings(self, role='All', conference=None):
        '''
        Returns the events for which this Worker is booked as "role".
        should remain focused on the upward connection of resource
        allocations, and avoid being sub class specific
        '''
        from scheduler.models import Event

        if role in ['All', None]:
            events = Event.objects.filter(
                resources_allocated__resource__worker___item=self)
        else:
            events = Event.objects.filter(
                resources_allocated__resource__worker___item=self,
                resources_allocated__resource__worker__role=role)
        if conference:

            events = events.filter(eventitem__event__conference=conference)
        return events

    def get_schedule(self):
        '''
        way of getting the schedule nuances of GBE-specific logic
        by calling the subclasses for their specific schedule
        '''
        child = WorkerItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)
        return child.get_schedule()

    def get_conflicts(self, new_event):
        '''
        Looks at all current bookings and returns all conflicts.
        Best to do *before* allocating as a resource.
        Returns = a list of conflicts.  And empty list means no conflicts.
        Any conflict listed overlaps with the new_event that was provided.
        '''
        conflicts = []
        for event in self.get_schedule():
            if event.check_conflict(new_event):
                conflicts += [event]
        return conflicts


class Worker(Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = models.ForeignKey(WorkerItem)
    role = models.CharField(max_length=50,
                            choices=role_options,
                            blank=True)

    @property
    def workeritem(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self._item.resourceitem_id)

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


class EventItem (models.Model):
    '''
    The payload for an event (ie, a class, act, show, or generic event)
    The EventItem must not impose any DB usage on its implementing model
    classes.
    '''
    objects = InheritanceManager()
    eventitem_id = models.AutoField(primary_key=True)
    visible = models.BooleanField(default=True)

    def child(self):
        return EventItem.objects.get_subclass(eventitem_id=self.eventitem_id)

    def get_conference(self):
        return self.child().conference

    def day_options(self):
        return self.get_conference().conferenceday_set.all()

    def volunteer_options(self):
        return VolunteerWindow.objects.filter(day__in=self.day_options())

    @property
    def bios(self):
        people = WorkerItem.objects.filter(
            worker__allocations__event__eventitem=self.eventitem_id,
            worker__role__in=['Teacher',
                              'Panelist',
                              'Moderator']).distinct().select_subclasses(
                                  'performer')
        if people.count() == 0:
            people = self.bio_payload
        return people

    def roles(self, roles=['Teacher',
                           'Panelist',
                           'Moderator',
                           'Staff Lead']):
        try:
            container = EventContainer.objects.filter(
                child_event__eventitem=self).first()
            people = Worker.objects.filter(
                (Q(allocations__event__eventitem=self) &
                 Q(role__in=roles)) |
                (Q(allocations__event=container.parent_event) &
                 Q(role__in=roles))).distinct().order_by(
                'role', '_item')
        except:
            people = Worker.objects.filter(
                allocations__event__eventitem=self,
                role__in=roles
            ).distinct().order_by('role', '_item')
        return people

    def set_duration(self, duration):
        child = self.child()
        child.duration = duration
        child.save(update_fields=('duration',))

    def remove(self):
        Event.objects.filter(eventitem=self).delete()
        self.visible = False
        self.save()

    @property
    def payload(self):
        return self.child().sched_payload

    @property
    def duration(self):
        child = self.child()
        return child.sched_duration

    @property
    def describe(self):
        try:
            child = self.child()
            return str(child)
        except:
            return "no child"

    def __str__(self):
        return str(self.describe)

    def __unicode__(self):
        return unicode(self.describe)


class Event(Schedulable):
    '''
    An Event is a schedulable item with a conference model item as its payload.
    '''
    objects = InheritanceManager()
    eventitem = models.ForeignKey(EventItem, related_name="scheduler_events")
    starttime = models.DateTimeField(blank=True)
    max_volunteer = models.PositiveIntegerField(default=0)

    def get_open_rehearsals(self):
        rehearsals = [
            ec.child_event
            for ec in EventContainer.objects.filter(parent_event=self)
            if (ec.child_event.confitem.type == 'Rehearsal Slot' and
                ec.child_event.has_act_opening())
        ]
        return sorted(rehearsals,
                      key=lambda sched_event: sched_event.starttime)

    def has_act_opening(self):
        '''
        returns True if the count of acts allocated to this event is less than
        max_volunteer
        '''
        allocs = ResourceAllocation.objects.filter(event=self)
        from gbe.models import Act  # late import, circularity
        acts_booked = len([a for a in allocs
                           if isinstance(a.resource.item.as_subtype, Act)])
        return self.max_volunteer - acts_booked > 0

    @property
    def detail_link(self):
        '''
        Return a detail link to self, with title as link text
        '''
        return '<a href="%s">%s</a>' % (reverse('detail_view',
                                                urlconf='scheduler.urls',
                                                args=[self.eventitem_id]),
                                        self.eventitem.describe)

    @property
    def confitem(self):
        '''
        Returns the conference item corresponding to this event
        '''
        import gbe.models as conf
        try:
            return conf.Event.objects.get_subclass(
                event_id=self.eventitem.event.event_id)
        except:
            return None   # need to do some defensive programming here

    def set_location(self, location):
        '''
        location is a LocationItem or a Location resource
        '''
        if isinstance(location, LocationItem):
            location = location.get_resource()
        if self.location == location.item:
            pass   # already set
        elif self.location is None:
            ra = ResourceAllocation(resource=location, event=self)
            ra.save()
        else:
            locations = LocationItem.objects.all()
            allocations = ResourceAllocation.objects.filter(event=self)
            for allocation in allocations:
                if allocation.resource.item in locations:
                    allocation.resource = location
                    allocation.save()

    def allocate_worker(self, worker, role, label=None, alloc_id=-1):
        '''
        worker can be an instance of WorkerItem or of Worker
        role is a string, must be one of the role types.
        Since a particular Worker can be allocated in multiple roles, or
        multiple times in the same role, this will not attempt to reject
        duplicate allocations, it will always just create the requested
        allocation

        It returns any warnings.  Warnings include:
           - conflicts found with the worker item's existing schedule
           - any case where the event is already booked with the maximum
             number of volunteers
        '''
        warnings = []
        time_format = DATETIME_FORMAT
        if isinstance(worker, WorkerItem):
            worker = Worker(_item=worker, role=role)
        else:
            worker.role = role
        worker.save()
        for conflict in worker.workeritem.get_conflicts(self):
            warnings += [
                ("Found event conflict, new booking %s - " +
                 "%s conflicts with %s - %s") % (
                    str(self),
                    self.starttime.strftime(time_format),
                    str(conflict),
                    conflict.starttime.strftime(time_format))]
        if alloc_id < 0:
            allocation = ResourceAllocation(event=self,
                                            resource=worker)
        else:
            allocation = ResourceAllocation.objects.get(
                id=alloc_id)
            allocation.resource = worker
        allocation.save()
        if self.extra_volunteers() > 0:
            warnings += ["%s - %s is overfull. Over by %d volunteer." % (
                str(self),
                self.starttime.strftime(time_format),
                self.extra_volunteers())]
        if label:
            allocation.set_label(label)
        return warnings

    def unallocate_worker(self, worker, role):
        ResourceAllocation.objects.get(
            event=self,
            resource__worker___item=worker,
            resource__worker__role=role).delete()

    def unallocate_role(self, role):
        '''
        Remove all Worker allocations with this role
        '''
        allocations = ResourceAllocation.objects.filter(event=self)
        for allocation in allocations:
            if type(allocation.resource.item) == WorkerItem:
                if Worker.objects.get(
                        id=allocation.resource.id).role == role:
                    allocation.delete()

    def get_volunteer_opps(self, role='Volunteer'):
        '''
        return volunteer opportunities associated with this event
        Returns a list of dicts,
        {'sched':scheduler.Event, 'conf':conference_event}
        '''
        opps = EventContainer.objects.filter(parent_event=self)
        opps = [
            {'sched': opp.child_event,
             'conf': EventItem.objects.get_subclass(
                 eventitem_id=opp.child_event.eventitem_id),
             'contacts': Worker.objects.filter(
                 allocations__event=opp.child_event, role=role)
             }
            for opp in opps]
        return filter(lambda o: o['conf'].type == 'Volunteer', opps)

    def contact_info(self, resource_type='All', worker_type=None, status=None):
        '''
        Returns a list of email addresses for the requested resource type.
        Currently, return as csv: display_name, email_address
        Future: nice interface
        '''
        if resource_type == 'Teachers':
            return self.class_contacts()
        elif resource_type == 'Worker':
            return self.worker_contact_info(worker_type=worker_type)
        elif resource_type == 'Act':
            return self.act_contact_info(status=status)
        else:
            return (self.worker_contact_info(worker_type=worker_type) +
                    self.act_contact_info(status=status))

    @property
    def volunteer_count(self):
        allocations = ResourceAllocation.objects.filter(event=self)
        volunteers = allocations.filter(resource__worker__role='Volunteer').count()
        if volunteers > 0:
            return "%d volunteers" % volunteers
        else:
            acts = ActResource.objects.filter(allocations__in=allocations).count()
            if acts > 0:
                return "%d acts" % acts
        return 0

    def get_workers(self, worker_type=None):
        '''
        Return a list of workers allocated to this event,
        filtered by type if worker_type is specified
        returns the Worker Resource assigned. Calling function has to
        drill down to get to profile
        '''
        worker_type = worker_type or 'Volunteer'
        opps = self.get_volunteer_opps()
        alloc_list = [(opp['conf'].volunteer_type,
                       list(opp['sched'].resources_allocated.all()))
                      for opp in opps]

        workers = []
        for a in alloc_list:
            for w in a[1]:
                if w.resource.type == worker_type:
                    workers.append((a[0].interest,
                                    Worker.objects.get(
                                        resource_ptr_id=w.resource_id)))
        return workers

    def get_acts(self, status=None):
        '''
        Returns a list of acts allocated to this event,
        filtered by acceptance status if specified
        '''
        allocations = ResourceAllocation.objects.filter(event=self)
        act_resources = [ar.resource_ptr for ar in ActResource.objects.all()]
        acts = [allocation.resource.item.act for allocation in allocations
                if allocation.resource in act_resources]
        if status:
            acts = [act for act in acts if act.accepted == status]
        return acts

    def get_direct_workers(self, worker_role=None):
        '''
        Returns workers allocated directly to an Event -
        Teachers, panelists, moderators, etc
        Assumes these workers are tied to Performers, not Profiles.
        This is true for Teachers, Moderators, Panelists.
        '''
        allocations = ResourceAllocation.objects.filter(event=self)
        if worker_role:
            filter_f = lambda w: w.role == worker_role
        else:
            filter_f = lambda w: True
        workers = [wr.resource_ptr for wr in Worker.objects.all()
                   if filter_f(wr)]

        allocations = [allocation for allocation in allocations
                       if allocation.resource in workers]

        workers = [allocation.resource.item.performer
                   for allocation in allocations]
        return workers

    def class_contacts(self):
        '''
        Returns contact info for teachers, panelists, and moderators
        associated with this event (if any)
        '''
        info = []
        for worker in self.get_direct_workers():
            profile = worker.contact
            info.append(
                (worker.contact_email,
                 str(self),
                 worker.name,
                 profile.display_name)
            )
        return info

    def class_contacts2(self):
        '''
        To do: reconcile the two class_contacts functions
        '''
        allocations = self.resources_allocated.filter(
            resource__in=Worker.objects.all())
        info = []
        for allocation in allocations:
            try:
                persona = WorkerItem.objects.get_subclass(
                    resourceitem_id=allocation.resource.item.resourceitem_id)
                info.append(
                    (persona.contact_email,
                     str(self),
                     allocation.resource.worker.role,
                     persona.name,
                     persona.contact.display_name,
                     persona.contact_phone)
                )
            except:
                profile = WorkerItem.objects.get_subclass(
                    resourceitem_id=allocation.resource.item.resourceitem_id)

                info.append(
                    (profile.user_object.email,
                     str(self),
                     allocation.resource.worker.role,
                     "No Performer Name",
                     profile.display_name,
                     profile.phone)
                )
        return info

    def act_contact_info(self, status=None):
        info = []
        for act in self.get_acts(status):
            info.append(act.contact_info)
        return info

    def worker_contact_info(self, worker_type=None):
        '''
        Returns contact information and information for filtering
        Suitable for passing into csv
        '''
        info = []
        for (category, worker) in self.get_workers(worker_type):
            profile = worker.item.profile
            info.append(
                (profile.display_name,
                 profile.contact_email,
                 profile.phone,
                 worker.role,
                 category)
            )
        return info

    def set_duration(self, duration):
        '''
        duration should be a gbe.Duration or a timedelta
        '''
        self.eventitem.set_duration(duration)

    @property
    def event_type_name(self):
        '''
        Get event type name. Uses a database call
        '''
        return self.event_type.__name__

    @property
    def event_type(self):
        '''
        Get event's underlying type (ie, conference model)
        '''
        return type(self.as_subtype)

    @property
    def as_subtype(self):
        '''
        Get the representation of this Event as its underlying conference type
        '''
        return EventItem.objects.get_subclass(eventitem_id=self.eventitem_id)

    @property
    def duration(self):
        return self.eventitem.duration

    # for a long list of bios, right now, that is acts in shows.
    @property
    def bio_list(self):
        acts = ActResource.objects.filter(allocations__event=self,
                                          _item__act__accepted=3)
        bio_list = list(set([act._item.bio for act in acts]))
        bio_list = sorted(bio_list, key=lambda bio: bio.name)

        return bio_list

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

    def extra_volunteers(self):
        '''
        The difference between the max suggested # of volunteers
        and the actual number
        > 0 if there are too many volunteers for the max. The number
        will be the # of people over booked
        (if there are 3 spaces, and 4 volunteers, the value returned is 1)
        = 0 if it is at capacity
        < 0 if it is fewer than the max, the abosolute value is the
        amount of space remaining (if there are 4 spaces, and 3 volunteers,
        the value will be -1)
        '''
        count = Worker.objects.filter(allocations__event=self,
                                      role='Volunteer').count()
        return count - self.max_volunteer

    def check_conflict(self, other_event):
        '''
        Check this event vs. another event to see if the times conflict.
        Useful whenever we want to check on shared resources.
        - if they start at the same time, it doesn't matter how long they are
        - if this event start time is after the other event, but the other
        event ends *after* this event starts - it's a conflict
        - if this event starts first, but bleeds into the other event by
        overlapping end_time - it's a conflict
        '''
        is_conflict = False
        if self.start_time == other_event.start_time:
            is_conflict = True
        elif (self.start_time > other_event.start_time and
              self.start_time < other_event.end_time):
            is_conflict = True
        elif (self.start_time < other_event.start_time and
              self.end_time > other_event.start_time):
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

    def get_label(self):
        try:
            return self.label
        except Label.DoesNotExist:
            l = Label(allocation=self, text="")
            l.save()
            return l

    def set_label(self, text):
        l = self.get_label()
        l.text = text
        l.save()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        try:
            return "%s :: Event: %s == %s : %s" % (
                unicode(self.start_time.astimezone(pytz.timezone('UTC'))),
                unicode(self.event),
                unicode(Resource.objects.get_subclass(
                    id=self.resource.id).__class__.__name__),
                unicode(Resource.objects.get_subclass(id=self.resource.id)))
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


class Label (models.Model):
    '''
    A decorator allowing free-entry "tags" on allocations
    '''
    text = models.TextField(default='')
    allocation = models.OneToOneField(ResourceAllocation)

    def __str__(self):
        return self.text


class EventContainer (models.Model):
    '''
    Another decorator. Links one Event to another. Used to link
    a volunteer shift (Generic Event) to a Show (or other conf event)
    '''
    parent_event = models.ForeignKey(Event, related_name='contained_events')
    child_event = models.OneToOneField(Event, related_name='container_event')
