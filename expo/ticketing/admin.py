#
# models.py - Contains Django code for the built-in Admin webpage
# edited by mdb 6/6/2014
# edited by bb 7/26/2014
#


from django.contrib import admin
from ticketing.models import *


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ticket_item',
                    'purchaser',
                    'amount',
                    'order_date',
                    'import_date')
    list_filter = ['order_date',
                   'import_date']
    search_fields = ['ticket_item__title',
                     'purchaser__matched_to_user__username']


class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('matched_to_user',
                    'first_name',
                    'last_name',
                    'email',
                    'phone')
    list_filter = ['state',
                   'country']
    search_fields = ['matched_to_user__username',
                     'first_name',
                     'last_name',
                     'email']


class TicketItemAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'ticket_id',
                    'active',
                    'cost',
                    'datestamp',
                    'modified_by',
                    'conference')
    list_filter = ['active',
                   'datestamp',
                   'modified_by',
                   'bpt_event']
    search_fields = ['title']

    def conference(self, obj):
            return obj.bpt_event.conference


class BPTEventsAdmin(admin.ModelAdmin):
    list_display = ('bpt_event_id',
                    'primary',
                    'act_submission_event',
                    'vendor_submission_event',
                    'badgeable',
                    'ticket_style',
                    'include_conference',
                    'include_most',
                    'conference')
    list_filter = ['primary',
                   'act_submission_event',
                   'vendor_submission_event',
                   'badgeable',
                   'conference']

    
class TicketingExclusionInline(admin.TabularInline):
    model = TicketingExclusion
    filter_horizontal = ("tickets",)
 
 
class RoleExclusionInline(admin.TabularInline):
    model = RoleExclusion
    

class EligibilityConditionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',
                    'checklistitem')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]
    
class TicketEligibilityConditionAdmin(admin.ModelAdmin):
    filter_horizontal = ("tickets",)
    list_display = ('__unicode__',
                    'checklistitem')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]

admin.site.register(BrownPaperSettings)
admin.site.register(BrownPaperEvents, BPTEventsAdmin)
admin.site.register(TicketItem, TicketItemAdmin)
admin.site.register(Purchaser, PurchaserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TicketingEligibilityCondition,
                    TicketEligibilityConditionAdmin)
admin.site.register(RoleEligibilityCondition,
                    EligibilityConditionAdmin)
admin.site.register(CheckListItem)
