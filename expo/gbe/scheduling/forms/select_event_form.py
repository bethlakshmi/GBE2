from django.forms import (
    Form,
    MultipleChoiceField,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import calendar_type as calendar_type_options


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
