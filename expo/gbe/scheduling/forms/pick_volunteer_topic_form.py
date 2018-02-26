from django.forms import (
    ChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import (
    GenericEvent,
    Show,
    StaffArea,
)
from scheduler.idd import get_occurrences
from expo.settings import DATETIME_FORMAT


class PickVolunteerTopicForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    volunteer_topic = ChoiceField(
        choices=[],
        widget=RadioSelect,
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(PickVolunteerTopicForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            complete_choices = []
            show_choices = []
            special_choices = []
            staff_choices = []
            response = get_occurrences(foreign_event_ids=Show.objects.filter(
                e_conference=initial['conference']
                ).values_list('eventitem_id', flat=True))
            for item in response.occurrences:
                show = Show.objects.get(eventitem_id=item.foreign_event_id)
                show_choices += [(item.pk, "%s - %s" % (
                    show.e_title,
                    item.start_time.strftime(DATETIME_FORMAT)))]
            if len(show_choices) > 0:
                complete_choices += [('Shows', show_choices)]
            response = get_occurrences(
                foreign_event_ids=GenericEvent.objects.filter(
                    e_conference=initial['conference'],
                    type="Special"
                    ).values_list('eventitem_id', flat=True))
            for item in response.occurrences:
                special = GenericEvent.objects.get(
                    eventitem_id=item.foreign_event_id)
                special_choices += [(item.pk, "%s - %s" % (
                    special.e_title,
                    item.start_time.strftime(DATETIME_FORMAT)))]
            if len(special_choices) > 0:
                complete_choices += [('Special Events', special_choices)]
            for item in StaffArea.objects.filter(
                    conference=initial['conference']):
                staff_choices += [("staff_%d" % item.pk,
                                   item.title)]
            if len(staff_choices) > 0:
                complete_choices += [('Staff Areas', staff_choices)]
            complete_choices += [(
                'Standalone',
                [("", "Make a Volunteer Opportunity with no topic"), ])]
            self.fields['volunteer_topic'].choices = complete_choices

