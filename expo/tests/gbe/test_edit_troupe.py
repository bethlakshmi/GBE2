import nose.tools as nt
from unittest import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    TroupeFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location
    )

# oddly, we can edit troupes even though we can't create them, and we can
# create combos but we can't edit them. This will have to be looked at.


class TestCreateTroupe(TestCase):
    '''Tests for edit_troupe view'''

    view_name = 'troupe_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe_no_performer(self):
        '''edit_troupe view, create flow
        '''
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        expected_loc = 'http://testserver/update_profile?next=/troupe/create'
        nt.assert_equal(location(response), expected_loc)


    def test_create_troupe_performer_exists(self):
        contact = PersonaFactory()
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)


class TestEditTroupe(TestCase):
    view_name = 'troupe_edit'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_no_persona(self):
        profile = ProfileFactory()
        troupe = TroupeFactory()
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        login_as(profile, self)
        response = self.client.get(url)
        expected_loc = 'http://testserver/performer/create?next=/troupe/create'
        nt.assert_equal(expected_loc, location(response))
        self.assertEqual(response.status_code, 302)
