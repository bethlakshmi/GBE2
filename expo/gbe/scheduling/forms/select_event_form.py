from django.forms import (
    Form,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import calendar_type as calendar_type_options
from gbe.models import AvailableInterest

class SelectEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    day = MultipleChoiceField(
        widget=CheckboxSelectMultiple(),
        required=False)
    calendar_type = MultipleChoiceField(
        choices=calendar_type_options.items(),
        widget=CheckboxSelectMultiple(),
        required=False)
    volunteer_type = MultipleChoiceField(
        choices=AvailableInterest.objects.filter(
            visible=True).values_list('pk', 'interest'),
        widget=CheckboxSelectMultiple(),
        required=False)


class HiddenSelectEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    day = MultipleChoiceField(
        widget=MultipleHiddenInput(),
        required=False)
    calendar_type = MultipleChoiceField(
        choices=calendar_type_options.items(),
        widget=MultipleHiddenInput(),
        required=False)
    volunteer_type = MultipleChoiceField(
        choices=AvailableInterest.objects.filter(
            visible=True).values_list('pk', 'interest'),
        widget=MultipleHiddenInput(),
        required=False)
