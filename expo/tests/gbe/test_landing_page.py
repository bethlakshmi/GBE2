import nose.tools as nt
from django.test import TestCase
from datetime import datetime
import pytz
from django.test import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import(
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    CostumeFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VendorFactory,
    VolunteerFactory,
)
from tests.factories.scheduler_factories import (
    SchedEventFactory,
    ResourceAllocationFactory,
    WorkerFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from unittest import skip

class TestIndex(TestCase):
    '''Tests for index view'''
    view_name = 'home'

    def setUp(self):
        self.client = Client()
        # Conference Setup
        self.factory = RequestFactory()
        self.current_conf = ConferenceFactory(accepting_bids=True,
                                              status='upcoming')
        self.previous_conf = ConferenceFactory(accepting_bids=False,
                                               status='completed')

        # User/Human setup
        self.profile = ProfileFactory()
        self.performer = PersonaFactory(performer_profile=self.profile,
                                        contact=self.profile)
        # Bid types previous and current
        self.current_act = ActFactory(performer=self.performer,
                                      submitted=True,
                                      b_conference=self.current_conf)
        self.previous_act = ActFactory(performer=self.performer,
                                       submitted=True,
                                       b_conference=self.previous_conf)
        self.current_class = ClassFactory(teacher=self.performer,
                                          submitted=True,
                                          accepted=3,
                                          b_conference=self.current_conf,
                                          e_conference=self.current_conf)
        self.previous_class = ClassFactory(teacher=self.performer,
                                           submitted=True,
                                           accepted=3,
                                           b_conference=self.previous_conf,
                                           e_conference= self.previous_conf)

        self.current_vendor = VendorFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_vendor = VendorFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)

        self.current_costume = CostumeFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_costume = CostumeFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)
        self.current_volunteer = VolunteerFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_volunteer = VolunteerFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)

        # Event assignments, previous and current
        current_opportunity = GenericEventFactory(
            e_conference=self.current_conf,
            type='Volunteer')
        previous_opportunity = GenericEventFactory(
            e_conference=self.previous_conf)

        self.current_sched = SchedEventFactory(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 5, 12, 30, 0, 0, pytz.utc),
            max_volunteer=10)
        self.previous_sched = SchedEventFactory(
            eventitem=previous_opportunity,
            starttime=datetime(2015, 2, 25, 12, 30, 0, 0, pytz.utc),
            max_volunteer=10)

        self.current_class_sched = SchedEventFactory(
            eventitem=self.current_class,
            starttime=datetime(2016, 2, 5, 2, 30, 0, 0, pytz.utc),
            max_volunteer=10)
        self.previous_class_sched = SchedEventFactory(
            eventitem=self.previous_class,
            starttime=datetime(2015, 2, 25, 2, 30, 0, 0, pytz.utc),
            max_volunteer=10)

        worker = WorkerFactory(_item=self.profile, role='Volunteer')
        for schedule_item in [self.current_sched,
                              self.previous_sched]:
            volunteer_assignment = ResourceAllocationFactory(
                event=schedule_item,
                resource=worker
                )

        persona_worker = WorkerFactory(_item=self.performer,
                                       role='Teacher')
        for schedule_item in [self.current_class_sched,
                              self.previous_class_sched]:
            volunteer_assignment = ResourceAllocationFactory(
                event=schedule_item,
                resource=worker
                )

    def is_event_present(self, event, content):
        ''' test all parts of the event being on the landing page schedule'''
        return (unicode(event) in content and
                event.start_time.strftime(
                    "%b. %-d, %Y, %-I:%M") in content and
                reverse('detail_view',
                        urlconf="scheduler.urls",
                        args=[event.eventitem.eventitem_id]) in content)

    def test_no_profile(self):
        url = reverse('home', urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_true("Your Expo" in response.content)

    @skip
    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        import pdb; pdb.set_trace()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content
        does_not_show_previous = (
            self.previous_act.b_title not in content and
            self.previous_class.b_title not in content and
            self.previous_vendor.b_title not in content and
            self.previous_costume.b_title not in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.previous_volunteer.id]) not in content)
        shows_all_current = (
            self.current_act.b_title in content and
            self.current_class.b_title in content and
            self.current_vendor.b_title in content and
            self.current_costume.b_title in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.current_volunteer.id]) in content)
        assert does_not_show_previous
        assert shows_all_current
        nt.assert_true(self.is_event_present(self.current_sched, content))
        nt.assert_false(self.is_event_present(self.previous_sched, content))
        nt.assert_true(self.is_event_present(
            self.current_class_sched, content))
        nt.assert_false(self.is_event_present(
            self.previous_class_sched, content))
    @skip
    def test_historical_view(self):
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(
            url,
            data={'historical': 1})
        content = response.content
        self.assertEqual(response.status_code, 200)
        shows_all_previous = (
            self.previous_act.b_title in content and
            self.previous_class.b_title in content and
            self.previous_vendor.b_title in content and
            self.previous_costume.b_title in content in content)
        does_not_show_current = (
            self.current_act.b_title not in content and
            self.current_class.b_title not in content and
            self.current_vendor.b_title not in content and
            self.current_costume.b_title not in content)
        nt.assert_true(shows_all_previous and
                       does_not_show_current)
        nt.assert_false(self.is_event_present(self.current_sched, content))
        nt.assert_true(self.is_event_present(self.previous_sched, content))
        nt.assert_false(self.is_event_present(
            self.current_class_sched, content))
        nt.assert_true(self.is_event_present(
            self.previous_class_sched, content))

    def test_as_privileged_user(self):
        staff_profile = ProfileFactory()
        grant_privilege(staff_profile, "Ticketing - Admin")
        login_as(staff_profile, self)
        url = reverse('admin_landing_page', urlconf='gbe.urls',
                      args=[staff_profile.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        nt.assert_true("You are viewing a" in response.content)

    def test_acts_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Act Reviewers")
        login_as(staff_profile, self)
        act = ActFactory(submitted=True,
                         b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(act.b_title in response.content)

    def test_classes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Class Reviewers")
        login_as(staff_profile, self)
        klass = ClassFactory(submitted=True,
                             b_conference=self.current_conf,
                             e_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(klass.b_title in response.content)

    def test_volunteers_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Volunteer Reviewers")
        login_as(staff_profile, self)
        volunteer = VolunteerFactory(submitted=True,
                                     b_conference=self.current_conf)

        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(volunteer.b_title in response.content)

    def test_vendors_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Vendor Reviewers")
        login_as(staff_profile, self)
        vendor = VendorFactory(submitted=True,
                               b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)

        nt.assert_true(vendor.b_title in response.content)

    def test_costumes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Costume Reviewers")
        login_as(staff_profile, self)
        costume = CostumeFactory(submitted=True,
                                 b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)

        nt.assert_true(costume.b_title in response.content)
