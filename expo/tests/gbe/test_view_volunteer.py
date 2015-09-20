import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_volunteer
from tests.factories import gbe_factories as factories
import mock
import gbe.ticketing_idd_interface


class TestViewVolunteer(TestCase):
    '''Tests for view_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def test_view_act_all_well(self):
        volunteer = factories.VolunteerFactory.create()
        request = self.factory.get('volunteer/view/%d' % volunteer.pk)
        request.user = volunteer.profile.user_object
        request.session = {'cms_admin_site':1}
        response = view_volunteer(request, volunteer.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)
