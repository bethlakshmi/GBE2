from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ProfileFactory,
    RoomFactory
)
from scheduler.models import EventContainer
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    StaffAreaContext,
)
from gbe.models import AvailableInterest


class TestEventList(TestCase):
    view_name = 'manage_opps'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        self.avail_interest = AvailableInterestFactory()
        self.room = RoomFactory()

    def get_new_opp_data(self, context):
        data = {
            'create': 'create',
            'new_opp-e_title': 'New Volunteer Opportunity',
            'new_opp-volunteer_type': self.avail_interest.pk,
            'new_opp-num_volunteers': '1',
            'new_opp-duration': '1:00:00',
            'new_opp-day': context.conf_day.pk,
            'new_opp-time': '10:00:00',
            'new_opp-location': self.room.pk}
        return data

    def get_basic_data(self, context):
        data = {
            'e_title': 'Copied Volunteer Opportunity',
            'volunteer_type': self.avail_interest.pk,
            'num_volunteers': '1',
            'duration': '1:00:00',
            'day': context.conf_day.pk,
            'time': '10:00:00',
            'location': self.room.pk}
        return data

    def get_basic_action_data(self, context, vol_opp, action):
        data = self.get_basic_data(context)
        data['title'] = 'Modify Volunteer Opportunity'
        data['opp_event_id'] = vol_opp.eventitem.pk
        data['opp_sched_id'] = vol_opp.pk
        data[action] = action
        return data

    def assert_volunteer_type_selector(self, response, selected_interest=None):
        if selected_interest:
            assert ('<select id="id_volunteer_type" name="volunteer_type">'
                    in response.content)
        else:
            assert ('<select id="id_new_opp-volunteer_type" '
                    'name="new_opp-volunteer_type">') in response.content
        assert '<option value="">---------</option>' in response.content
        for i in AvailableInterest.objects.all():
            if selected_interest and i == selected_interest:
                assert '<option value="%d" selected="selected">%s</option>' % (
                    i.pk, i.interest) in response.content
            elif i.visible:
                assert '<option value="%d">%s</option>' % (
                    i.pk, i.interest) in response.content
            else:
                assert i.interest not in response.content

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
        AvailableInterest.objects.all().delete()
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
        assert "Volunteer Management" in response.content

    def test_good_user_get_w_interest(self):
        context = StaffAreaContext()
        AvailableInterestFactory()
        AvailableInterestFactory(visible=False)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url, follow=True)
        self.assert_volunteer_type_selector(response)

    def test_good_user_get_w_a_volunteer_opp(self):
        context = StaffAreaContext()
        opp = context.add_volunteer_opp(
            room=self.room)
        AvailableInterestFactory()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url, follow=True)
        self.assert_volunteer_type_selector(
            response,
            opp.eventitem.volunteer_type)

    def test_create_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        context = StaffAreaContext()
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.post(
            url,
            data=self.get_new_opp_data(context),
            follow=True)
        assert_redirects(response, reverse('edit_event',
                                           urlconf='scheduler.urls',
                                           args=['GenericEvent',
                                                 context.sched_event.pk]))
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(opps.exists())
        for opp in opps:
            nt.assert_equal(opp.child_event.eventitem.child().e_title,
                            'New Volunteer Opportunity')
            self.assert_volunteer_type_selector(
                response,
                opp.child_event.eventitem.child().volunteer_type)
        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="New Volunteer Opportunity" />',
                     response.content)

    def test_create_opportunity_error(self):
        context = StaffAreaContext()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_new_opp_data(context)
        data['new_opp-num_volunteers'] = ''
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])

        # number of volunteers is missing, it's required
        response = self.client.post(
            url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_false(opps.exists())
        nt.assert_in('<ul class="errorlist"><li>required</li></ul>',
                     response.content)

    def test_copy_opportunity(self):
        context = StaffAreaContext()
        context.add_volunteer_opp(room=self.room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        data = self.get_basic_data(context)
        data['duplicate'] = 'duplicate'
        response = self.client.post(
            url,
            data=data,
            follow=True)
        assert_redirects(response, reverse('edit_event',
                                           urlconf='scheduler.urls',
                                           args=['GenericEvent',
                                                 context.sched_event.pk]))
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(len(opps), 2)
        for opp in opps:
            nt.assert_in(
                '<input id="id_e_title" maxlength="128" '
                'name="e_title" type="text" value="%s" />' % (
                    opp.child_event.eventitem.child().e_title),
                response.content)

    def test_edit_opportunity(self):
        context = StaffAreaContext()
        vol_opp = context.add_volunteer_opp(room=self.room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.post(
            url,
            data=self.get_basic_action_data(context, vol_opp, 'edit'),
            follow=True)
        assert_redirects(response, reverse('edit_event',
                                           urlconf='scheduler.urls',
                                           args=['GenericEvent',
                                                 context.sched_event.pk]))
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(len(opps), 1)
        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="Modify Volunteer Opportunity" />',
                     response.content)

    def test_edit_opportunity_error(self):
        context = StaffAreaContext()
        vol_opp = context.add_volunteer_opp(room=self.room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        data = self.get_basic_action_data(context, vol_opp, 'edit')
        data['num_volunteers'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="Modify Volunteer Opportunity" />',
                     response.content)
        nt.assert_in('<ul class="errorlist"><li>required</li></ul>',
                     response.content)

    def test_delete_opportunity(self):
        context = StaffAreaContext()
        vol_opp = context.add_volunteer_opp(room=self.room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])

        # number of volunteers is missing, it's required
        response = self.client.post(
            url,
            data=self.get_basic_action_data(context, vol_opp, 'delete'),
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_not_in('Modify Volunteer Opportunity',
                         response.content)
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_false(opps.exists())

    def test_allocate_opportunity(self):
        context = StaffAreaContext()
        vol_opp = context.add_volunteer_opp(room=self.room)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])

        # number of volunteers is missing, it's required
        data = self.get_basic_action_data(context, vol_opp, 'allocate')
        data['num_volunteers'] = ''
        response = self.client.post(
            url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_not_in('Modify Volunteer Opportunity',
                         response.content)
        opps = EventContainer.objects.filter(parent_event=context.sched_event)
        nt.assert_true(opps.exists())
        nt.assert_in("Volunteer Allocation", response.content)
