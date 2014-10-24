from django.contrib import admin
from gbe.models import *

class BidAdmin(admin.ModelAdmin):
    list_display = (str, 'submitted', 'accepted')
    list_filter = ['submitted', 'accepted']
    
admin.site.register( Profile )
admin.site.register( Biddable )
admin.site.register( Act, BidAdmin )
admin.site.register( Class, BidAdmin )
admin.site.register( Vendor, BidAdmin )
admin.site.register( Volunteer, BidAdmin )
admin.site.register( Show )
admin.site.register( Room )
admin.site.register( ClassProposal )
admin.site.register( BidEvaluation )
admin.site.register( Performer )
admin.site.register( TechInfo )
admin.site.register( AudioInfo )
admin.site.register( LightingInfo )
admin.site.register( StageInfo )
admin.site.register( PerformerFestivals )
admin.site.register( ProfilePreferences )
admin.site.register( Persona )
admin.site.register( Combo )
admin.site.register( Troupe )
admin.site.register( ConferenceVolunteer )
admin.site.register( GenericEvent )
admin.site.register( Event )
