#
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
#

from ticketing.models import *
from django import forms
from gbe.models import Event
from gbe_forms_text import *


class TicketItemForm(forms.ModelForm):
    '''
    Used to create a form for editing ticket item.  Used by the TicketItemEdit
    view.
    '''

    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = TicketItem
        fields = ['ticket_id',
                  'title',
                  'description',
                  'active',
                  'cost'
                  ]
        labels = ticket_item_labels

    def save(self, user, commit=True):
        form = super(TicketItemForm, self).save(commit=False)
        form.modified_by = user

        exists = TicketItem.objects.filter(ticket_id=form.ticket_id)
        if (exists.count() > 0):
            form.id = exists[0].id

        if commit:
            form.save()
        return form


class BPTEventForm(forms.ModelForm):
    '''
    Used to create a form for editing the whole event.  Used by the
    TicketItemEdit view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    linked_events = forms.ModelMultipleChoiceField(
                                 queryset=Event.objects.all())

    class Meta:
        model = BrownPaperEvents
        fields = ['primary',
                  'act_submission_event',
                  'vendor_submission_event',
                  'linked_events',
                  'include_conference',
                  'include_most',
                  'badgeable',
                  'ticket_style'
                  ]
        labels = ticket_item_labels
