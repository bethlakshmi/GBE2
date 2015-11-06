import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from gbe.views import register_persona
from tests.factories import gbe_factories as factories


class TestRegisterPersona(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.user_factory = factories.UserFactory

    def test_register_persona(self):
        '''register_persona view should load and return:
        302 if user but no profile
        200 if profile but no form
        302 if profile and valid form - need to write this
        '''
        request = self.factory.get('/')
        request.session = {'cms_admin_site': 1}
        user = factories.UserFactory.create()
        request.user = user
        response = register_persona(request)
        self.assertEqual(response.status_code, 302)
        profile = factories.ProfileFactory.create()
        request.user = profile.user_object
        request.method = 'POST'
        response = register_persona(request)
        self.assertEqual(response.status_code, 200)

    def test_register_persona_friendly_urls(self):
        profile = factories.ProfileFactory.create()
        request = self.factory.post(
            reverse('persona_create', urlconf='gbe.urls'),
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': 'persona name',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here'
                  })
        request.session = {'cms_admin_site': 1}
        request.user = profile.user_object
        response = register_persona(request)
        nt.assert_equal(response.status_code, 302)
