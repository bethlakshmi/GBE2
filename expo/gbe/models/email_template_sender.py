from django.db.models import (
    EmailField,
    Model,
    OneToOneField,
)
from post_office.models import EmailTemplate


class EmailTemplateSender(Model):
    template = OneToOneField(EmailTemplate)
    from_email = EmailField()

    class Meta:
        ordering = ['template']
        app_label = "gbe"
