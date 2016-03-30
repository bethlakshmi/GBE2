from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client


from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    ProfileFactory,
)
from gbe.models import (
    Act,
    Conference,
)
from tests.functions.gbe_functions import login_as

class TestCloneBid(TestCase):
    view_name = 'clone_bid'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()


    def test_clone_bid_succeed(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()

        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Act',
                              'bid_id': bid.id})
        login_as(bid.performer.contact, self)

        response = self.client.get(url)
        nt.assert_true(Act.objects.filter(
            title=bid.title,
            conference=current_conference).exists())

    def test_clone_bid_bad_bid_type(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Steakknife',
                              'bid_id': bid.id})
        login_as(bid.performer.contact, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 404)

    def test_clone_bid_wrong_user(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Act',
                              'bid_id': bid.id})
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)
