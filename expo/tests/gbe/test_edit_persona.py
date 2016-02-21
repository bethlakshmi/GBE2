import gbe.models as conf
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_persona
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditPersona(TestCase):
    '''Tests for edit_persona view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Stage Persona'

    def test_edit_persona(self):
        '''edit_troupe view, create flow
        '''
        contact = PersonaFactory()
        urlstring = '/persona/edit/%d' % contact.resourceitem_id
        request = self.factory.get(urlstring)
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = edit_persona(request, contact.resourceitem_id)
        nt.assert_equal(response.status_code, 302)
        user = UserFactory()
        login_as(user, self)
        request.user = user
        response = edit_persona(request, contact.resourceitem_id)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        '/profile')
        request.user = contact.performer_profile.user_object
        login_as(contact.performer_profile, self)
        response = edit_persona(request, contact.resourceitem_id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)

    @nt.raises(PermissionDenied)
    def test_wrong_profile(self):
        persona = PersonaFactory()
        viewer = ProfileFactory()
        request = self.factory.get(reverse("persona_edit",
                                           urlconf="gbe.urls",
                                           args=[persona.pk]))
        request.user = viewer.user_object
        login_as(viewer, self)
        request.session = {'cms_admin_site': 1}
        edit_persona(request, persona.pk)
