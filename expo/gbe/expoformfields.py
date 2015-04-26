from django.forms.fields import CharField
from django.forms.util import ValidationError as FormValidationError
from datetime import timedelta
from duration import Duration


class DurationFormField(CharField):
    def __init__(self, *args, **kwargs):
        super(DurationFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(CharField, self).clean(value)
        try:
            return self.parse_to_duration(value)
        except ValueError:
            raise FormValidationError('Data entered must be in format MM:SS')

    def parse_to_duration(self, value):
        '''
        Attempt to make a value out of this string
        For now the rules are: '' => zero-duration timedelta
        'mm:ss' || 'hh:mm:ss' => timedelta of this value
        else: ValueError
        '''
        if value == None:
            return Duration(0)
        if len(value) == 0:
            return Duration(0)
        vs = [int(v) for v in value.split(':')]
        if len(vs) < 2 or len(vs) > 4:
            raise ValueError('Format error with value: %s' % value)
        time = vs[-1] + 60 * vs[-2]
        if len(vs) == 3:
            time += 60 * 60 * vs[0]
        return Duration(seconds = time)

    def to_python(self, value):
        try:
            return self.parse_to_duration(value)
        except ValueError:
            raise FormValidationError('Please enter your duration as mm:ss')
