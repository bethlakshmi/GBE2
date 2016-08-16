# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Schedulable'
        db.create_table(u'scheduler_schedulable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['Schedulable'])

        # Adding model 'ResourceItem'
        db.create_table(u'scheduler_resourceitem', (
            ('resourceitem_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['ResourceItem'])

        # Adding model 'Resource'
        db.create_table(u'scheduler_resource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['Resource'])

        # Adding model 'ActItem'
        db.create_table(u'scheduler_actitem', (
            (u'resourceitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceItem'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['ActItem'])

        # Adding model 'ActResource'
        db.create_table(u'scheduler_actresource', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Resource'], unique=True, primary_key=True)),
            ('_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scheduler.ActItem'])),
        ))
        db.send_create_signal(u'scheduler', ['ActResource'])

        # Adding model 'LocationItem'
        db.create_table(u'scheduler_locationitem', (
            (u'resourceitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceItem'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['LocationItem'])

        # Adding model 'Location'
        db.create_table(u'scheduler_location', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Resource'], unique=True, primary_key=True)),
            ('_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scheduler.LocationItem'])),
        ))
        db.send_create_signal(u'scheduler', ['Location'])

        # Adding model 'WorkerItem'
        db.create_table(u'scheduler_workeritem', (
            (u'resourceitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceItem'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['WorkerItem'])

        # Adding model 'Worker'
        db.create_table(u'scheduler_worker', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Resource'], unique=True, primary_key=True)),
            ('_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scheduler.WorkerItem'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'scheduler', ['Worker'])

        # Adding model 'EquipmentItem'
        db.create_table(u'scheduler_equipmentitem', (
            (u'resourceitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceItem'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'scheduler', ['EquipmentItem'])

        # Adding model 'Equipment'
        db.create_table(u'scheduler_equipment', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Resource'], unique=True, primary_key=True)),
            ('_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scheduler.EquipmentItem'])),
        ))
        db.send_create_signal(u'scheduler', ['Equipment'])

        # Adding model 'EventItem'
        db.create_table(u'scheduler_eventitem', (
            ('eventitem_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'scheduler', ['EventItem'])

        # Adding model 'Event'
        db.create_table(u'scheduler_event', (
            (u'schedulable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Schedulable'], unique=True, primary_key=True)),
            ('eventitem', self.gf('django.db.models.fields.related.ForeignKey')(related_name='scheduler_events', to=orm['scheduler.EventItem'])),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('max_volunteer', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'scheduler', ['Event'])

        # Adding model 'ResourceAllocation'
        db.create_table(u'scheduler_resourceallocation', (
            (u'schedulable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.Schedulable'], unique=True, primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources_allocated', to=orm['scheduler.Event'])),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='allocations', to=orm['scheduler.Resource'])),
        ))
        db.send_create_signal(u'scheduler', ['ResourceAllocation'])

        # Adding model 'Ordering'
        db.create_table(u'scheduler_ordering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('allocation', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceAllocation'], unique=True)),
        ))
        db.send_create_signal(u'scheduler', ['Ordering'])

        # Adding model 'Label'
        db.create_table(u'scheduler_label', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
            ('allocation', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ResourceAllocation'], unique=True)),
        ))
        db.send_create_signal(u'scheduler', ['Label'])

        # Adding model 'EventContainer'
        db.create_table(u'scheduler_eventcontainer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent_event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contained_events', to=orm['scheduler.Event'])),
            ('child_event', self.gf('django.db.models.fields.related.OneToOneField')(related_name='container_event', unique=True, to=orm['scheduler.Event'])),
        ))
        db.send_create_signal(u'scheduler', ['EventContainer'])


    def backwards(self, orm):
        # Deleting model 'Schedulable'
        db.delete_table(u'scheduler_schedulable')

        # Deleting model 'ResourceItem'
        db.delete_table(u'scheduler_resourceitem')

        # Deleting model 'Resource'
        db.delete_table(u'scheduler_resource')

        # Deleting model 'ActItem'
        db.delete_table(u'scheduler_actitem')

        # Deleting model 'ActResource'
        db.delete_table(u'scheduler_actresource')

        # Deleting model 'LocationItem'
        db.delete_table(u'scheduler_locationitem')

        # Deleting model 'Location'
        db.delete_table(u'scheduler_location')

        # Deleting model 'WorkerItem'
        db.delete_table(u'scheduler_workeritem')

        # Deleting model 'Worker'
        db.delete_table(u'scheduler_worker')

        # Deleting model 'EquipmentItem'
        db.delete_table(u'scheduler_equipmentitem')

        # Deleting model 'Equipment'
        db.delete_table(u'scheduler_equipment')

        # Deleting model 'EventItem'
        db.delete_table(u'scheduler_eventitem')

        # Deleting model 'Event'
        db.delete_table(u'scheduler_event')

        # Deleting model 'ResourceAllocation'
        db.delete_table(u'scheduler_resourceallocation')

        # Deleting model 'Ordering'
        db.delete_table(u'scheduler_ordering')

        # Deleting model 'Label'
        db.delete_table(u'scheduler_label')

        # Deleting model 'EventContainer'
        db.delete_table(u'scheduler_eventcontainer')


    models = {
        u'scheduler.actitem': {
            'Meta': {'object_name': 'ActItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.actresource': {
            'Meta': {'object_name': 'ActResource', '_ormbases': [u'scheduler.Resource']},
            '_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['scheduler.ActItem']"}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Resource']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.equipment': {
            'Meta': {'object_name': 'Equipment', '_ormbases': [u'scheduler.Resource']},
            '_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['scheduler.EquipmentItem']"}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Resource']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.equipmentitem': {
            'Meta': {'object_name': 'EquipmentItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.event': {
            'Meta': {'object_name': 'Event', '_ormbases': [u'scheduler.Schedulable']},
            'eventitem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scheduler_events'", 'to': u"orm['scheduler.EventItem']"}),
            'max_volunteer': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'schedulable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Schedulable']", 'unique': 'True', 'primary_key': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'})
        },
        u'scheduler.eventcontainer': {
            'Meta': {'object_name': 'EventContainer'},
            'child_event': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'container_event'", 'unique': 'True', 'to': u"orm['scheduler.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contained_events'", 'to': u"orm['scheduler.Event']"})
        },
        u'scheduler.eventitem': {
            'Meta': {'object_name': 'EventItem'},
            'eventitem_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'scheduler.label': {
            'Meta': {'object_name': 'Label'},
            'allocation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceAllocation']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'scheduler.location': {
            'Meta': {'object_name': 'Location', '_ormbases': [u'scheduler.Resource']},
            '_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['scheduler.LocationItem']"}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Resource']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.locationitem': {
            'Meta': {'object_name': 'LocationItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.ordering': {
            'Meta': {'object_name': 'Ordering'},
            'allocation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceAllocation']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'scheduler.resource': {
            'Meta': {'object_name': 'Resource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'scheduler.resourceallocation': {
            'Meta': {'object_name': 'ResourceAllocation', '_ormbases': [u'scheduler.Schedulable']},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources_allocated'", 'to': u"orm['scheduler.Event']"}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations'", 'to': u"orm['scheduler.Resource']"}),
            u'schedulable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Schedulable']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'scheduler.resourceitem': {
            'Meta': {'object_name': 'ResourceItem'},
            'resourceitem_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'scheduler.schedulable': {
            'Meta': {'object_name': 'Schedulable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'scheduler.worker': {
            'Meta': {'object_name': 'Worker', '_ormbases': [u'scheduler.Resource']},
            '_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['scheduler.WorkerItem']"}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.Resource']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'scheduler.workeritem': {
            'Meta': {'object_name': 'WorkerItem', '_ormbases': [u'scheduler.ResourceItem']},
            u'resourceitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.ResourceItem']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['scheduler']