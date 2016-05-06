from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
    RoomFactory
)
from gbe.models import Conference
from scheduler.models import EventContainer

from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)
from tests.factories.scheduler_factories import (
    SchedEventFactory,
)
from tests.contexts import (
    StaffAreaContext,
)


class TestEventList(TestCase):
    view_name = 'manage_opps'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["1"])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["1"])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_not_post(self):
        context = StaffAreaContext()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url, follow=True)
        assert_redirects(response, reverse('edit_event',
                                              urlconf='scheduler.urls',
                                              args=['GenericEvent',
                                                    context.sched_event.pk]))

    def test_create_opportunity(self):
        context = StaffAreaContext()
        room = RoomFactory()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.post(
            url,
            data={'create': 'create',
                  'new_opp-title': 'New Volunteer Opportunity',
                  'new_opp-volunteer_category': 'VA0',
                  'new_opp-num_volunteers': '1',
                  'new_opp-duration': '1:00:00',
                  'new_opp-day': context.conf_day.pk,
                  'new_opp-time': '10:00:00',
                  'new_opp-location': room.pk},
            follow=True)
        assert_redirects(response, reverse('edit_event',
                                              urlconf='scheduler.urls',
                                              args=['GenericEvent',
                                                    context.sched_event.pk]))
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(opps.exists())
        for opp in opps:
            nt.assert_equal(opp.child_event.eventitem.child().title,
                            'New Volunteer Opportunity')
        nt.assert_in('<input id="id_title" maxlength="128" name="title" '+
                     'type="text" value="New Volunteer Opportunity" />',
                     response.content)

    def test_create_opportunity_error(self):
        context = StaffAreaContext()
        room = RoomFactory()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        
        # number of volunteers is missing, it's required
        response = self.client.post(
            url,
            data={'create': 'create',
                  'new_opp-title': 'New Volunteer Opportunity',
                  'new_opp-volunteer_category': 'VA0',
                  'new_opp-num_volunteers': '',
                  'new_opp-duration': '1:00:00',
                  'new_opp-day': context.conf_day.pk,
                  'new_opp-time': '10:00:00',
                  'new_opp-location': room.pk},
            follow=True)
        nt.assert_equal(response.status_code, 200)
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_false(opps.exists())
        nt.assert_in('<ul class="errorlist"><li>required</li></ul>',
                     response.content)

    def test_copy_opportunity(self):
        context = StaffAreaContext()
        room = RoomFactory()
        context.add_volunteer_opp(room=room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        
        # number of volunteers is missing, it's required
        response = self.client.post(
            url,
            data={'duplicate': 'duplicate',
                  'title': 'Copied Volunteer Opportunity',
                  'volunteer_category': 'VA0',
                  'num_volunteers': '1',
                  'duration': '1:00:00',
                  'day': context.conf_day.pk,
                  'time': '10:00:00',
                  'location': room.pk},
            follow=True)
        assert_redirects(response, reverse('edit_event',
                                              urlconf='scheduler.urls',
                                              args=['GenericEvent',
                                                    context.sched_event.pk]))
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(len(opps), 2)
        for opp in opps:
            nt.assert_in('<input id="id_title" maxlength="128" name="title" '+
                        'type="text" value="'+
                        opp.child_event.eventitem.child().title+
                        '" />',
                        response.content)
