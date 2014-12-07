from django.contrib import admin

from scheduler.models import *
import datetime
from gbe_forms_text import *

class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('event', 'resource')
    list_filter = ['event', 'resource']

class EventAdmin(admin.ModelAdmin):
    list_display = ('eventitem','starttime','max_volunteer')
    list_filter = ['eventitem','starttime','max_volunteer']

admin.site.register(EventItem)
admin.site.register(LocationItem)
admin.site.register(WorkerItem)
admin.site.register(ResourceItem)
admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Worker)
admin.site.register(Resource)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(ActItem)
admin.site.register(ActResource)

