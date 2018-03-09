from django.forms import (
    ModelChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import Show


class PickShowForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    accepted_class = ModelChoiceField(
        queryset=Show.objects.all().order_by('e_title'),
        widget=RadioSelect,
        empty_label="Make New Show",
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(PickShowForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            self.fields['accepted_class'].queryset = Show.objects.filter(
                e_conference=initial['conference']).order_by('e_title')
