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

class EventIncludes(admin.ModelAdmin):
    '''
    The fields that contain multiple entries within a Master Event.
    '''

    fieldsets = [
        ('Viewable', {'fields': ['viewable']}),
        ]

    inlines = [MasterEventTabularInline]

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
        ('Description', {'fields': ['description']}),
        ]
    inlines = [EventTypesInline]

class PropertiesInclude(admin.ModelAdmin):
    '''
    Properties of a data object, to control object interactions.
    '''

    model = Properties

    fieldsets = [
        ('Property Text', {'fields': ['property_name'], 'classes': ['collapse']}),
        ('Property Value', {'fields': ['property_info'], 'classes': ['collapse']}),
        ]

class LocationsTabularInline(admin.TabularInline):
	  '''
	  Form to build a location, add properties to it, etc.
	  '''

	  model = Locations

	  fieldsets = [
	      ('Location Name', {'fields': ['name', 'description', 'room_type']}),
	      ]

class LocationsInclude(admin.ModelAdmin):
    '''
    Build a list of locations to schedule events into.
    '''

    inlines = [LocationsTabularInline]

    fieldsets = [
        ('Location Name', {'fields': ['name']}),
        ('Description', {'fields': ['description'], 'classes': ['collapse']}),
        ('Room type', {'fields': ['room_type'], 'classes': ['collapse']}),
        ('Room Properties', {'fields': ['room_properties'], 'classes': ['collapse']}),
        ]

class RoomTypesTabularInline(admin.TabularInline):
    '''
    In Line Admin for Room Types
    '''

    model = RoomTypes
    fieldsets = [
        ('Room Type', {'fields': ['type']}),
        ]

class RoomTypesInclude(admin.ModelAdmin):
    '''
    Type of Room that can have scheduled events within them
    '''

    fieldsets = [
        ('Room Type', {'fields': ['types']}),
        ('Description', {'fields': ['description']}),
        ]
    inlines = [RoomTypesTabularInline]


admin.site.register(MasterEvent)
admin.site.register(Locations)
admin.site.register(Properties)
admin.site.register(EventTypes)
admin.site.register(RoomTypes)
