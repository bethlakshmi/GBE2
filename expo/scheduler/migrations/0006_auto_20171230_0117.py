# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0005_auto_20171217_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventEvalComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(max_length=500, blank=True)),
                ('event', models.ForeignKey(to='scheduler.Event')),
                ('profile', models.ForeignKey(to='scheduler.WorkerItem')),
            ],
        ),
        migrations.CreateModel(
            name='EventEvalGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.CharField(blank=True, max_length=10, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F'), (b'', b'NA')])),
                ('event', models.ForeignKey(to='scheduler.Event')),
                ('profile', models.ForeignKey(to='scheduler.WorkerItem')),
            ],
        ),
        migrations.CreateModel(
            name='EventEvalQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=200)),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(max_length=500, blank=True)),
                ('order', models.IntegerField()),
                ('answer_type', models.CharField(max_length=20, choices=[(b'grade', b'grade'), (b'text', b'text')])),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='eventevalquestion',
            unique_together=set([('order',), ('question',)]),
        ),
        migrations.AddField(
            model_name='eventevalgrade',
            name='question',
            field=models.ForeignKey(to='scheduler.EventEvalQuestion'),
        ),
        migrations.AddField(
            model_name='eventevalcomment',
            name='question',
            field=models.ForeignKey(to='scheduler.EventEvalQuestion'),
        ),
        migrations.AlterUniqueTogether(
            name='eventevalgrade',
            unique_together=set([('question', 'profile', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventevalcomment',
            unique_together=set([('profile', 'event')]),
        ),
    ]
