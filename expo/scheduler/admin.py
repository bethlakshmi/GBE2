from django.contrib import admin
from scheduler.models import *
import datetime
from gbe_forms_text import *


class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('event', 'resource', 'resource_email', 'resource_type')
    list_filter = ['event', 'resource']

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


class EventItemAdmin(admin.ModelAdmin):
    list_display = (str, 'visible')
    list_filter = ['visible']


class EventAdmin(admin.ModelAdmin):
    list_display = ('eventitem', 'starttime', 'max_volunteer')
    list_filter = ['eventitem', 'starttime', 'max_volunteer']


class EventContainerAdmin(admin.ModelAdmin):
    list_display = ('parent_event', 'child_event', 'parent_conf')
    
    def parent_conf(self, obj):
        return obj.parent_event.eventitem.get_conference()


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
