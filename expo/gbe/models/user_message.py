from django.db import models

class UserMessage(models.Model):
    summary = models.CharField(max_length=128)
    description = models.TextField(max_length=500)
    view = models.CharField(max_length=128)
    code = models.CharField(max_length=128)

    class Meta:
        app_label = "gbe"
    