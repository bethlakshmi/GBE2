from django.contrib import admin

from scheduler.models import *
import datetime
from gbe_forms_text import *



admin.site.register(EventItem)
admin.site.register(LocationItem)
admin.site.register(WorkerItem)
admin.site.register(Event)
admin.site.register(Location)
admin.site.register(Worker)
admin.site.register(ResourceAllocation)
admin.site.register(Schedulable)
