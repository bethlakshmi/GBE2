from django.db import models
from django.db.models.fields import IntegerField
from expoformfields import DurationFormField
import datetime

class DurationField(IntegerField):
    __metaclass__ = models.SubfieldBase

    def contribute_to_class(self, cls, name):
        super(DurationField, self).contribute_to_class(cls, name)

    
    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, (int, long)):
            return datetime.timedelta(seconds=value)
        elif isinstance(value, (basestring, unicode)):
            minutes, seconds = map(int, value.split(':'))
            return datetime.timedelta(seconds=(seconds + minutes*60))
        elif not isinstance(value, datetime.timedelta):
            raise ValidationError('Unable to convert %s to timedelta.' % value)
        return value
              
    def get_db_prep_value(self, value, connection, prepared=False):
        return value.seconds + (86400 * value.days)

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
