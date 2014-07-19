from django.forms.fields import CharField
from django.forms.util import ValidationError as FormValidationError

class DurationFormField(CharField):
    def __init__(self, *args, **kwargs):
        self.max_length = 10
        super(DurationFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(CharField, self).clean(value)
        if len(value.split(':')) != 2:
            raise FormValidationError('Data entered must be in format MM:SS')
        return value
