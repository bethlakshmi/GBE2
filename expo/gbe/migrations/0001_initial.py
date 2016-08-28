# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserMessage'
        db.create_table(u'gbe_usermessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('view', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('gbe', ['UserMessage'])

        # Adding unique constraint on 'UserMessage', fields ['view', 'code']
        db.create_unique(u'gbe_usermessage', ['view', 'code'])

        # Adding model 'AvailableInterest'
        db.create_table(u'gbe_availableinterest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('interest', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gbe', ['AvailableInterest'])

        # Adding model 'Conference'
        db.create_table(u'gbe_conference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('conference_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('conference_slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.CharField')(default='upcoming', max_length=50)),
            ('accepting_bids', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gbe', ['Conference'])

        # Adding model 'Biddable'
        db.create_table(u'gbe_biddable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('b_title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('b_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('submitted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('b_conference', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='b_conference_set', to=orm['gbe.Conference'])),
        ))
        db.send_create_signal('gbe', ['Biddable'])

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
        db.send_create_signal('gbe', ['Profile'])

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
        db.send_create_signal('gbe', ['Performer'])

        # Adding model 'Persona'
        db.create_table(u'gbe_persona', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
            ('performer_profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='personae', to=orm['gbe.Profile'])),
        ))
        db.send_create_signal('gbe', ['Persona'])

        # Adding model 'Troupe'
        db.create_table(u'gbe_troupe', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('gbe', ['Troupe'])

        # Adding M2M table for field membership on 'Troupe'
        m2m_table_name = db.shorten_name(u'gbe_troupe_membership')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('troupe', models.ForeignKey(orm['gbe.troupe'], null=False)),
            ('persona', models.ForeignKey(orm['gbe.persona'], null=False))
        ))
        db.create_unique(m2m_table_name, ['troupe_id', 'persona_id'])

        # Adding model 'Combo'
        db.create_table(u'gbe_combo', (
            (u'performer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Performer'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('gbe', ['Combo'])

        # Adding M2M table for field membership on 'Combo'
        m2m_table_name = db.shorten_name(u'gbe_combo_membership')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('combo', models.ForeignKey(orm['gbe.combo'], null=False)),
            ('persona', models.ForeignKey(orm['gbe.persona'], null=False))
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
        db.send_create_signal('gbe', ['AudioInfo'])

        # Adding model 'LightingInfo'
        db.create_table(u'gbe_lightinginfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('costume', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('specific_needs', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gbe', ['LightingInfo'])

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
        db.send_create_signal('gbe', ['StageInfo'])

        # Adding model 'TechInfo'
        db.create_table(u'gbe_techinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('audio', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.AudioInfo'], unique=True, blank=True)),
            ('lighting', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.LightingInfo'], unique=True, blank=True)),
            ('stage', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.StageInfo'], unique=True, blank=True)),
        ))
        db.send_create_signal('gbe', ['TechInfo'])

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
        db.send_create_signal('gbe', ['CueInfo'])

        # Adding model 'Act'
        db.create_table(u'gbe_act', (
            (u'actitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.ActItem'], unique=True)),
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='acts', null=True, to=orm['gbe.Performer'])),
            ('tech', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.TechInfo'], unique=True, blank=True)),
            ('video_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('video_choice', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('shows_preferences', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('other_performance', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('why_you', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gbe', ['Act'])

        # Adding model 'Room'
        db.create_table(u'gbe_room', (
            (u'locationitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.LocationItem'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('overbook_size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gbe', ['Room'])

        # Adding model 'ConferenceDay'
        db.create_table(u'gbe_conferenceday', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('conference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Conference'])),
        ))
        db.send_create_signal('gbe', ['ConferenceDay'])

        # Adding model 'VolunteerWindow'
        db.create_table(u'gbe_volunteerwindow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.TimeField')(blank=True)),
            ('end', self.gf('django.db.models.fields.TimeField')(blank=True)),
            ('day', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.ConferenceDay'])),
        ))
        db.send_create_signal('gbe', ['VolunteerWindow'])

        # Adding model 'Event'
        db.create_table(u'gbe_event', (
            (u'eventitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scheduler.EventItem'], unique=True)),
            ('e_title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('e_description', self.gf('django.db.models.fields.TextField')()),
            ('blurb', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('duration', self.gf('gbe.expomodelfields.DurationField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('event_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('e_conference', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='e_conference_set', to=orm['gbe.Conference'])),
        ))
        db.send_create_signal('gbe', ['Event'])

        # Adding model 'Show'
        db.create_table(u'gbe_show', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Event'], unique=True, primary_key=True)),
            ('cue_sheet', self.gf('django.db.models.fields.CharField')(default='Theater', max_length=128)),
        ))
        db.send_create_signal('gbe', ['Show'])

        # Adding M2M table for field acts on 'Show'
        m2m_table_name = db.shorten_name(u'gbe_show_acts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('show', models.ForeignKey(orm['gbe.show'], null=False)),
            ('act', models.ForeignKey(orm['gbe.act'], null=False))
        ))
        db.create_unique(m2m_table_name, ['show_id', 'act_id'])

        # Adding M2M table for field mc on 'Show'
        m2m_table_name = db.shorten_name(u'gbe_show_mc')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('show', models.ForeignKey(orm['gbe.show'], null=False)),
            ('persona', models.ForeignKey(orm['gbe.persona'], null=False))
        ))
        db.create_unique(m2m_table_name, ['show_id', 'persona_id'])

        # Adding model 'GenericEvent'
        db.create_table(u'gbe_genericevent', (
            (u'event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Event'], unique=True, primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Special', max_length=128)),
            ('volunteer_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.AvailableInterest'], null=True, blank=True)),
        ))
        db.send_create_signal('gbe', ['GenericEvent'])

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
            ('avoided_constraints', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('space_needs', self.gf('django.db.models.fields.CharField')(default='Please Choose an Option', max_length=128, blank=True)),
            ('physical_restrictions', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('multiple_run', self.gf('django.db.models.fields.CharField')(default='No', max_length=20)),
        ))
        db.send_create_signal('gbe', ['Class'])

        # Adding model 'BidEvaluation'
        db.create_table(u'gbe_bidevaluation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Profile'])),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Biddable'])),
        ))
        db.send_create_signal('gbe', ['BidEvaluation'])

        # Adding model 'PerformerFestivals'
        db.create_table(u'gbe_performerfestivals', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('festival', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('experience', self.gf('django.db.models.fields.CharField')(default='No', max_length=20)),
            ('act', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Act'])),
        ))
        db.send_create_signal('gbe', ['PerformerFestivals'])

        # Adding model 'Volunteer'
        db.create_table(u'gbe_volunteer', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='volunteering', to=orm['gbe.Profile'])),
            ('number_shifts', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('availability', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('unavailability', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('opt_outs', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pre_event', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('background', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gbe', ['Volunteer'])

        # Adding M2M table for field available_windows on 'Volunteer'
        m2m_table_name = db.shorten_name(u'gbe_volunteer_available_windows')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('volunteer', models.ForeignKey(orm['gbe.volunteer'], null=False)),
            ('volunteerwindow', models.ForeignKey(orm['gbe.volunteerwindow'], null=False))
        ))
        db.create_unique(m2m_table_name, ['volunteer_id', 'volunteerwindow_id'])

        # Adding M2M table for field unavailable_windows on 'Volunteer'
        m2m_table_name = db.shorten_name(u'gbe_volunteer_unavailable_windows')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('volunteer', models.ForeignKey(orm['gbe.volunteer'], null=False)),
            ('volunteerwindow', models.ForeignKey(orm['gbe.volunteerwindow'], null=False))
        ))
        db.create_unique(m2m_table_name, ['volunteer_id', 'volunteerwindow_id'])

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
        db.send_create_signal('gbe', ['Vendor'])

        # Adding model 'AdBid'
        db.create_table(u'gbe_adbid', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('gbe', ['AdBid'])

        # Adding model 'ArtBid'
        db.create_table(u'gbe_artbid', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('bio', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('works', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('art1', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('art2', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('art3', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('gbe', ['ArtBid'])

        # Adding model 'Costume'
        db.create_table(u'gbe_costume', (
            (u'biddable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['gbe.Biddable'], unique=True, primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='costumes', to=orm['gbe.Profile'])),
            ('performer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Persona'], null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('act_title', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('debut_date', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('active_use', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('pieces', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('pasties', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dress_size', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('more_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('picture', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('gbe', ['Costume'])

        # Adding model 'ClassProposal'
        db.create_table(u'gbe_classproposal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('proposal', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='Class', max_length=20)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('conference', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['gbe.Conference'])),
        ))
        db.send_create_signal('gbe', ['ClassProposal'])

        # Adding model 'ConferenceVolunteer'
        db.create_table(u'gbe_conferencevolunteer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('presenter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conf_volunteer', to=orm['gbe.Persona'])),
            ('bid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.ClassProposal'])),
            ('how_volunteer', self.gf('django.db.models.fields.CharField')(default='Any of the Above', max_length=20)),
            ('qualification', self.gf('django.db.models.fields.TextField')(blank='True')),
            ('volunteering', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('gbe', ['ConferenceVolunteer'])

        # Adding model 'ProfilePreferences'
        db.create_table(u'gbe_profilepreferences', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='preferences', unique=True, to=orm['gbe.Profile'])),
            ('in_hotel', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('inform_about', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('show_hotel_infobox', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('gbe', ['ProfilePreferences'])

        # Adding model 'VolunteerInterest'
        db.create_table(u'gbe_volunteerinterest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('interest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.AvailableInterest'])),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gbe.Volunteer'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('gbe', ['VolunteerInterest'])

        # Adding unique constraint on 'VolunteerInterest', fields ['interest', 'volunteer']
        db.create_unique(u'gbe_volunteerinterest', ['interest_id', 'volunteer_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'VolunteerInterest', fields ['interest', 'volunteer']
        db.delete_unique(u'gbe_volunteerinterest', ['interest_id', 'volunteer_id'])

        # Removing unique constraint on 'UserMessage', fields ['view', 'code']
        db.delete_unique(u'gbe_usermessage', ['view', 'code'])

        # Deleting model 'UserMessage'
        db.delete_table(u'gbe_usermessage')

        # Deleting model 'AvailableInterest'
        db.delete_table(u'gbe_availableinterest')

        # Deleting model 'Conference'
        db.delete_table(u'gbe_conference')

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

        # Deleting model 'ConferenceDay'
        db.delete_table(u'gbe_conferenceday')

        # Deleting model 'VolunteerWindow'
        db.delete_table(u'gbe_volunteerwindow')

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

        # Removing M2M table for field available_windows on 'Volunteer'
        db.delete_table(db.shorten_name(u'gbe_volunteer_available_windows'))

        # Removing M2M table for field unavailable_windows on 'Volunteer'
        db.delete_table(db.shorten_name(u'gbe_volunteer_unavailable_windows'))

        # Deleting model 'Vendor'
        db.delete_table(u'gbe_vendor')

        # Deleting model 'AdBid'
        db.delete_table(u'gbe_adbid')

        # Deleting model 'ArtBid'
        db.delete_table(u'gbe_artbid')

        # Deleting model 'Costume'
        db.delete_table(u'gbe_costume')

        # Deleting model 'ClassProposal'
        db.delete_table(u'gbe_classproposal')

        # Deleting model 'ConferenceVolunteer'
        db.delete_table(u'gbe_conferencevolunteer')

        # Deleting model 'ProfilePreferences'
        db.delete_table(u'gbe_profilepreferences')

        # Deleting model 'VolunteerInterest'
        db.delete_table(u'gbe_volunteerinterest')


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
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'gbe.biddable': {
            'Meta': {'object_name': 'Biddable'},
            'accepted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'b_conference': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'b_conference_set'", 'to': "orm['gbe.Conference']"}),
            'b_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'b_title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'avoided_constraints': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['gbe.Conference']"}),
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
            'Meta': {'ordering': "['e_title']", 'object_name': 'Event', '_ormbases': [u'scheduler.EventItem']},
            'blurb': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('gbe.expomodelfields.DurationField', [], {}),
            'e_conference': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'e_conference_set'", 'to': "orm['gbe.Conference']"}),
            'e_description': ('django.db.models.fields.TextField', [], {}),
            'e_title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'event_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'eventitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.EventItem']", 'unique': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'gbe.genericevent': {
            'Meta': {'ordering': "['e_title']", 'object_name': 'GenericEvent', '_ormbases': ['gbe.Event']},
            u'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['gbe.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Special'", 'max_length': '128'}),
            'volunteer_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gbe.AvailableInterest']", 'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "['e_title']", 'object_name': 'Show', '_ormbases': ['gbe.Event']},
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
            'rank': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
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