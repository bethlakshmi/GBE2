from django.contrib import admin
from scheduler.models import *
import datetime
from gbe_forms_text import *
from import_export.admin import (
    ImportExportActionModelAdmin,
    ImportExportModelAdmin,
)
from import_export.resources import ModelResource


class ResourceAllocationAdmin(ImportExportActionModelAdmin):
    list_display = ('id',
                    'event',
                    'event_type',
                    'resource',
                    'resource_email',
                    'resource_type')
    list_filter = ['event__eventitem__event__conference',
                   'resource__worker__role',
                   'resource__location']

    def resource_email(self, obj):
        try:
            resource = Resource.objects.filter(allocations=obj)[0]
            return resource.item.contact_email
        except:
            return "no email"

    def resource_type(self, obj):
        try:
            resource = Resource.objects.filter(allocations=obj)[0]
            return resource.type
        except:
            return "no email"

    def event_type(self, obj):
        if str(obj.event.eventitem.child().__class__.__name__) == 'GenericEvent':
            return obj.event.eventitem.child().sched_payload['type']
        else:
            return str(obj.event.eventitem.child().__class__.__name__)


class EventItemAdmin(admin.ModelAdmin):
    list_display = (
        'eventitem_id', str, 'visible', 'event_type', 'conference')
    list_filter = ['visible', 'event__conference']
    search_fields = ['event__title']

    def event_type(self, obj):
        if str(obj.child().__class__.__name__) == 'GenericEvent':
            return obj.child().sched_payload['type']
        else:
            return str(obj.child().__class__.__name__)

    def conference(self, obj):
        return obj.child().conference


class EventAdmin(ImportExportModelAdmin):
    list_display = ('id', 'eventitem', 'starttime', 'max_volunteer')
    list_filter = ['starttime',
                   'max_volunteer',
                   'eventitem__event__conference', ]


class EventContainerAdmin(ImportExportModelAdmin):
    list_display = ('parent_event', 'child_event', 'child_conf')
    list_filter = ['parent_event__eventitem__event__conference']

    def child_conf(self, obj):
        return obj.child_event.eventitem.get_conference()


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('_item', 'role')
    list_filter = ['role', '_item']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'allocation')


admin.site.register(EventItem, EventItemAdmin)
admin.site.register(LocationItem)
admin.site.register(WorkerItem)
admin.site.register(ResourceItem)
admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Resource)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(ActItem)
admin.site.register(Ordering, OrderAdmin)
admin.site.register(ActResource)
admin.site.register(EventContainer, EventContainerAdmin)
