import nose.tools as nt
from django.core.urlresolvers import reverse
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    ActFactory,
)
from tests.functions.gbe_functions import login_as

class TestViewAct(TestCase):
    '''Tests for view_act view'''
    view_name = 'act_view'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def test_view_act_all_well(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)
