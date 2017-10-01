import nose.tools as nt
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import ViewTroupeView
from tests.factories.gbe_factories import (
    TroupeFactory,
    PersonaFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
)


class TestViewTroupe(TestCase):
    '''Tests for view_troupe view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_view_troupe(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')
        login_as(contact.profile.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_no_profile(self):
        troupe = TroupeFactory()
        user = UserFactory()
        url = reverse(
            "troupe_view",
            args=[troupe.resourceitem_id],
            urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        nt.assert_equal(302, response.status_code)

    def test_review_class_no_state_in_profile(self):
        troupe = TroupeFactory()
        troupe.contact.state = ''
        troupe.contact.save()
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')

        login_as(troupe.contact.profile.user_object, self)
        response = self.client.get(url)
        assert 'No State Chosen' in response.content
