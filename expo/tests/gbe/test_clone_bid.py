from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase
from django.test import Client

from tests.factories.gbe_factories import (
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
)
from gbe.models import (
    Act,
    Class,
    Conference,
)
from tests.functions.gbe_functions import (
    clear_conferences,
    login_as,
)


class TestCloneBid(TestCase):
    view_name = 'clone_bid'

    def setUp(self):
        self.client = Client()

    def test_clone_act_succeed(self):
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

    # following test fails, not sure why.
    # ClassFactory creates an instance of gbe.Class w/o data,
    # which doesn't seem to persist to the db

    def test_clone_class_succeed(self):
        clear_conferences()
        Conference.objects.all().delete()
        old_conference = ConferenceFactory(status="completed",
                                           accepting_bids=False)
        current_conference = ConferenceFactory(status="upcoming",
                                               accepting_bids=True)
        bid = ClassFactory(conference=old_conference)
        bid.title = "Factory is broken"
        bid.save()
        count = Class.objects.filter(
            title=bid.title,
            conference=current_conference).count()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Class',
                              'bid_id': bid.id})
        login_as(bid.teacher.contact, self)

        response = self.client.get(url)
        nt.assert_equal(
            1 + count,
            Class.objects.filter(title=bid.title,
                                 conference=current_conference).count())

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
