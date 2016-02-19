import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from datetime import datetime
import pytz
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from gbe.views import landing_page
from tests.factories.gbe_factories import(
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    CostumeFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
    VolunteerFactory,
)
from scheduler.models import (
    Event,
    ResourceAllocation,
    Worker
)


class TestIndex(TestCase):
    '''Tests for index view'''
    def setUp(self):
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

        #Bid types previous and current
        self.current_act = ActFactory(performer=self.performer,
                                             submitted=True,
                                      conference=self.current_conf)
        self.previous_act = ActFactory(performer=self.performer,
                                              submitted=True,
                                       conference=self.previous_conf)
        self.current_class = ClassFactory(teacher=self.performer,
                                                 submitted=True,
                                                 accepted=3)
        self.current_class.title = "Current Class"
        self.current_class.conference = self.current_conf
        self.current_class.save()
        self.previous_class = ClassFactory(teacher=self.performer,
                                                  submitted=True,
                                                  accepted=3)
        self.previous_class.conference = self.previous_conf
        self.previous_class.title = 'Previous Class'
        self.previous_class.save()

        self.current_vendor = VendorFactory(profile=self.profile,
                                            submitted=True,
                                            conference=self.current_conf)
        self.previous_vendor = VendorFactory(profile=self.profile,
                                                    submitted=True,
                                             conference=self.previous_conf)

        self.current_costume = CostumeFactory(profile=self.profile,
                                                     submitted=True,
                                              conference=self.current_conf)
        self.previous_costume = CostumeFactory(profile=self.profile,
                                                      submitted=True,
                                               conference=self.previous_conf)
        self.current_volunteer = VolunteerFactory(profile=self.profile,
                                                         submitted=True,
                                                  conference=self.current_conf)
        self.previous_volunteer = VolunteerFactory(profile=self.profile,
                                                          submitted=True,
                                                   conference=self.previous_conf)

        # Event assignments, previous and current
        current_opportunity = GenericEventFactory(
            conference=self.current_conf,
            title="Current Volunteering",
            type='Volunteer')
        current_opportunity.save()
        previous_opportunity = GenericEventFactory(
            title="Previous Volunteering",
            conference=self.previous_conf)
        previous_opportunity.save()

        self.current_sched = Event(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 5, 12, 30, 0, 0, tzinfo=pytz.utc),
            max_volunteer=10)
        self.current_sched.save()
        self.previous_sched = Event(
            eventitem=previous_opportunity,
            starttime=datetime(2015, 2, 25, 12, 30, 0, 0, pytz.utc),
            max_volunteer=10)
        self.previous_sched.save()

        self.current_class_sched = Event(
            eventitem=self.current_class,
            starttime=datetime(2016, 2, 5, 2, 30, 0, 0, pytz.utc),
            max_volunteer=10)
        self.current_class_sched.save()
        self.previous_class_sched = Event(
            eventitem=self.previous_class,
            starttime=datetime(2015, 2, 25, 2, 30, 0, 0, pytz.utc),
            max_volunteer=10)
        self.previous_class_sched.save()

        worker = Worker(_item=self.profile, role='Volunteer')
        worker.save()
        for schedule_item in [self.current_sched,
                              self.previous_sched]:
            volunteer_assignment = ResourceAllocation(
                event=schedule_item,
                resource=worker
                )
            volunteer_assignment.save()

        persona_worker = Worker(_item=self.performer, role='Teacher')
        persona_worker.save()
        for schedule_item in [self.current_class_sched,
                              self.previous_class_sched]:
            volunteer_assignment = ResourceAllocation(
                event=schedule_item,
                resource=worker
                )
            volunteer_assignment.save()


    def is_event_present(self, event, content):
        ''' test all parts of the event being on the landing page schedule'''
        return (unicode(event) in content and
                event.start_time.strftime(
                    "%b. %-d, %Y, %-I:%M") in content and
                reverse('detail_view',
                        urlconf="scheduler.urls",
                        args=[event.eventitem.eventitem_id]) in content)

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        request = self.factory.get('/')
        request.user = self.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = landing_page(request)
        self.assertEqual(response.status_code, 200)
        content = response.content
        does_not_show_previous = (
            self.previous_act.title not in content and
            self.previous_class.title not in content and
            self.previous_vendor.title not in content and
            self.previous_costume.title not in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.previous_volunteer.id]) not in content)
        shows_all_current = (
            self.current_act.title in content and
            self.current_class.title in content and
            self.current_vendor.title in content and
            self.current_costume.title in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.current_volunteer.id]) in content)
        nt.assert_true(does_not_show_previous and
                       shows_all_current)
        nt.assert_true(self.is_event_present(self.current_sched, content))
        nt.assert_false(self.is_event_present(self.previous_sched, content))
        nt.assert_true(self.is_event_present(self.current_class_sched, content))
        nt.assert_false(self.is_event_present(self.previous_class_sched, content))

    def test_historical_view(self):
        request = self.factory.get('/')
        request.user = self.profile.user_object
        request.GET = {'historical': 1}
        request.session = {'cms_admin_site': 1}
        response = landing_page(request)
        content = response.content
        self.assertEqual(response.status_code, 200)
        shows_all_previous = (
            self.previous_act.title in content and
            self.previous_class.title in content and
            self.previous_vendor.title in content and
            self.previous_costume.title in content in content)
        does_not_show_current = (
            self.current_act.title not in content and
            self.current_class.title not in content and
            self.current_vendor.title not in content and
            self.current_costume.title not in content)
        nt.assert_true(shows_all_previous and
                       does_not_show_current)
        nt.assert_false(self.is_event_present(self.current_sched, content))
        nt.assert_true(self.is_event_present(self.previous_sched, content))
        nt.assert_false(self.is_event_present(self.current_class_sched, content))
        nt.assert_true(self.is_event_present(self.previous_class_sched, content))
