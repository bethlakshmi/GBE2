from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import SchedEventFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)

from scheduler.models import Event as sEvent


class TestReviewClass(TestCase):
    '''Tests for review_class view'''
    view_name = 'class_review'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Class Reviewers')
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def test_review_class_all_well(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_class_post_form_invalid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data={'accepted': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_class_post_form_valid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        profile = self.privileged_user.profile
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    {'vote': 3,
                                     'notes': "blah blah",
                                     'evaluator': profile.pk,
                                     'bid': klass.pk},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_class_past_conference(self):
        klass = ClassFactory()
        klass.b_conference.status = 'completed'
        klass.b_conference.save()
        url = reverse(self.view_name, args=[klass.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('class_view',
                    urlconf='gbe.urls',
                    args=[klass.pk]))
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        klass = ClassFactory()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, 'Class Reviewers')
        login_as(reviewer, self)
        url = reverse(self.view_name, args=[klass.pk], urlconf="gbe.urls")
        response = self.client.get(url)
        assert "Review Bids" in response.content
        assert response.status_code == 200
