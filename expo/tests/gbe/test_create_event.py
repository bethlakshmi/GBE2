import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_event
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
)
from gbe.models import Show


class TestCreateEvent(TestCase):
    '''Tests for create_event view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        current_conference()

    def test_authorized_user_can_access(self):
        request = self.factory.get('create_event/Show')
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = create_event(request, 'Show')
        nt.assert_equal(response.status_code, 200)

    def test_auth_user_can_create_show(self):
        request = self.factory.post('create_event/Show')
        request.user = self.privileged_user
        title = 'The Big Show'
        request.POST['title'] = title
        description = 'Really Big Show'
        request.POST['description'] = description
        duration = '2:00:00'
        request.POST['duration'] = duration
        create_event(request, 'Show')
        nt.assert_true(Show.objects.filter(title=title).count() > 0)

    def test_invalid_form(self):
        request = self.factory.post('create_event/Show')
        request.user = self.privileged_user
        title = 'The Little Show'
        request.POST['title'] = title
        description = 'Really Big Show'
        request.POST['description'] = description
        request.session = {'cms_admin_site': 1}
        duration = '2:00:00'
        create_event(request, 'Show')
        nt.assert_false(Show.objects.filter(title=title).exists())
