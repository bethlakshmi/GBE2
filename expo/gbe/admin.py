from django.contrib import admin
from gbe.models import *
from model_utils.managers import InheritanceManager
from import_export.admin import ImportExportActionModelAdmin


class BidAdmin(admin.ModelAdmin):
    list_display = (str, 'submitted', 'accepted', 'created_at', 'updated_at')
    list_filter = ['submitted', 'accepted', 'conference']


class ClassAdmin(BidAdmin):
    list_display = ('__unicode__',
                    'teacher',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted', 'conference']


class ActAdmin(admin.ModelAdmin):
    list_display = ('performer',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted', 'conference']


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')


class TroupeAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    filter_horizontal = ("membership",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')
    search_fields = ['display_name',
                     'user_object__email']


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


class ShowAdmin(admin.ModelAdmin):
    list_filter = ['conference']


class GenericAdmin(ImportExportActionModelAdmin):
    list_display = ('title', 'type')
    list_filter = ['conference', 'type']


class EventAdmin(admin.ModelAdmin):
    list_display = ('eventitem_id', 'title', 'subclass')
    list_filter = ['conference']

    def subclass(self, obj):
        try:
            event = Event.objects.get_subclass(event_id=obj.event_id)
            return str(event.__class__.__name__)
        except:
            return "Event"


class MessageAdmin(admin.ModelAdmin):
    list_display = ('view',
                    'code',
                    'summary',
                    'description')
    list_editable = ('summary', 'description')
    readonly_fields = ('view', 'code')


class AvailableInterestAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'interest',
                    'visible',
                    'help_text')
    list_editable = ('interest',
                     'visible',
                     'help_text')


class VolunteerInterestAdmin(admin.ModelAdmin):
    list_display = ('interest',
                    'volunteer',
                    'rank',
                    'conference')
    list_filter = ['interest',
                   'rank',
                   'volunteer__conference']

    def conference(self, obj):
        return obj.volunteer.conference


class VolunteerWindowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'day_w_year',
                    'start',
                    'end',
                    'conference')
    list_filter = ['day',
                   'day__conference']
    list_editable = ('start',
                     'end',)

    def conference(self, obj):
        return obj.day.conference

    def day_w_year(self, obj):
        return obj.day.day


class ConferenceDayAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'day',
                    'conference')
    list_filter = ['conference']
    list_editable = ('day',
                     'conference',)


admin.site.register(Conference)
admin.site.register(ConferenceDay, ConferenceDayAdmin)
admin.site.register(VolunteerWindow, VolunteerWindowAdmin)
admin.site.register(VolunteerInterest, VolunteerInterestAdmin)
admin.site.register(AvailableInterest, AvailableInterestAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Biddable, BidAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Vendor, BidAdmin)
admin.site.register(Volunteer, BidAdmin)
admin.site.register(Costume, BidAdmin)
admin.site.register(Show, ShowAdmin)
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
admin.site.register(Troupe, TroupeAdmin)
admin.site.register(ConferenceVolunteer, ConferenceVolunteerAdmin)
admin.site.register(GenericEvent, GenericAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(UserMessage, MessageAdmin)
admin.site.register(ShowVote)
admin.site.register(ActBidEvaluation)
