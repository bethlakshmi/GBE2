# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0013_auto_20170829_0358'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferenceday',
            name='open_to_public',
            field=models.BooleanField(default=True),
        ),
    ]
