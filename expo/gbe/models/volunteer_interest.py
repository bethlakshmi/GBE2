from django.db import models
from gbe.models import (
    AvailableInterest,
    Volunteer
)
from gbe_forms_text import rank_interest_options

class VolunteerInterest(models.Model):
    interest = models.ForeignKey(AvailableInterest)
    volunteer = models.ForeignKey(Volunteer)
    rank = models.IntegerField(choices=rank_interest_options,
                               blank=True)

    class Meta:
        app_label = "gbe"
        unique_together = (('interest', 'volunteer'),)
