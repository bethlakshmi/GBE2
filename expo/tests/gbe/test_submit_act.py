from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import submit_act
import mock
from django.contrib.auth.models import Group
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)


class TestSubmitAct(TestCase):
    '''Tests for submit_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_submit_act(self):
        act = factories.ActFactory.create()
        request = self.factory.get('act/submit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        response = submit_act(request, act.pk)
        nt.assert_equal(response.status_code, 302)
