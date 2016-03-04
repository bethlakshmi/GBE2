import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_troupe
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

class TestEditTroupe(TestCase):
    '''Tests for edit_troupe view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe(self):
        '''edit_troupe view, create flow
        '''
        contact = PersonaFactory.create()
        request = self.factory.get('/troupe/create/')
        request.user = UserFactory.create()
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 302)

        user = UserFactory.create()
        login_as(user, self)
        request.user = user
        response = edit_troupe(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        '/update_profile?next=/troupe/create')
        request.user = contact.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        login_as(contact.performer_profile, self)
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)

    def test_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory.create()
        contact = persona.performer_profile
        troupe = TroupeFactory.create(contact=contact)
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        request.user = contact.profile.user_object
        request.session = {'cms_admin_site':1}
        self.client.logout()
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 200)

    def test_no_persona(self):
        profile = ProfileFactory.create()
        troupe = TroupeFactory()
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        request.user = profile.user_object
        login_as(profile, self)
        request.session = {'cms_admin_site': 1}
        response = edit_troupe(request)
        nt.assert_equal('/performer/create?next=/troupe/create',
                        location(response))
        self.assertEqual(response.status_code, 302)


    def test_no_persona(self):
        profile = ProfileFactory.create()
        troupe = TroupeFactory()
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        request.user = profile.user_object
        login_as(profile, self)
        request.session = {'cms_admin_site': 1}
        response = edit_troupe(request)
        nt.assert_equal('/performer/create?next=/troupe/create',
                        location(response))
        self.assertEqual(response.status_code, 302)
