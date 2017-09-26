from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.class_context import ClassContext
from gbetext import acceptance_states

class TestMailToBidder(TestCase):
    view_name = 'mail_to_bidders'
    priv_list = ['Act', 'Class', 'Costume', 'Vendor', 'Volunteer']

    def setUp(self):
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        for priv in self.priv_list:
            grant_privilege(
                self.privileged_profile.user_object,
                '%s Coordinator' % priv)
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")

    def reduced_login(self):
        reduced_profile = ProfileFactory()
        grant_privilege(
            reduced_profile.user_object,
            '%s Coordinator' % "Act")
        login_as(reduced_profile, self)
        return reduced_profile
    
    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s/?next=/email/mail_to_bidders" % (
            reverse('login', urlconf='gbe.urls'))
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="" selected="selected">All</option>',
            3)
        for priv in self.priv_list:
            self.assertContains(
                response,
                '<option value="%s">%s</option>' % (priv, priv))
        for state in acceptance_states:
            self.assertContains(
                response,
                '<option value="%s">%s</option>' % (state[0], state[1]))

    def test_reduced_login_first_get(self):
        self.reduced_login()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="" selected="selected">All</option>',
            3)
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % ("Act", "Act"))

    def test_full_login_first_get_2_conf(self):
        extra_conf = ConferenceFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                self.context.conference.pk,
                self.context.conference.conference_name))
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                extra_conf.pk,
                extra_conf.conference_name))
