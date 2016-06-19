from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)


class TestReviewCostume(TestCase):
    '''Tests for review_costume view'''
    view_name = "costume_review"

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Costume Reviewers')

    def test_review_costume_all_well(self):
        costume = CostumeFactory()
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_costume_past_conference(self):
        conference = ConferenceFactory(status='completed')
        costume = CostumeFactory(b_conference=conference)
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('costume_view',
                    urlconf='gbe.urls',
                    args=[costume.pk]))
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
