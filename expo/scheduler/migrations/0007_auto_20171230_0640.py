# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_auto_20171230_0401'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventEvalBoolean',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.BooleanField()),
                ('event', models.ForeignKey(to='scheduler.Event')),
                ('profile', models.ForeignKey(to='scheduler.WorkerItem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='eventevalyesno',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='eventevalyesno',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventevalyesno',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='eventevalyesno',
            name='question',
        ),
        migrations.AlterField(
            model_name='eventevalquestion',
            name='answer_type',
            field=models.CharField(max_length=20, choices=[(b'grade', b'grade'), (b'text', b'text'), (b'boolean', b'boolean')]),
        ),
        migrations.DeleteModel(
            name='EventEvalYesNo',
        ),
        migrations.AddField(
            model_name='eventevalboolean',
            name='question',
            field=models.ForeignKey(to='scheduler.EventEvalQuestion'),
        ),
        migrations.AlterUniqueTogether(
            name='eventevalboolean',
            unique_together=set([('profile', 'event', 'question')]),
        ),
    ]
