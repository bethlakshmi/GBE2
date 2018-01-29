from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ProfileFactory,
)
from scheduler.models import (
    EventContainer,
    EventLabel,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    VolunteerContext,
)
from gbe.models import AvailableInterest
from django.utils.formats import date_format


class TestManageVolunteerOpportunity(TestCase):
    view_name = 'manage_opps'

    def setUp(self):
        AvailableInterest.objects.all().delete()
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        self.avail_interest = AvailableInterestFactory()
        self.context = VolunteerContext()
        self.room = self.context.room
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.sched_event.eventitem.event.__class__.__name__,
                  self.context.sched_event.eventitem.eventitem_id,
                  self.context.sched_event.pk])

    def get_new_opp_data(self, context):
        data = {
            'create': 'create',
            'new_opp-e_title': 'New Volunteer Opportunity',
            'new_opp-volunteer_type': self.avail_interest.pk,
            'new_opp-type': "Volunteer",
            'new_opp-max_volunteer': '1',
            'new_opp-duration': '1:00:00',
            'new_opp-day': context.conf_day.pk,
            'new_opp-time': '10:00:00',
            'new_opp-location': self.room.pk}
        return data

    def get_basic_data(self, context):
        data = {
            'e_title': 'Copied Volunteer Opportunity',
            'volunteer_type': self.avail_interest.pk,
            'type': 'Volunteer',
            'max_volunteer': '1',
            'duration': '1:00:00',
            'day': context.conf_day.pk,
            'time': '10:00:00',
            'location': self.room.pk}
        return data

    def get_basic_action_data(self, context, vol_opp, action):
        data = self.get_basic_data(context)
        data['e_title'] = 'Modify Volunteer Opportunity'
        data['opp_event_id'] = vol_opp.eventitem.child().pk
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
                      urlconf="gbe.scheduling.urls",
                      args=["Show", "1", "1"])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Show", "1", "1"])
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_not_post(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_redirects(
            response,
            reverse('edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=['Show',
                          self.context.sched_event.eventitem.eventitem_id,
                          self.context.sched_event.pk]))
        assert "Volunteer Management" in response.content

    def test_good_user_get_w_interest(self):
        AvailableInterestFactory()
        AvailableInterestFactory(visible=False)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assert_volunteer_type_selector(response)

    def test_good_user_get_w_a_volunteer_opp(self):
        x, opp = self.context.add_opportunity()
        AvailableInterestFactory()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assert_volunteer_type_selector(
            response,
            opp.eventitem.child().volunteer_type)
        sched_day = date_format(
            self.context.sched_event.start_time, "DATE_FORMAT")
        expected_string = 'selected="selected">%s</option>' % sched_day
        self.assertContains(response, expected_string)

    def test_create_opportunity(self):
        orig_opp = self.context.opp_event
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event
            ).exclude(child_event=orig_opp)
        nt.assert_true(opps.exists())
        for opp in opps:
            nt.assert_equal(opp.child_event.eventitem.child().e_title,
                            'New Volunteer Opportunity')
            self.assert_volunteer_type_selector(
                response,
                opp.child_event.eventitem.child().volunteer_type)
            assert_redirects(response, "%s?changed_id=%d" % (
                reverse('edit_event_schedule',
                        urlconf='gbe.scheduling.urls',
                        args=['Show',
                              self.context.sched_event.eventitem.eventitem_id,
                              self.context.sched_event.pk]),
                opp.child_event.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=opp.child_event.eventitem.child(
                    ).e_conference.conference_slug,
                event=opp.child_event).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                text="Volunteer",
                event=opp.child_event).count(), 1)

        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="New Volunteer Opportunity" />',
                     response.content)

    def test_create_opportunity_bad_parent(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.sched_event.eventitem.event.__class__.__name__,
                  self.context.sched_event.eventitem.eventitem_id,
                  self.context.sched_event.pk+1])
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1))

    def test_create_opportunity_error(self):
        orig_opp = self.context.opp_event
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_new_opp_data(self.context)
        data['new_opp-max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event
            ).exclude(child_event=orig_opp)
        nt.assert_false(opps.exists())
        nt.assert_in(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            response.content)

    def test_copy_opportunity(self):
        old = self.context.opp_event
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_basic_data(self.context)
        data['duplicate'] = 'duplicate'
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        nt.assert_true(len(opps), 2)
        for opp in opps:
            nt.assert_in(
                '<input id="id_e_title" maxlength="128" '
                'name="e_title" type="text" value="%s" />' % (
                    opp.child_event.eventitem.child().e_title),
                response.content)
            if opp.child_event != old:
                assert_redirects(
                    response,
                    "%s?changed_id=%d" % (reverse(
                        'edit_event_schedule',
                        urlconf='gbe.scheduling.urls',
                        args=['Show',
                              self.context.sched_event.eventitem.eventitem_id,
                              self.context.sched_event.pk]),
                                          opp.child_event.pk))

    def test_edit_opportunity(self):
        x, vol_opp = self.context.add_opportunity()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, vol_opp, 'edit'),
            follow=True)
        assert_redirects(response, "%s?changed_id=%d" % (
            reverse('edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=['Show',
                          self.context.sched_event.eventitem.eventitem_id,
                          self.context.sched_event.pk]),
            vol_opp.pk))
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        nt.assert_true(len(opps), 1)
        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="Modify Volunteer Opportunity" />',
                     response.content)

    def test_edit_opportunity_change_room(self):
        x, vol_opp = self.context.add_opportunity()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, vol_opp, 'edit'),
            follow=True)
        assert_redirects(response, "%s?changed_id=%d" % (
            reverse('edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=['Show',
                          self.context.sched_event.eventitem.eventitem_id,
                          self.context.sched_event.pk]),
            vol_opp.pk))
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        nt.assert_true(len(opps), 1)
        nt.assert_in(self.room.name,
                     response.content)

    def test_edit_opportunity_error(self):
        x, vol_opp = self.context.add_opportunity()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_basic_action_data(self.context, vol_opp, 'edit')
        data['max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in('<input id="id_e_title" maxlength="128" name="e_title" ' +
                     'type="text" value="Modify Volunteer Opportunity" />',
                     response.content)
        nt.assert_in(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            response.content)

    def test_delete_opportunity(self):
        vol_opp = self.context.opp_event
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, vol_opp, 'delete'),
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_not_in('Modify Volunteer Opportunity',
                         response.content)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        nt.assert_false(opps.exists())

    def test_allocate_opportunity(self):
        vol_opp = self.context.opp_event
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        # number of volunteers is missing, it's required
        data = self.get_basic_action_data(self.context, vol_opp, 'allocate')
        data['max_volunteer'] = ''
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_not_in('Modify Volunteer Opportunity',
                         response.content)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        nt.assert_true(opps.exists())
        nt.assert_in("Volunteer Allocation", response.content)
