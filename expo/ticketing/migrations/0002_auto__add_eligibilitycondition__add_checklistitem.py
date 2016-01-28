# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EligibilityCondition'
        db.create_table(u'ticketing_eligibilitycondition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checklist_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'ticketing_eligibilitycondition', to=orm['ticketing.CheckListItem'])),
        ))
        db.send_create_signal(u'ticketing', ['EligibilityCondition'])

        # Adding model 'CheckListItem'
        db.create_table(u'ticketing_checklistitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'ticketing', ['CheckListItem'])


    def backwards(self, orm):
        # Deleting model 'EligibilityCondition'
        db.delete_table(u'ticketing_eligibilitycondition')

        # Deleting model 'CheckListItem'
        db.delete_table(u'ticketing_checklistitem')


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
        u'gbe.conference': {
            'Meta': {'object_name': 'Conference'},
            'accepting_bids': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conference_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'conference_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'upcoming'", 'max_length': '50'})
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
        u'scheduler.eventitem': {
            'Meta': {'object_name': 'EventItem'},
            'eventitem_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'ticketing.brownpaperevents': {
            'Meta': {'object_name': 'BrownPaperEvents'},
            'act_submission_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'badgeable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bpt_event_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ticketing_item'", 'to': u"orm['gbe.Conference']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_conference': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_most': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'linked_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'ticketing_item'", 'blank': 'True', 'to': u"orm['gbe.Event']"}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ticket_style': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'vendor_submission_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ticketing.brownpapersettings': {
            'Meta': {'object_name': 'BrownPaperSettings'},
            'client_username': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'developer_token': ('django.db.models.fields.CharField', [], {'max_length': '15', 'primary_key': 'True'}),
            'last_poll_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.checklistitem': {
            'Meta': {'object_name': 'CheckListItem'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ticketing.eligibilitycondition': {
            'Meta': {'object_name': 'EligibilityCondition'},
            'checklist_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'ticketing_eligibilitycondition'", 'to': u"orm['ticketing.CheckListItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ticketing.purchaser': {
            'Meta': {'object_name': 'Purchaser'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'matched_to_user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'ticketing.ticketitem': {
            'Meta': {'object_name': 'TicketItem'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bpt_event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ticketitems'", 'blank': 'True', 'to': u"orm['ticketing.BrownPaperEvents']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'datestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ticket_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'ticketing.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order_date': ('django.db.models.fields.DateTimeField', [], {}),
            'order_notes': ('django.db.models.fields.TextField', [], {}),
            'payment_source': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'purchaser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Purchaser']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ticket_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.TicketItem']"})
        }
    }

    complete_apps = ['ticketing']