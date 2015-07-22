# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Biddable'
        db.create_table(u'gbe_biddable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('submitted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Biddable'])

        # Adding model 'Profile'
        db.create_table(u'gbe_profile', (
            (u'workeritem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.WorkerItem'], unique=True, primary_key=True)),
            ('user_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('purchase_email', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('best_time', self.gf('django.db.models.fields.CharField')(default='Any', max_length=50, blank=True)),
            ('how_heard', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Profile'])

        # Adding model 'Performer'
        db.create_table(u'gbe_performer', (
            (u'workeritem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.WorkerItem'], unique=True, primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contact', to=orm['gbe.Profile'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('homepage', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('bio', self.gf('django.db.models.fields.TextField')()),
            ('experience', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('awards', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('promo_image', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('festivals', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Performer'])

        # Adding model 'Persona'
        db.create_table(u'gbe_persona', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
            ('performer_profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='personae', to=orm['gbe.Profile'])),
        ))
        db.send_create_signal(u'gbe', ['Persona'])

        # Adding model 'Troupe'
        db.create_table(u'gbe_troupe', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'gbe', ['Troupe'])

        # Adding M2M table for field membership on 'Troupe'
        m2m_table_name = db.shorten_name(u'gbe_troupe_membership')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('troupe', models.ForeignKey(orm[u'gbe.troupe'], null=False)),
            ('persona', models.ForeignKey(orm[u'gbe.persona'], null=False))
        ))
        db.create_unique(m2m_table_name, ['troupe_id', 'persona_id'])

        # Adding model 'Combo'
        db.create_table(u'gbe_combo', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'gbe', ['Combo'])

        # Adding M2M table for field membership on 'Combo'
        m2m_table_name = db.shorten_name(u'gbe_combo_membership')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('combo', models.ForeignKey(orm[u'gbe.combo'], null=False)),
            ('persona', models.ForeignKey(orm[u'gbe.persona'], null=False))
        ))
        db.create_unique(m2m_table_name, ['combo_id', 'persona_id'])

        # Adding model 'AudioInfo'
        db.create_table(u'gbe_audioinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('track_title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('track_artist', self.gf('django.db.models.fields.CharField')(max_length=123, blank=True)),
            ('track', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('track_duration', self.gf('gbe.expomodelfields.DurationField')(blank=True)),
            ('need_mic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('own_mic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('confirm_no_music', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'gbe', ['AudioInfo'])

        # Adding model 'LightingInfo'
        db.create_table(u'gbe_lightinginfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('costume', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['LightingInfo'])

        # Adding model 'StageInfo'
        db.create_table(u'gbe_stageinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('act_duration', self.gf('gbe.expomodelfields.DurationField')(blank=True)),
            ('intro_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('confirm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('set_props', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cue_props', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('clear_props', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['StageInfo'])

        # Adding model 'TechInfo'
        db.create_table(u'gbe_techinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('audio', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.AudioInfo'], unique=True, blank=True)),
            ('lighting', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.LightingInfo'], unique=True, blank=True)),
            ('stage', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.StageInfo'], unique=True, blank=True)),
        ))
        db.send_create_signal(u'gbe', ['TechInfo'])

        # Adding model 'CueInfo'
        db.create_table(u'gbe_cueinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cue_sequence', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('cue_off_of', self.gf('django.db.models.fields.TextField')()),
            ('follow_spot', self.gf('django.db.models.fields.CharField')(default=('White', 'White'), max_length=25)),
            ('center_spot', self.gf('django.db.models.fields.CharField')(default='OFF', max_length=20)),
            ('backlight', self.gf('django.db.models.fields.CharField')(default='OFF', max_length=20)),
            ('cyc_color', self.gf('django.db.models.fields.CharField')(default=('Blue', 'Blue'), max_length=25)),
            ('wash', self.gf('django.db.models.fields.CharField')(default=('White', 'White'), max_length=25)),
            ('sound_note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('techinfo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.TechInfo'])),
        ))
        db.send_create_signal(u'gbe', ['CueInfo'])

        # Adding model 'Act'
        db.create_table(u'gbe_act', (
            (u'actitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ActItem'], unique=True)),
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='acts', null=True, to=orm['gbe.Performer'])),
            ('tech', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.TechInfo'], unique=True, blank=True)),
            ('video_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('video_choice', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('shows_preferences', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('why_you', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Act'])

        # Adding model 'Room'
        db.create_table(u'gbe_room', (
            (u'locationitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.LocationItem'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('overbook_size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'gbe', ['Room'])

        # Adding model 'Event'
        db.create_table(u'gbe_event', (
            (u'eventitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.EventItem'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('blurb', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('duration', self.gf('gbe.expomodelfields.DurationField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('event_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'gbe', ['Event'])

        # Adding model 'Show'
        db.create_table(u'gbe_show', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Event'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'gbe', ['Show'])

        # Adding M2M table for field acts on 'Show'
        m2m_table_name = db.shorten_name(u'gbe_show_acts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('show', models.ForeignKey(orm[u'gbe.show'], null=False)),
            ('act', models.ForeignKey(orm[u'gbe.act'], null=False))
        ))
        db.create_unique(m2m_table_name, ['show_id', 'act_id'])

        # Adding M2M table for field mc on 'Show'
        m2m_table_name = db.shorten_name(u'gbe_show_mc')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('show', models.ForeignKey(orm[u'gbe.show'], null=False)),
            ('persona', models.ForeignKey(orm[u'gbe.persona'], null=False))
        ))
        db.create_unique(m2m_table_name, ['show_id', 'persona_id'])

        # Adding model 'GenericEvent'
        db.create_table(u'gbe_genericevent', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Event'], unique=True, primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Special', max_length=128)),
            ('volunteer_category', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
        ))
        db.send_create_signal(u'gbe', ['GenericEvent'])

        # Adding model 'Class'
        db.create_table(u'gbe_class', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Event'], unique=True)),
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='is_teaching', to=orm['gbe.Persona'])),
            ('minimum_enrollment', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('maximum_enrollment', self.gf('django.db.models.fields.IntegerField')(default=20, blank=True)),
            ('organization', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Lecture', max_length=128, blank=True)),
            ('fee', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('other_teachers', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('length_minutes', self.gf('django.db.models.fields.IntegerField')(default=60, blank=True)),
            ('history', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('run_before', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('schedule_constraints', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('space_needs', self.gf('django.db.models.fields.CharField')(default='Please Choose an Option', max_length=128, blank=True)),
            ('physical_restrictions', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('multiple_run', self.gf('django.db.models.fields.CharField')(default='No', max_length=20)),
        ))
        db.send_create_signal(u'gbe', ['Class'])

        # Adding model 'BidEvaluation'
        db.create_table(u'gbe_bidevaluation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Profile'])),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Biddable'])),
        ))
        db.send_create_signal(u'gbe', ['BidEvaluation'])

        # Adding model 'PerformerFestivals'
        db.create_table(u'gbe_performerfestivals', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('festival', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('experience', self.gf('django.db.models.fields.CharField')(default='No', max_length=20)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Act'])),
        ))
        db.send_create_signal(u'gbe', ['PerformerFestivals'])

        # Adding model 'Volunteer'
        db.create_table(u'gbe_volunteer', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='volunteering', to=orm['gbe.Profile'])),
            ('number_shifts', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('availability', self.gf('django.db.models.fields.TextField')()),
            ('unavailability', self.gf('django.db.models.fields.TextField')()),
            ('interests', self.gf('django.db.models.fields.TextField')()),
            ('opt_outs', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pre_event', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('background', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Volunteer'])

        # Adding model 'Vendor'
        db.create_table(u'gbe_vendor', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Profile'])),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('physical_address', self.gf('django.db.models.fields.TextField')()),
            ('publish_physical_address', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('logo', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('want_help', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('help_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('help_times', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'gbe', ['Vendor'])

        # Adding model 'AdBid'
        db.create_table(u'gbe_adbid', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'gbe', ['AdBid'])

        # Adding model 'ArtBid'
        db.create_table(u'gbe_artbid', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('bio', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('works', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('art1', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('art2', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('art3', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'gbe', ['ArtBid'])

        # Adding model 'ClassProposal'
        db.create_table(u'gbe_classproposal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('proposal', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='Class', max_length=20)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'gbe', ['ClassProposal'])

        # Adding model 'ConferenceVolunteer'
        db.create_table(u'gbe_conferencevolunteer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('presenter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conf_volunteer', to=orm['gbe.Persona'])),
            ('bid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.ClassProposal'])),
            ('how_volunteer', self.gf('django.db.models.fields.CharField')(default='Any of the Above', max_length=20)),
            ('qualification', self.gf('django.db.models.fields.TextField')(blank='True')),
            ('volunteering', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'gbe', ['ConferenceVolunteer'])

        # Adding model 'ProfilePreferences'
        db.create_table(u'gbe_profilepreferences', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='preferences', unique=True, to=orm['gbe.Profile'])),
            ('in_hotel', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('inform_about', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('show_hotel_infobox', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'gbe', ['ProfilePreferences'])


    def backwards(self, orm):
        # Deleting model 'Biddable'
        db.delete_table(u'gbe_biddable')

        # Deleting model 'Profile'
        db.delete_table(u'gbe_profile')

        # Deleting model 'Performer'
        db.delete_table(u'gbe_performer')

        # Deleting model 'Persona'
        db.delete_table(u'gbe_persona')

        # Deleting model 'Troupe'
        db.delete_table(u'gbe_troupe')

        # Removing M2M table for field membership on 'Troupe'
        db.delete_table(db.shorten_name(u'gbe_troupe_membership'))

        # Deleting model 'Combo'
        db.delete_table(u'gbe_combo')

        # Removing M2M table for field membership on 'Combo'
        db.delete_table(db.shorten_name(u'gbe_combo_membership'))

        # Deleting model 'AudioInfo'
        db.delete_table(u'gbe_audioinfo')

        # Deleting model 'LightingInfo'
        db.delete_table(u'gbe_lightinginfo')

        # Deleting model 'StageInfo'
        db.delete_table(u'gbe_stageinfo')

        # Deleting model 'TechInfo'
        db.delete_table(u'gbe_techinfo')

        # Deleting model 'CueInfo'
        db.delete_table(u'gbe_cueinfo')

        # Deleting model 'Act'
        db.delete_table(u'gbe_act')

        # Deleting model 'Room'
        db.delete_table(u'gbe_room')

        # Deleting model 'Event'
        db.delete_table(u'gbe_event')

        # Deleting model 'Show'
        db.delete_table(u'gbe_show')

        # Removing M2M table for field acts on 'Show'
        db.delete_table(db.shorten_name(u'gbe_show_acts'))

        # Removing M2M table for field mc on 'Show'
        db.delete_table(db.shorten_name(u'gbe_show_mc'))

        # Deleting model 'GenericEvent'
        db.delete_table(u'gbe_genericevent')

        # Deleting model 'Class'
        db.delete_table(u'gbe_class')

        # Deleting model 'BidEvaluation'
        db.delete_table(u'gbe_bidevaluation')

        # Deleting model 'PerformerFestivals'
        db.delete_table(u'gbe_performerfestivals')

        # Deleting model 'Volunteer'
        db.delete_table(u'gbe_volunteer')

        # Deleting model 'Vendor'
        db.delete_table(u'gbe_vendor')

        # Deleting model 'AdBid'
        db.delete_table(u'gbe_adbid')

        # Deleting model 'ArtBid'
        db.delete_table(u'gbe_artbid')

        # Deleting model 'ClassProposal'
        db.delete_table(u'gbe_classproposal')

        # Deleting model 'ConferenceVolunteer'
        db.delete_table(u'gbe_conferencevolunteer')

        # Deleting model 'ProfilePreferences'
        db.delete_table(u'gbe_profilepreferences')


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
            'background': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'biddable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['gbe.Biddable']", 'unique': 'True', 'primary_key': 'True'}),
            'interests': ('django.db.models.fields.TextField', [], {}),
            'number_shifts': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'opt_outs': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pre_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'volunteering'", 'to': u"orm['gbe.Profile']"}),
            'unavailability': ('django.db.models.fields.TextField', [], {})
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