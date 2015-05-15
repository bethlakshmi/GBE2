from django.contrib import admin
from gbe.models import *
from model_utils.managers import InheritanceManager


class BidAdmin(admin.ModelAdmin):
    list_display = (str, 'submitted', 'accepted', 'created_at', 'updated_at')
    list_filter = ['submitted', 'accepted']


class ClassAdmin(BidAdmin):
    list_display = (str,
                    'teacher',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted']


class ActAdmin(admin.ModelAdmin):
    list_display = ('performer',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted']


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')


class AudioInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo',
                    'track_title',
                    'track_artist',
                    'track_duration',
                    'need_mic',
                    'confirm_no_music')


class LightingInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo', 'notes', 'costume')


class CueInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo', 'cue_sequence')


class BidEvalAdmin(admin.ModelAdmin):
    list_display = ('bid', 'evaluator', 'vote', 'notes')


class ClassProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'email', 'type', 'display')


class ConferenceVolunteerAdmin(admin.ModelAdmin):
    list_display = ('presenter',
                    'bid',
                    'how_volunteer',
                    'qualification',
                    'volunteering')
    list_filter = ['presenter', 'bid', 'how_volunteer']


class ProfilePreferencesAdmin(admin.ModelAdmin):
    list_display = ('profile',
                    'in_hotel',
                    'inform_about',
                    'show_hotel_infobox')
    list_filter = ['in_hotel', 'inform_about']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'overbook_size')


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'subclass')

    def subclass(self, obj):
        try:
            event = Event.objects.get_subclass(event_id=obj.event_id)
            return str(event.__class__.__name__)
        except:
            return "Event"


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Biddable, BidAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Vendor, BidAdmin)
admin.site.register(Volunteer, BidAdmin)
admin.site.register(Show)
admin.site.register(Room, RoomAdmin)
admin.site.register(ClassProposal, ClassProposalAdmin)
admin.site.register(BidEvaluation, BidEvalAdmin)
admin.site.register(TechInfo)
admin.site.register(AudioInfo, AudioInfoAdmin)
admin.site.register(LightingInfo, LightingInfoAdmin)
admin.site.register(CueInfo, CueInfoAdmin)
admin.site.register(StageInfo)
admin.site.register(PerformerFestivals)
admin.site.register(ProfilePreferences, ProfilePreferencesAdmin)
admin.site.register(Persona, PerformerAdmin)
admin.site.register(Performer, PerformerAdmin)
admin.site.register(Combo, PerformerAdmin)
admin.site.register(Troupe, PerformerAdmin)
admin.site.register(ConferenceVolunteer, ConferenceVolunteerAdmin)
admin.site.register(GenericEvent)
admin.site.register(Event, EventAdmin)
