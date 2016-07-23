# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Volunteer.interests'
        db.delete_column(u'gbe_volunteer', 'interests')


    def backwards(self, orm):
        # Adding field 'Volunteer.interests'
        db.add_column(u'gbe_volunteer', 'interests',
                      self.gf('django.db.models.fields.TextField')(default='[]'),
                      keep_default=False)


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
        'gbe.act': {
            'Meta': {'object_name': 'Act', '_ormbases': ['gbe.Biddable', u'scheduler.ActItem']},
            u'actitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ActItem']", 'unique': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'other_performance': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'acts'", 'null': 'True', 'to': "orm['gbe.Performer']"}),
            'shows_preferences': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tech': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.TechInfo']", 'unique': 'True', 'blank': 'True'}),
            'video_choice': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'video_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'why_you': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'gbe.adbid': {
            'Meta': {'object_name': 'AdBid', '_ormbases': ['gbe.Biddable']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'gbe.artbid': {
            'Meta': {'object_name': 'ArtBid', '_ormbases': ['gbe.Biddable']},
            'art1': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'art2': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'art3': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'works': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'gbe.audioinfo': {
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
        'gbe.availableinterest': {
            'Meta': {'object_name': 'AvailableInterest'},
            'help_text': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gbe.biddable': {
            'Meta': {'object_name': 'Biddable'},
            'accepted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Conference']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'gbe.bidevaluation': {
            'Meta': {'object_name': 'BidEvaluation'},
            'bid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Biddable']"}),
            'evaluator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        },
        'gbe.class': {
            'Meta': {'object_name': 'Class', '_ormbases': ['gbe.Biddable', 'gbe.Event']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Event']", 'unique': 'True'}),
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
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'is_teaching'", 'to': "orm['gbe.Persona']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Lecture'", 'max_length': '128', 'blank': 'True'})
        },
        'gbe.classproposal': {
            'Meta': {'object_name': 'ClassProposal'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Conference']"}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'proposal': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Class'", 'max_length': '20'})
        },
        'gbe.combo': {
            'Meta': {'ordering': "['name']", 'object_name': 'Combo', '_ormbases': ['gbe.Performer']},
            'membership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'combos'", 'symmetrical': 'False', 'to': "orm['gbe.Persona']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'gbe.conference': {
            'Meta': {'object_name': 'Conference'},
            'accepting_bids': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conference_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'conference_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'upcoming'", 'max_length': '50'})
        },
        'gbe.conferenceday': {
            'Meta': {'ordering': "['day']", 'object_name': 'ConferenceDay'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Conference']"}),
            'day': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'gbe.conferencevolunteer': {
            'Meta': {'object_name': 'ConferenceVolunteer'},
            'bid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.ClassProposal']"}),
            'how_volunteer': ('django.db.models.fields.CharField', [], {'default': "'Any of the Above'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'presenter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conf_volunteer'", 'to': "orm['gbe.Persona']"}),
            'qualification': ('django.db.models.fields.TextField', [], {'blank': "'True'"}),
            'volunteering': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gbe.costume': {
            'Meta': {'object_name': 'Costume', '_ormbases': ['gbe.Biddable']},
            'act_title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'active_use': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'debut_date': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'dress_size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'more_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pasties': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Persona']", 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'pieces': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'costumes'", 'to': "orm['gbe.Profile']"})
        },
        'gbe.cueinfo': {
            'Meta': {'object_name': 'CueInfo'},
            'backlight': ('django.db.models.fields.CharField', [], {'default': "'OFF'", 'max_length': '20'}),
            'center_spot': ('django.db.models.fields.CharField', [], {'default': "'OFF'", 'max_length': '20'}),
            'cue_off_of': ('django.db.models.fields.TextField', [], {}),
            'cue_sequence': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'cyc_color': ('django.db.models.fields.CharField', [], {'default': "('Blue', 'Blue')", 'max_length': '25'}),
            'follow_spot': ('django.db.models.fields.CharField', [], {'default': "('White', 'White')", 'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sound_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'techinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.TechInfo']"}),
            'wash': ('django.db.models.fields.CharField', [], {'default': "('White', 'White')", 'max_length': '25'})
        },
        'gbe.event': {
            'Meta': {'ordering': "['title']", 'object_name': 'Event', '_ormbases': [u'scheduler.EventItem']},
            'blurb': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Conference']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration': ('gbe.expomodelfields.DurationField', [], {}),
            'event_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'eventitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.EventItem']", 'unique': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'gbe.genericevent': {
            'Meta': {'ordering': "['title']", 'object_name': 'GenericEvent', '_ormbases': ['gbe.Event']},
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Special'", 'max_length': '128'}),
            'volunteer_category': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        'gbe.lightinginfo': {
            'Meta': {'object_name': 'LightingInfo'},
            'costume': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'specific_needs': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'gbe.performer': {
            'Meta': {'ordering': "['name']", 'object_name': 'Performer', '_ormbases': [u'scheduler.WorkerItem']},
            'awards': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bio': ('django.db.models.fields.TextField', [], {}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact'", 'to': "orm['gbe.Profile']"}),
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'festivals': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'promo_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'workeritem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.WorkerItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        'gbe.performerfestivals': {
            'Meta': {'object_name': 'PerformerFestivals'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Act']"}),
            'experience': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '20'}),
            'festival': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'gbe.persona': {
            'Meta': {'ordering': "['name']", 'object_name': 'Persona', '_ormbases': ['gbe.Performer']},
            'performer_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'personae'", 'to': "orm['gbe.Profile']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'gbe.profile': {
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
        'gbe.profilepreferences': {
            'Meta': {'object_name': 'ProfilePreferences'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_hotel': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'inform_about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'preferences'", 'unique': 'True', 'to': "orm['gbe.Profile']"}),
            'show_hotel_infobox': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gbe.room': {
            'Meta': {'object_name': 'Room', '_ormbases': [u'scheduler.LocationItem']},
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            u'locationitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.LocationItem']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'overbook_size': ('django.db.models.fields.IntegerField', [], {})
        },
        'gbe.show': {
            'Meta': {'ordering': "['title']", 'object_name': 'Show', '_ormbases': ['gbe.Event']},
            'acts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'appearing_in'", 'blank': 'True', 'to': "orm['gbe.Act']"}),
            'cue_sheet': ('django.db.models.fields.CharField', [], {'default': "'Theater'", 'max_length': '128'}),
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'mc': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'mc_for'", 'blank': 'True', 'to': "orm['gbe.Persona']"})
        },
        'gbe.stageinfo': {
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
        'gbe.techinfo': {
            'Meta': {'object_name': 'TechInfo'},
            'audio': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.AudioInfo']", 'unique': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lighting': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.LightingInfo']", 'unique': 'True', 'blank': 'True'}),
            'stage': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.StageInfo']", 'unique': 'True', 'blank': 'True'})
        },
        'gbe.troupe': {
            'Meta': {'ordering': "['name']", 'object_name': 'Troupe', '_ormbases': ['gbe.Performer']},
            'membership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'troupes'", 'symmetrical': 'False', 'to': "orm['gbe.Persona']"}),
            u'performer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Performer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'gbe.usermessage': {
            'Meta': {'unique_together': "(('view', 'code'),)", 'object_name': 'UserMessage'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'view': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'gbe.vendor': {
            'Meta': {'object_name': 'Vendor', '_ormbases': ['gbe.Biddable']},
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'help_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'help_times': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'logo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'physical_address': ('django.db.models.fields.TextField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Profile']"}),
            'publish_physical_address': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_help': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'gbe.volunteer': {
            'Meta': {'object_name': 'Volunteer', '_ormbases': ['gbe.Biddable']},
            'availability': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'available_windows': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'availablewindow_set'", 'blank': 'True', 'to': "orm['gbe.VolunteerWindow']"}),
            'background': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'number_shifts': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'opt_outs': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pre_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'volunteering'", 'to': "orm['gbe.Profile']"}),
            'unavailability': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unavailable_windows': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'unavailablewindow_set'", 'blank': 'True', 'to': "orm['gbe.VolunteerWindow']"})
        },
        'gbe.volunteerinterest': {
            'Meta': {'unique_together': "(('interest', 'volunteer'),)", 'object_name': 'VolunteerInterest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.AvailableInterest']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '2', 'blank': 'True'}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.Volunteer']"})
        },
        'gbe.volunteerwindow': {
            'Meta': {'ordering': "['day', 'start']", 'object_name': 'VolunteerWindow'},
            'day': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.ConferenceDay']"}),
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