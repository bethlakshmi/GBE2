from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import submit_act
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
)
from gbe.models import Act


class TestSubmitAct(TestCase):
    '''Tests for submit_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_submit_act(self):
        act = ActFactory()
        request = self.factory.get('act/submit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        response = submit_act(request, act.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(Http404)
    def test_submit_act_does_not_exist(self):
        Act.objects.all().delete()
        request = self.factory.get('act/submit/%d' % 1)
        request.user = ProfileFactory().user_object
        response = submit_act(request, 1)

    def test_submit_act_not_owner(self):
        act = ActFactory()
        request = self.factory.get('act/submit/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = ProfileFactory().user_object
        response = submit_act(request, act.pk)
        error_string = "Error: You don&#39;t own that act."
        nt.assert_true(error_string in response.content)
