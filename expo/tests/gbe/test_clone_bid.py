import gbe.models as conf
from django.core.exceptions import PermissionDenied
from django.http import Http404

from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import clone_bid

from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    ProfileFactory,
)
from gbe.models import (
    Act,
    Conference,
)

class TestCloneBid(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.urlstring = 'clone_bid'

    def test_clone_bid_succeed(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()
        request = self.factory.get(self.urlstring,
                                   urlconf="gbe.urls",
                                   args=('Act', bid.id))
        request.session = {'cms_admin_site': 1}
        request.user = bid.performer.contact.user_object

        response = clone_bid(request, 'Act', bid.id)
        nt.assert_true(Act.objects.filter(
            title=bid.title,
            conference=current_conference).exists())

    @nt.raises(Http404)
    def test_clone_bid_bad_bid_type(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()
        request = self.factory.get(self.urlstring,
                                   urlconf="gbe.urls",
                                   args=('Act', bid.id))
        request.session = {'cms_admin_site': 1}
        request.user = bid.performer.contact.user_object
        response = clone_bid(request, 'Show', bid.id)

    @nt.raises(PermissionDenied)
    def test_clone_bid_wrong_user(self):
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ActFactory(conference=old_conference)
        Act.objects.filter(title=bid.title,
                           conference=current_conference).delete()
        request = self.factory.get(self.urlstring,
                                   urlconf="gbe.urls",
                                   args=('Act', bid.id))
        request.session = {'cms_admin_site': 1}
        request.user = ProfileFactory().user_object
        response = clone_bid(request, 'Act', bid.id)
