import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_act
import mock
import gbe.ticketing_idd_interface 
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestViewAct(TestCase):
    '''Tests for view_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def test_view_act_all_well(self):
        act = factories.ActFactory.create()
        request = self.factory.get('act/view/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        response = view_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Submitted proposals cannot be modified' in response.content)
