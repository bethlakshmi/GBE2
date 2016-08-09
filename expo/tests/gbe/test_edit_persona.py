from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from gbe.models import Persona
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
    view_name = 'persona_edit'

    '''Tests for edit_persona view'''
    def setUp(self):
        self.client = Client()
        self.expected_string = 'Tell Us About Your Stage Persona'

    def test_edit_persona(self):
        '''edit_troupe view, create flow
        '''
        contact = PersonaFactory()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[contact.resourceitem_id])
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        'http://testserver/profile')
        login_as(contact.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.expected_string in response.content)

    def test_wrong_profile(self):
        persona = PersonaFactory()
        viewer = ProfileFactory()
        url = (reverse(self.view_name,
                       urlconf="gbe.urls",
                       args=[persona.pk]))
        login_as(viewer, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_edit_persona_change_stage_name(self):
        persona = PersonaFactory()
        login_as(persona.performer_profile, self)
        old_name = persona.name
        new_name = "Fifi"
        urlstring = '/persona/edit/%d' % persona.resourceitem_id
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[persona.resourceitem_id])
        response = self.client.post(
            url,
            data={'performer_profile': persona.performer_profile.pk,
                  'contact': persona.performer_profile.pk,
                  'name': new_name,
                  'homepage': persona.homepage,
                  'bio': "bio",
                  'experience': 1,
                  'awards': "many"}
        )
        persona_reloaded = Persona.objects.get(pk=persona.pk)
        nt.assert_equal(persona_reloaded.name, new_name)

    def test_edit_persona_invalid_post(self):
        persona = PersonaFactory()
        login_as(persona.performer_profile, self)
        old_name = persona.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[persona.resourceitem_id])
        response = self.client.post(
            url,
            data={'performer_profile': persona.pk,
                  'contact': persona.pk,
                  'name': new_name,
                  'homepage': persona.homepage,
                  'bio': "bio",
                  'experience': 1,
                  'awards': "many"}
        )
        nt.assert_true(self.expected_string in response.content)
        persona_reloaded = Persona.objects.get(pk=persona.pk)
        nt.assert_equal(persona_reloaded.name, old_name)
