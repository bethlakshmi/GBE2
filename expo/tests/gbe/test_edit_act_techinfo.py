from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
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

    def test_edit_act_techinfo_unauthorized_user(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Cue Sheet Instructions" in response.content)

    def test_edit_act_techinfo_wrong_profile(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_true(400 <= response.status_code < 500)

    def test_edit_act_techinfo_no_profile(self):
        context = ActTechInfoContext()
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 404)

    def test_edit_act_techinfo_authorized_user_with_rehearsal(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Cue Sheet Instructions" in response.content)

    def test_edit_act_techinfo_authorized_user_post_empty_form(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse('act_techinfo_edit',
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.post(url, {})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Cue Sheet Instructions" in response.content)
