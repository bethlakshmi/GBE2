from django.contrib import admin
from gbe.models import *

class BidAdmin(admin.ModelAdmin):
    list_display = (str, 'submitted', 'accepted', 'created_at', 'updated_at')
    list_filter = ['submitted', 'accepted']
    
class ActAdmin(admin.ModelAdmin):
    list_display = ('title', 'performer', 'submitted', 'accepted', 'created_at', 'updated_at')
    list_filter = ['submitted', 'accepted']

class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')
    
admin.site.register( Profile, ProfileAdmin )
admin.site.register( Biddable )
admin.site.register( Act, ActAdmin )
admin.site.register( Class, BidAdmin )
admin.site.register( Vendor, BidAdmin )
admin.site.register( Volunteer, BidAdmin )
admin.site.register( Show )
admin.site.register( Room )
admin.site.register( ClassProposal )
admin.site.register( BidEvaluation )
admin.site.register( TechInfo )
admin.site.register( AudioInfo )
admin.site.register( LightingInfo )
admin.site.register( StageInfo )
admin.site.register( PerformerFestivals )
admin.site.register( ProfilePreferences )
admin.site.register( Persona, PerformerAdmin )
admin.site.register( Performer, PerformerAdmin )
admin.site.register( Combo, PerformerAdmin )
admin.site.register( Troupe, PerformerAdmin )
admin.site.register( ConferenceVolunteer )
admin.site.register( GenericEvent )
admin.site.register( Event )
