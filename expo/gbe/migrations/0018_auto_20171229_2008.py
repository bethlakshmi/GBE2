# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0017_remove_vendor_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='BidReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.CharField(blank=True, max_length=10, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'F', b'F'), (b'', b'NA')])),
                ('bid', models.ForeignKey(to='gbe.Biddable')),
                ('profile', models.ForeignKey(to='gbe.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='BidReviewComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(max_length=500, blank=True)),
                ('bid', models.ForeignKey(to='gbe.Biddable')),
                ('profile', models.ForeignKey(to='gbe.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='BidReviewQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=200)),
                ('bid_type', models.CharField(max_length=20, choices=[(b'Act', b'Act'), (b'Class', b'Class'), (b'Costume', b'Costume'), (b'Vendor', b'Vendor'), (b'Volunteer', b'Volunteer')])),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(max_length=500, blank=True)),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='show',
            name='acts',
        ),
        migrations.RemoveField(
            model_name='show',
            name='cue_sheet',
        ),
        migrations.AlterUniqueTogether(
            name='bidreviewquestion',
            unique_together=set([('order', 'bid_type'), ('question', 'bid_type')]),
        ),
        migrations.AddField(
            model_name='bidreview',
            name='question',
            field=models.ForeignKey(to='gbe.BidReviewQuestion'),
        ),
        migrations.AlterUniqueTogether(
            name='bidreviewcomment',
            unique_together=set([('profile', 'bid')]),
        ),
        migrations.AlterUniqueTogether(
            name='bidreview',
            unique_together=set([('question', 'profile', 'bid')]),
        ),
    ]
