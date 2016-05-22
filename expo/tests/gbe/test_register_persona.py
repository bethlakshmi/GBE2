import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    UserFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as,
)


class TestRegisterPersona(TestCase):
    '''Tests for index view'''
    view_name = 'persona_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_register_persona_no_profile(self):
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_register_persona_profile(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_persona_friendly_urls(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        persona_count = profile.personae.count()
        response = self.client.post(
            url,
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': 'persona for %s' % profile.display_name,
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here'
                  })
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(1, profile.personae.count()-persona_count)


    def test_register_persona_invalid_post(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        persona_count = profile.personae.count()
        response = self.client.post(
            url,
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': '',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here'
                  })
        nt.assert_equal(response.status_code, 200)
        assert "This field is required." in response.content




    def test_redirect(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.post(
            url + '?next=/troupe/create',
            data={'performer_profile': profile.pk,
                  'contact': profile.pk,
                  'name': 'persona name',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here',
                  },
            follow=True)
        assert response.status_code == 200
        redirect = ('http://testserver/troupe/create', 302)
        assert redirect in response.redirect_chain
        assert "Tell Us About Your Troupe" in response.content

    def test_get(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')

        response = self.client.get(
            reverse('persona_create', urlconf='gbe.urls'),
        )
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Tell Us About Your Stage Persona" in response.content)
