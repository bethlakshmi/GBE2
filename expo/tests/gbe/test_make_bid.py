from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    UserFactory
)
from tests.functions.gbe_functions import login_as
from gbe.models import (
    Conference,
)


class TestMakeBid(TestCase):
    '''Tests for the centralized make bid view'''
    view_name = 'class_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.conference = ConferenceFactory(accepting_bids=True)

    def test_bid_no_profile(self):
        '''act_bid, when user has no profile, should bounce out to /profile'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        user = UserFactory()
        login_as(user, self)
        response = self.client.get(url, )
        self.assertRedirects(
            response,
            '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                reverse('class_create', urlconf='gbe.urls')))

    def test_get_new_bid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.conference.conference_name in response.content)
