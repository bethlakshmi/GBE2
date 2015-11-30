# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from datetime import date, time, datetime
from pytz import utc


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        gbe2015 = orm.Conference.objects.get(conference_slug="GBE2015")
        gbe2016 = orm.Conference.objects.get(conference_slug="GBE2016")
        shifts = {}
        shifts [gbe2015]={}
        shifts [gbe2016]={}

        thu15 = orm.ConferenceDay(
            day = date(2015, 02, 19), 
            conference = gbe2015)
        thu15.save()
        shifts[gbe2015]['SH0'] = orm.VolunteerWindow(
            day=thu15,
            start=time(18,0),
            end=time(23,0))
        shifts[gbe2015]['SH0'].save() 
        fri15 = orm.ConferenceDay(
            day = date(2015, 02, 20), 
            conference = gbe2015)
        fri15.save()
        shifts[gbe2015]['SH1'] = orm.VolunteerWindow(
            day=fri15,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2015]['SH1'].save() 
        shifts[gbe2015]['SH2'] = orm.VolunteerWindow(
            day=fri15,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2015]['SH2'].save() 
        shifts[gbe2015]['SH3'] = orm.VolunteerWindow(
            day=fri15,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2015]['SH3'].save() 
        shifts[gbe2015]['SH4'] = orm.VolunteerWindow(
            day=fri15,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2015]['SH4'].save() 
        sat15 = orm.ConferenceDay.objects.create(
            day = date(2015, 02, 21), 
            conference = gbe2015)
        sat15.save()
        shifts[gbe2015]['SH5'] = orm.VolunteerWindow(
            day=sat15,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2015]['SH5'].save() 
        shifts[gbe2015]['SH6'] = orm.VolunteerWindow(
            day=sat15,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2015]['SH6'].save() 
        shifts[gbe2015]['SH7'] = orm.VolunteerWindow(
            day=sat15,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2015]['SH7'].save() 
        shifts[gbe2015]['SH8'] = orm.VolunteerWindow(
            day=sat15,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2015]['SH8'].save()
        sun15 = orm.ConferenceDay.objects.create(
            day = date(2015, 02, 22), 
            conference = gbe2015)
        sun15.save()
        shifts[gbe2015]['SH9'] = orm.VolunteerWindow(
            day=sun15,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2015]['SH9'].save() 
        shifts[gbe2015]['SH10'] = orm.VolunteerWindow(
            day=sun15,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2015]['SH10'].save() 
        shifts[gbe2015]['SH11'] = orm.VolunteerWindow(
            day=sun15,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2015]['SH11'].save() 
        shifts[gbe2015]['SH12'] = orm.VolunteerWindow(
            day=sun15,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2015]['SH12'].save()
        mon15 = orm.ConferenceDay.objects.create(
            day = date(2015, 02, 23), 
            conference = gbe2015)
        mon15.save()
        shifts[gbe2015]['SH13'] = orm.VolunteerWindow(
            day=mon15,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2015]['SH13'].save()


        thu16 = orm.ConferenceDay(
            day = date(2016, 02, 4), 
            conference = gbe2016)
        thu16.save()
        shifts[gbe2016]['SH0'] = orm.VolunteerWindow(
            day=thu16,
            start=time(18,0),
            end=time(23,0))
        shifts[gbe2016]['SH0'].save() 
        fri16 = orm.ConferenceDay(
            day = date(2016, 02, 5), 
            conference = gbe2016)
        fri16.save()
        shifts[gbe2016]['SH1'] = orm.VolunteerWindow(
            day=fri16,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2016]['SH1'].save() 
        shifts[gbe2016]['SH2'] = orm.VolunteerWindow(
            day=fri16,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2016]['SH2'].save() 
        shifts[gbe2016]['SH3'] = orm.VolunteerWindow(
            day=fri16,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2016]['SH3'].save() 
        shifts[gbe2016]['SH4'] = orm.VolunteerWindow(
            day=fri16,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2016]['SH4'].save() 
        sat16 = orm.ConferenceDay.objects.create(
            day = date(2016, 02, 6), 
            conference = gbe2016)
        sat16.save()
        shifts[gbe2016]['SH5'] = orm.VolunteerWindow(
            day=sat16,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2016]['SH5'].save() 
        shifts[gbe2016]['SH6'] = orm.VolunteerWindow(
            day=sat16,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2016]['SH6'].save() 
        shifts[gbe2016]['SH7'] = orm.VolunteerWindow(
            day=sat16,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2016]['SH7'].save() 
        shifts[gbe2016]['SH8'] = orm.VolunteerWindow(
            day=sat16,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2016]['SH8'].save()
        sun16 = orm.ConferenceDay.objects.create(
            day = date(2016, 02, 7), 
            conference = gbe2016)
        sun16.save()
        shifts[gbe2016]['SH9'] = orm.VolunteerWindow(
            day=sun16,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2016]['SH9'].save() 
        shifts[gbe2016]['SH10'] = orm.VolunteerWindow(
            day=sun16,
            start=time(12,0),
            end=time(18,0))
        shifts[gbe2016]['SH10'].save() 
        shifts[gbe2016]['SH11'] = orm.VolunteerWindow(
            day=sun16,
            start=time(17,0),
            end=time(22,0))
        shifts[gbe2016]['SH11'].save() 
        shifts[gbe2016]['SH12'] = orm.VolunteerWindow(
            day=sun16,
            start=time(20,0),
            end=time(23,0))
        shifts[gbe2016]['SH12'].save()
        mon16 = orm.ConferenceDay.objects.create(
            day = date(2016, 02, 8), 
            conference = gbe2016)
        mon16.save()
        shifts[gbe2016]['SH13'] = orm.VolunteerWindow(
            day=mon16,
            start=time(9,0),
            end=time(12,0))
        shifts[gbe2016]['SH13'].save()
        
        dday = datetime(2015, 2, 24, 0, 0 ,0)

        for volunteer in orm.Volunteer.objects.all():
            for shift in eval(volunteer.availability):
                volunteer.available_windows.add(shifts[volunteer.conference][shift])
            for shift in eval(volunteer.unavailability):
                volunteer.unavailable_windows.add(shifts[volunteer.conference][shift])


    def backwards(self, orm):
        "Write your backwards methods here."
        for volunteer in orm.Volunteer.objects.all():
            volunteer.availability = "[u'SH0']"  # no reverse from here
            volunteer.availability = "[u'SH0']"  
            volunteer.save()






    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'gbe.act': {
            'Meta': {'object_name': 'Act', '_ormbases': [u'gbe.Biddable', u'scheduler.ActItem']},
            u'actitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ActItem']", 'unique': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'other_performance': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'acts'", 'null': 'True', 'to': u"orm['gbe.Performer']"}),
            'shows_preferences': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tech': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.TechInfo']", 'unique': 'True', 'blank': 'True'}),
            'video_choice': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'video_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'why_you': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'gbe.adbid': {
            'Meta': {'object_name': 'AdBid', '_ormbases': [u'gbe.Biddable']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'gbe.artbid': {
            'Meta': {'object_name': 'ArtBid', '_ormbases': [u'gbe.Biddable']},
            'art1': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'art2': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'art3': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'works': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'gbe.audioinfo': {
            'Meta': {'object_name': 'AudioInfo'},
            'confirm_no_music': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need_mic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'own_mic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'track': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'track_artist': ('django.db.models.fields.CharField', [], {'max_length': '123', 'blank': 'True'}),
            'track_duration': ('gbe.expomodelfields.DurationField', [], {'blank': 'True'}),
            'track_title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        u'gbe.biddable': {
            'Meta': {'object_name': 'Biddable'},
            'accepted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Conference']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'gbe.bidevaluation': {
            'Meta': {'object_name': 'BidEvaluation'},
            'bid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Biddable']"}),
            'evaluator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gbe.class': {
            'Meta': {'object_name': 'Class', '_ormbases': [u'gbe.Biddable', u'gbe.Event']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Event']", 'unique': 'True'}),
            'fee': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'length_minutes': ('django.db.models.fields.IntegerField', [], {'default': '60', 'blank': 'True'}),
            'maximum_enrollment': ('django.db.models.fields.IntegerField', [], {'default': '20', 'blank': 'True'}),
            'minimum_enrollment': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'multiple_run': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '20'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'other_teachers': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'physical_restrictions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'run_before': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'schedule_constraints': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'space_needs': ('django.db.models.fields.CharField', [], {'default': "'Please Choose an Option'", 'max_length': '128', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'is_teaching'", 'to': u"orm['gbe.Persona']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Lecture'", 'max_length': '128', 'blank': 'True'})
        },
        u'gbe.classproposal': {
            'Meta': {'object_name': 'ClassProposal'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Conference']"}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'proposal': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Class'", 'max_length': '20'})
        },
        u'gbe.combo': {
            'Meta': {'ordering': "['name']", 'object_name': 'Combo', '_ormbases': [u'gbe.Performer']},
            'membership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'combos'", 'symmetrical': 'False', 'to': u"orm['gbe.Persona']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gbe.conference': {
            'Meta': {'object_name': 'Conference'},
            'accepting_bids': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conference_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'conference_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'upcoming'", 'max_length': '50'})
        },
        u'gbe.conferenceday': {
            'Meta': {'ordering': "['day']", 'object_name': 'ConferenceDay'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Conference']"}),
            'day': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'gbe.conferencevolunteer': {
            'Meta': {'object_name': 'ConferenceVolunteer'},
            'bid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.ClassProposal']"}),
            'how_volunteer': ('django.db.models.fields.CharField', [], {'default': "'Any of the Above'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'presenter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conf_volunteer'", 'to': u"orm['gbe.Persona']"}),
            'qualification': ('django.db.models.fields.TextField', [], {'blank': "'True'"}),
            'volunteering': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'gbe.cueinfo': {
            'Meta': {'object_name': 'CueInfo'},
            'backlight': ('django.db.models.fields.CharField', [], {'default': "'OFF'", 'max_length': '20'}),
            'center_spot': ('django.db.models.fields.CharField', [], {'default': "'OFF'", 'max_length': '20'}),
            'cue_off_of': ('django.db.models.fields.TextField', [], {}),
            'cue_sequence': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'cyc_color': ('django.db.models.fields.CharField', [], {'default': "('Blue', 'Blue')", 'max_length': '25'}),
            'follow_spot': ('django.db.models.fields.CharField', [], {'default': "('White', 'White')", 'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sound_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'techinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.TechInfo']"}),
            'wash': ('django.db.models.fields.CharField', [], {'default': "('White', 'White')", 'max_length': '25'})
        },
        u'gbe.event': {
            'Meta': {'ordering': "['title']", 'object_name': 'Event', '_ormbases': [u'scheduler.EventItem']},
            'blurb': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Conference']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration': ('gbe.expomodelfields.DurationField', [], {}),
            'event_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'eventitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.EventItem']", 'unique': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'gbe.genericevent': {
            'Meta': {'ordering': "['title']", 'object_name': 'GenericEvent', '_ormbases': [u'gbe.Event']},
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Special'", 'max_length': '128'}),
            'volunteer_category': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        u'gbe.lightinginfo': {
            'Meta': {'object_name': 'LightingInfo'},
            'costume': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'gbe.performer': {
            'Meta': {'ordering': "['name']", 'object_name': 'Performer', '_ormbases': [u'scheduler.WorkerItem']},
            'awards': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bio': ('django.db.models.fields.TextField', [], {}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact'", 'to': u"orm['gbe.Profile']"}),
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'festivals': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'promo_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'workeritem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.WorkerItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gbe.performerfestivals': {
            'Meta': {'object_name': 'PerformerFestivals'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Act']"}),
            'experience': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '20'}),
            'festival': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'gbe.persona': {
            'Meta': {'ordering': "['name']", 'object_name': 'Persona', '_ormbases': [u'gbe.Performer']},
            'performer_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'personae'", 'to': u"orm['gbe.Profile']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gbe.profile': {
            'Meta': {'ordering': "['display_name']", 'object_name': 'Profile', '_ormbases': [u'scheduler.WorkerItem']},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'best_time': ('django.db.models.fields.CharField', [], {'default': "'Any'", 'max_length': '50', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'how_heard': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'purchase_email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'user_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            u'workeritem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.WorkerItem']", 'unique': 'True', 'primary_key': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'gbe.profilepreferences': {
            'Meta': {'object_name': 'ProfilePreferences'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_hotel': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'inform_about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'preferences'", 'unique': 'True', 'to': u"orm['gbe.Profile']"}),
            'show_hotel_infobox': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'gbe.room': {
            'Meta': {'object_name': 'Room', '_ormbases': [u'scheduler.LocationItem']},
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            u'locationitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.LocationItem']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'overbook_size': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gbe.show': {
            'Meta': {'ordering': "['title']", 'object_name': 'Show', '_ormbases': [u'gbe.Event']},
            'acts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'appearing_in'", 'blank': 'True', 'to': u"orm['gbe.Act']"}),
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'mc': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'mc_for'", 'blank': 'True', 'to': u"orm['gbe.Persona']"})
        },
        u'gbe.stageinfo': {
            'Meta': {'object_name': 'StageInfo'},
            'act_duration': ('gbe.expomodelfields.DurationField', [], {'blank': 'True'}),
            'clear_props': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cue_props': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'set_props': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'gbe.techinfo': {
            'Meta': {'object_name': 'TechInfo'},
            'audio': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.AudioInfo']", 'unique': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lighting': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.LightingInfo']", 'unique': 'True', 'blank': 'True'}),
            'stage': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.StageInfo']", 'unique': 'True', 'blank': 'True'})
        },
        u'gbe.troupe': {
            'Meta': {'ordering': "['name']", 'object_name': 'Troupe', '_ormbases': [u'gbe.Performer']},
            'membership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'troupes'", 'symmetrical': 'False', 'to': u"orm['gbe.Persona']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'gbe.vendor': {
            'Meta': {'object_name': 'Vendor', '_ormbases': [u'gbe.Biddable']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'help_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'help_times': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'logo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'physical_address': ('django.db.models.fields.TextField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.Profile']"}),
            'publish_physical_address': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_help': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'gbe.volunteer': {
            'Meta': {'object_name': 'Volunteer', '_ormbases': [u'gbe.Biddable']},
            'availability': ('django.db.models.fields.TextField', [], {}),
            'available_windows': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'availablewindow_set'", 'blank': 'True', 'to': u"orm['gbe.VolunteerWindow']"}),
            'background': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'interests': ('django.db.models.fields.TextField', [], {}),
            'number_shifts': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'opt_outs': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pre_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'volunteering'", 'to': u"orm['gbe.Profile']"}),
            'unavailability': ('django.db.models.fields.TextField', [], {}),
            'unavailable_windows': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'unavailablewindow_set'", 'blank': 'True', 'to': u"orm['gbe.VolunteerWindow']"})
        },
        u'gbe.volunteerwindow': {
            'Meta': {'ordering': "['day', 'start']", 'object_name': 'VolunteerWindow'},
            'day': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gbe.ConferenceDay']"}),
            'end': ('django.db.models.fields.TimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'blank': 'True'})
        },
        u'scheduler.actitem': {
            'Meta': {'object_name': 'ActItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.eventitem': {
            'Meta': {'object_name': 'EventItem'},
            'eventitem_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'scheduler.locationitem': {
            'Meta': {'object_name': 'LocationItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.resourceitem': {
            'Meta': {'object_name': 'ResourceItem'},
            'resourceitem_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'scheduler.workeritem': {
            'Meta': {'object_name': 'WorkerItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['gbe']
    symmetrical = True
