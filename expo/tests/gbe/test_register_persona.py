import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from gbe.views import register_persona
from tests.factories.gbe_factories import (
    UserFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    location,
)

class TestRegisterPersona(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.user_factory = UserFactory

    def test_register_persona(self):
        '''register_persona view should load and return:
        302 if user but no profile
        200 if profile but no form
        302 if profile and valid form - need to write this
        '''
        request = self.factory.get('/')
        request.session = {'cms_admin_site': 1}
        user = UserFactory.create()
        request.user = user
        response = register_persona(request)
        self.assertEqual(response.status_code, 302)
        profile = ProfileFactory.create()
        request.user = profile.user_object
        request.method = 'POST'
        response = register_persona(request)
        self.assertEqual(response.status_code, 200)

    def test_register_persona_friendly_urls(self):
        profile = ProfileFactory.create()
        persona_count = profile.personae.count()
        request = self.factory.post(
            reverse('persona_create', urlconf='gbe.urls'),
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': 'persona for %s' % profile.display_name,
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here'
                  })
        request.session = {'cms_admin_site': 1}
        request.user = profile.user_object
        response = register_persona(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(1, profile.personae.count()-persona_count)

    def test_redirect(self):
        profile = ProfileFactory.create()
        request = self.factory.post(
            'performer/create?next=/combo/create',
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': 'persona name',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here',
                  },
            follow=True)
        request.session = {'cms_admin_site': 1}
        request.user = profile.user_object
        response = register_persona(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/combo/create')


    def test_get(self):
        profile = ProfileFactory.create()
        request = self.factory.get(
            reverse('persona_create', urlconf='gbe.urls'),
        )
        request.session = {'cms_admin_site': 1}
        request.user = profile.user_object
        response = register_persona(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Tell Us About Your Stage Persona" in response.content)
