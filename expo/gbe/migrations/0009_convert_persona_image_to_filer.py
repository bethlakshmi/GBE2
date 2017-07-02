# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


def create_filer_images(apps, schema_editor):
    from filer.models import Image
    Performer = apps.get_model('gbe', 'Performer')
    for performer in Performer.objects.all():
        if performer.promo_image:
            img, created = Image.objects.get_or_create(
                file=performer.promo_image.file,
                defaults={
                    'name': performer.name,
                    'description': performer.bio,
            })
            performer.img = img
            performer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20161016_1055'),
        ('gbe', '0008_remove_act_is_summer'),
    ]

    operations = [
        migrations.RunPython(create_filer_images),
    ]
