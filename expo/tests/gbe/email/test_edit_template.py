from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    EmailTemplateSenderFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.show_context import ShowContext
from django.conf import settings


class TestEventList(TestCase):
    view_name = 'edit_template'

    def setUp(self):
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        self.sender = EmailTemplateSenderFactory(
            from_email="volunteeremail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template"
        )
        self.url = reverse(self.view_name,
                           args=[self.sender.template.name],
                           urlconf="gbe.email.urls")

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s/?next=/email/edit_template/%s" % (
            reverse('login', urlconf='gbe.urls'),
            "volunteer%2520schedule%2520update")
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_volunteer_schedule_update_exists_w_get(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)

        self.assertContains(response, self.sender.from_email)
        self.assertContains(response, self.sender.template.subject)
        self.assertContains(response, self.sender.template.html_content)

    def test_act_accept_not_exists_w_get(self):
        context = ShowContext()
        grant_privilege(self.privileged_profile.user_object,
                        'Act Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf="gbe.email.urls",
                    args=["act accepted - %s" % context.show.e_title.lower()]))

        self.assertContains(response, settings.DEFAULT_FROM_EMAIL)
        self.assertContains(response, 'Your act has been cast in %s' % (
            context.show.e_title))
        self.assertContains(
            response,
            'Be sure to fill out your Act Tech Info Page ASAP')
