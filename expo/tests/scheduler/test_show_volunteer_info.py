from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.functions.scheduler_functions import (
    assert_link,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import AvailableInterest

'''
#
#  This is a spin off of edit event, or manage volunteer opportunities.
#    It's the testing for the case of presenting eligible volunteers on an
#    event that is a volunteer opportunity.  Not testing the basics, as they
#    are covered elsewhere (ie, privileges and basic bad data)
#
'''
class TestShowVolunteers(TestCase):
    view_name = 'edit_event'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.context = VolunteerContext()
        self.url = reverse(
            self.view_name,
            args=["GenericEvent", self.context.opp_event.pk],
            urlconf="scheduler.urls")

    def test_no_available_volunteers(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        volunteer, alloc = context.book_volunteer(
        volunteer_opp)
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                args=["GenericEvent", volunteer_opp.pk],
            urlconf="scheduler.urls"),
            follow=True)
        assert ("no available volunteers" in response.content)

    def test_volunteer_has_conflict(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        print response.content
        assert ("no available volunteers" not in response.content)
        assert_link(response, self.url)

    def test_volunteer_is_available(self):
        self.context.bid.available_windows.add(self.context.window)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" not in response.content)
        assert('<td class="bid-table">Available</td>' in response.content)

    def test_volunteer_is_not_available(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" not in response.content)
        assert('<td class="bid-table">Not Available</td>' in response.content)

    def test_volunteer_is_really_not_available(self):
        self.context.bid.unavailable_windows.add(self.context.window)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" in response.content)

    def test_volunteer_is_interested(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert('4 - Somewhat interested' in response.content)

    def test_volunteer_is_not(self):
        self.context.interest.rank = 0
        self.context.interest.save()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert('4 - Somewhat interested' not in response.content)
        assert ("no available volunteers" not in response.content)
