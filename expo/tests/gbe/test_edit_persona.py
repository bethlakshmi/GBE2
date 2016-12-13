from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from gbe.models import Persona
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
)
from gbetext import default_edit_persona_msg
from gbe.models import UserMessage


class TestEditPersona(TestCase):
    view_name = 'persona_edit'

    '''Tests for edit_persona view'''
    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.expected_string = 'Tell Us About Your Stage Persona'
        self.persona = PersonaFactory()

    def submit_persona(self):
        login_as(self.persona.performer_profile, self)
        old_name = self.persona.name
        new_name = "Fifi"
        urlstring = '/persona/edit/%d' % self.persona.resourceitem_id
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id])
        response = self.client.post(
            url,
            data={'performer_profile': self.persona.performer_profile.pk,
                  'contact': self.persona.performer_profile.pk,
                  'name': new_name,
                  'homepage': self.persona.homepage,
                  'bio': "bio",
                  'experience': 1,
                  'awards': "many"},
            follow=True
        )
        return response, new_name

    def test_edit_persona(self):
        '''edit_troupe view, create flow
        '''
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id])
        login_as(UserFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(location(response),
                         'http://testserver/profile')
        login_as(self.persona.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.expected_string in response.content)

    def test_wrong_profile(self):
        viewer = ProfileFactory()
        url = (reverse(self.view_name,
                       urlconf="gbe.urls",
                       args=[self.persona.pk]))
        login_as(viewer, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_edit_persona_change_stage_name(self):
        response, new_name = self.submit_persona()
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.name, new_name)

    def test_edit_persona_invalid_post(self):
        login_as(self.persona.performer_profile, self)
        old_name = self.persona.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id])
        response = self.client.post(
            url,
            data={'performer_profile': self.persona.pk,
                  'contact': self.persona.pk,
                  'name': new_name,
                  'homepage': self.persona.homepage,
                  'bio': "bio",
                  'experience': 1,
                  'awards': "many"}
        )
        self.assertTrue(self.expected_string in response.content)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.name, old_name)

    def test_edit_persona_make_message(self):
        response, new_name = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', default_edit_persona_msg)

    def test_edit_persona_has_message(self):
        msg = UserMessageFactory(
            view='EditPersonaView',
            code='UPDATE_PERSONA')
        response, new_name = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
