# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actresource',
            name='role',
            field=models.CharField(blank=True, max_length=50, choices=[(b'Featured Performer', b'Featured Performer'), (b'Host', b'Host')]),
        ),
    ]
