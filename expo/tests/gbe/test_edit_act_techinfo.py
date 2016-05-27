from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory,
    UserFactory,
)
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import (
    login_as,
    is_login_page,
    is_profile_update_page,
    location
)
from scheduler.models import (
    Event as sEvent,
)


class TestEditActTechInfo(TestCase):
    '''Tests for edit_act_techinfo view'''
    view_name = 'act_techinfo_edit'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_full_post(self, rehearsal, techinfo, show):
        data = {
            'show': show.title,
            'rehearsal': str(rehearsal.pk),
            'lighting_info-notes': 'lighting notes',
            'lighting_info-costume': 'costume description',
            'lighting_info-specific_needs': 'lighting specific needs',
            'audio_info-track_title': 'track title',
            'audio_info-track_artist': 'artist',
            'audio_info-track_duration': '00:03:30',
            'audio_info-need_mic': 'checked',
            'audio_info-own_mic': 'checked',
            'audio_info-notes': 'audio notes',
            'audio_info-confirm_no_music': 'checked',
            'stage_info-act_duration': '00:04:10',
            'stage_info-intro_text': 'intro act',
            'stage_info-set_props': 'checked',
            'stage_info-clear_props': 'checked',
            'stage_info-notes': 'notes',
            'stage_info-set_props': 'checked',
            'stage_info-set_props': 'checked',
            'stage_info-set_props': 'checked',
            'cue0-cue_off_of': 'Start of music',
            'cue0-follow_spot': 'Blue',
            'cue0-center_spot': 'ON',
            'cue0-backlight': 'ON',
            'cue0-cyc_color': 'White',
            'cue0-wash': 'Blue',
            'cue0-sound_note': 'sound note',
            'cue0-techinfo': techinfo.pk,
            'cue1-cue_off_of': 'cue note',
            'cue1-follow_spot': 'Pink',
            'cue1-center_spot': 'OFF',
            'cue1-backlight': 'OFF',
            'cue1-cyc_color': 'Green',
            'cue1-wash': 'Green',
            'cue1-sound_note': 'sound note',
            'cue1-techinfo': techinfo.pk,
            'cue2-cue_off_of': 'cue note',
            'cue2-follow_spot': 'Red',
            'cue2-center_spot': 'ON',
            'cue2-backlight': 'ON',
            'cue2-cyc_color': 'Red',
            'cue2-wash': 'Red',
            'cue2-sound_note': 'sound note',
            'cue2-techinfo': techinfo.pk,
        }
        return data

    def test_edit_act_techinfo_unauthorized_user(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Cue Sheet Instructions" in response.content)

    def test_edit_act_techinfo_wrong_profile(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertTrue(400 <= response.status_code < 500)

    def test_edit_act_techinfo_no_profile(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_techinfo_authorized_user_with_rehearsal(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Cue Sheet Instructions" in response.content)

    def test_edit_act_techinfo_authorized_user_post_empty_form(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Cue Sheet Instructions" in response.content)

    def test_edit_act_techinfo_authorized_user_post_complete_form(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        another_rehearsal = context._schedule_rehearsal(context.sched_event)
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.post(
            url,
            data=self.get_full_post(
                another_rehearsal,
                context.act.tech,
                context.show))
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        self.assertEqual(len(context.act.get_scheduled_rehearsals()), 1)
        self.assertEqual(context.act.get_scheduled_rehearsals()[0],
                         another_rehearsal)
