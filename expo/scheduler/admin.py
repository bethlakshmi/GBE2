from django.contrib import admin

from scheduler.models import *
import datetime
from gbe_forms_text import *

class MasterEventTabularInline(admin.TabularInline):
    '''
    Tool to create and enter data into a Master Event.
    '''

    model = MasterEvent
    
    fieldsets = [
        ('Master Event Name', {'fields': ['name']}),
        ('Start Time', {'fields': ['start_time']}),
        ('Stop Time', {'fields': ['stop_time']}),
        ('Blocking', {'fields': ['blocking']}),
        ('Event Types',{'fields': ['event_type']}),
        ]

class SchedEventTabularInline(admin.TabularInline):
    '''
    Tool to create and enter data into an Event.
    '''

    model = SchedEvent
    
    fieldsets = [
        ('Event Name', {'fields': ['name']}),
        ('Hard Time', {'fields': ['hard_time']}),
        ('Soft Time', {'fields': ['soft_time']}),
        ('Blocking', {'fields': ['blocking']}),
        ('Event Types', {'fields': ['event_type']}),
        ('Include Types', {'fields': ['item_type']})
        ]

class EventIncludes(admin.ModelAdmin):
    '''
    The fields that contain multiple entries within a Master Event.
    '''

    fieldsets = [
        ('Included Items', {'fields': ['item_list']}),
        ('Viewable', {'fields': ['viewable']}),
        ]

    inlines = [MasterEventTabularInline, SchedEventTabularInline]

class EventTypesInline(admin.TabularInline):
    '''
    Create a list of Event Types within Event objects that allow
    for selection from a predetermined list.
    '''

    model = EventTypes
    extra = 2

class EventTypeIncludes(admin.ModelAdmin):

    fieldsets = [
        ('Event Type', {'fields': ['event_types']}),
        ]
    inlines = [EventTypesInline]

class PropertyInlines(admin.TabularInline):
    '''
    Individual property handler.
    '''

    model = Property
    extra = 2

class PropertiesInclude(admin.ModelAdmin):
    '''
    Properties of a data object, to control object interactions.
    '''

    #model = Properties

    fieldsets = [
        ('Property Text', {'fields': ['property_name'], 'classes': ['collapse']}),
        ('Property Value', {'fields': ['property_info'], 'classes': ['collapse']}),
        ]
    inlines = [PropertyInlines]

class LocationsTabularInline(admin.TabularInline):
	  '''
	  Form to build a location, add properties to it, etc.
	  '''

	  model = Locations

	  fieldsets = [
	      ('Location Name', {'fields': ['name', 'description', 'room_type']}),
	      ]

admin.site.register(MasterEvent)
admin.site.register(SchedEvent)
#admin.site.register(Items)
admin.site.register(Locations)
admin.site.register(Properties)
admin.site.register(EventTypes)