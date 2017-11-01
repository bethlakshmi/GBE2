from django.forms import (
    ChoiceField,
    ModelChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import (
    Event,
    ConferenceDay,
    Show,
    Class,
    GenericEvent,
)
from expo.settings import DATE_FORMAT
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
)


class TargetDay(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.conference.conference_slug, obj.day.strftime(DATE_FORMAT))


class TargetEvent(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.e_conference.conference_slug, obj.e_title)


class CopyEventPickDayForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    copy_to_day = TargetDay(
        queryset=ConferenceDay.objects.exclude(
            conference__status="completed").order_by('day'),
        required=False
        )

class CopyEventPickModeForm(CopyEventPickDayForm):
    '''
    Form for selecting the type of event to create
    '''
    copy_mode = ChoiceField(choices=copy_mode_choices,
                            label=copy_mode_labels['copy_mode'],
                            widget=RadioSelect)
    
    target_event = TargetEvent(queryset=Event.objects.none(),
                               required=False)

    def __init__(self, *args, **kwargs):
        event_type = None
        if 'event_type' in kwargs:
            event_type = kwargs.pop('event_type')
        super(CopyEventPickModeForm, self).__init__(*args, **kwargs)
        if event_type == "Show":
            self.fields['target_event'].queryset = Show.objects.exclude(
                e_conference__status="completed")
        elif event_type == "Class":
            self.fields['target_event'].queryset = Class.objects.exclude(
                e_conference__status="completed")
        elif event_type:
            self.fields[
                'target_event'].queryset = GenericEvent.objects.exclude(
                e_conference__status="completed").filter(type=event_type)
        else:
            self.fields['target_event'].queryset = Event.objects.exclude(
                e_conference__status="completed")

    def clean(self):
        cleaned_data = super(CopyEventPickModeForm, self).clean()
        copy_mode = cleaned_data.get("copy_mode")
        target_event = cleaned_data.get("target_event")
        copy_to_day = cleaned_data.get("copy_to_day")
        if copy_mode:
            if copy_mode == copy_mode_choices[0][0] and not target_event:
                msg = " Must choose the target event when copying sub-events."
                self.add_error('target_event', msg)
            if copy_mode == copy_mode_choices[1][0] and not copy_to_day:
                msg = " Must choose a day when copying all events."
                self.add_error('copy_to_day', msg)
