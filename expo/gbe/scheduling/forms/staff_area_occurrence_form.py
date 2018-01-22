from django.forms import (
    Form,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import Room
from gbe_forms_text import schedule_occurrence_labels


class StaffAreaOccurrenceForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    max_volunteer = IntegerField(required=True, initial=0)
    occurrence_id = IntegerField(required=False, widget=HiddenInput())
