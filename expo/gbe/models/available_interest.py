from django.db import models


class AvailableInterest(models.Model):
    interest = models.CharField(
        max_length=128,
        unique=True)
    visible = models.BooleanField(default=True)
    help_text = models.TextField(max_length=500)

    class Meta:
        app_label = "gbe"
