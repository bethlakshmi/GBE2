#
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
# edited by bb 7/27/2015
#

from ticketing.models import *
from django import forms
from gbe.models import Show, GenericEvent, Event
from gbe_forms_text import *
from django.db.models import Q



class TicketItemForm(forms.ModelForm):
    '''
    Used to create a form for editing ticket item.  Used by the TicketItemEdit
    view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    bpt_event = forms.ModelChoiceField(
                            queryset = BrownPaperEvents.objects.all(),
                            empty_label=None)


    class Meta:
        model = TicketItem
        fields = ['ticket_id',
                  'title',
                  'description',
                  'active',
                  'cost',
                  'bpt_event'
                  ]
        widgets = {'bpt_event': forms.HiddenInput()}
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
    shows = Show.objects.all()
    genericevents = GenericEvent.objects.exclude(type="Volunteer")
    event_set = Event.objects.filter(Q(show__in=shows) |
                                     Q(genericevent__in=genericevents))
    linked_events = forms.ModelMultipleChoiceField \
                               (queryset=event_set,
                                required=False,
                                label=bpt_event_labels['linked_events'])


    class Meta:
        model = BrownPaperEvents
        fields = ['primary',
                  'act_submission_event',
                  'vendor_submission_event',
                  'linked_events',
                  'include_conference',
                  'include_most',
                  'badgeable',
                  'ticket_style',
                  'conference'
                  ]
        labels = bpt_event_labels
        help_texts = bpt_event_help_text
