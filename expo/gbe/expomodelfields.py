from django.db import models
from django.db.models.fields import IntegerField
from expoformfields import DurationFormField
from datetime import timedelta
from django.core.exceptions import ValidationError


class Duration(timedelta):
    def __init__ (self, *args, **kwargs):
        super(timedelta, self)
    

    def __str__(self):
        return ':'.join(map(str, [self.seconds/60,self.seconds%60]))


class DurationField(IntegerField):
    __metaclass__ = models.SubfieldBase

    def contribute_to_class(self, cls, name):
        super(DurationField, self).contribute_to_class(cls, name)

    def get_internal_type(self):
        return 'DurationField'

    def db_type(self, connection=None):
        return 'bigint'
    
    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, (int, long)):
            return Duration(seconds=value)
        elif isinstance(value, (basestring, unicode)):
            try:
                minutes, seconds = map(int, value.split(':'))
                return Duration(seconds=(seconds + minutes*60))
            except:
                raise ValidationError ('That didn\'t look like a duration to me')
        elif not isinstance(value, timedelta):
            raise ValidationError('Unable to convert %s to Duration.' % value)
        return value

    def get_prep_value(self, value):
            minutes, seconds = divmod(value.seconds, 60)
            return "%02d:%02d" % (minutes, seconds)
              
    def get_db_prep_value(self, value, connection, prepared=False):
        if value == None:
            return 0
        if isinstance(value, timedelta):
            return value.seconds + (86400 * value.days)
        try:
            value = int(value)
            return value
        except:
            return 0
#            raise ValueError('%s is not a reasonable value for a duration' % value)

    def value_to_string(self, instance):
        timedelta = getattr(instance, self.name)
        if timedelta:
            minutes, seconds = divmod(timedelta.seconds, 60)
            return "%02d:%02d" % (minutes, seconds)
        return None


    def formfield(self, form_class=DurationFormField, **kwargs):
        defaults = {"help_text": "Enter duration in the format: MM:SS"}
        defaults.update(kwargs)
        return form_class(**defaults)
