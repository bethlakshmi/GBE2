from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserMessageFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_right_mail_right_addresses,
    assert_hidden_value,
    assert_rank_choice_exists,
    clear_conferences,
    login_as,
    grant_privilege,
)
from gbetext import (
    default_volunteer_submit_msg,
    default_volunteer_no_interest_msg
)
from gbe.models import UserMessage
from expo.settings import DATETIME_FORMAT


class TestEditVolunteer(TestCase):
    '''Tests for edit_volunteer view'''
    view_name = 'volunteer_edit'

    # this test case should be unnecessary, since edit_volunteer should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def get_form(self, context, invalid=False, rank=5):
        interest_pk = context.bid.volunteerinterest_set.first().pk
        avail_pk = context.bid.volunteerinterest_set.first().interest.pk
        form = {'profile': 1,
                'number_shifts': 2,
                'availability': ('SH0',),
                'available_windows': [context.conference.windows().first().pk],
                'background': 'this is the background',
                'b_title': 'title',
                '%d-rank' % interest_pk: rank,
                '%d-interest' % interest_pk: avail_pk,
                 }
        if invalid:
            del(form['number_shifts'])
        return form

    def edit_volunteer(self, rank=5):
        clear_conferences()
        context = VolunteerContext()
        add_window = context.add_window()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        form = self.get_form(context, rank=rank)
        form['unavailable_windows'] = add_window.pk
        response = self.client.post(
            url,
            form,
            follow=True)
        return response, context

    def post_conflict(self, staff=True):
        context = VolunteerContext()
        change_window = context.add_window()
        if staff:
            context.sched_event.allocate_worker(
                context.profile, 'Staff Lead')
        context.bid.available_windows.add(context.window)
        form = self.get_form(context)
        form['available_windows'] = [change_window.pk]
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(context.profile, self)
        response = self.client.post(
            url,
            form,
            follow=True)
        return response, context

    def test_edit_volunteer_no_volunteer(self):
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[0])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_edit_volunteer_profile_is_not_coordinator(self):
        user = ProfileFactory().user_object
        volunteer = VolunteerFactory()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_edit_volunteer_profile_is_owner(self):
        volunteer = VolunteerFactory()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(volunteer.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Volunteer at the Expo' in response.content)

    def test_volunteer_edit_post_form_not_valid(self):
        '''volunteer_edit, if form not valid, should return
        to VolunteerEditForm'''
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            self.get_form(context,
                          invalid=True))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('Volunteer at the Expo' in response.content)

    def test_volunteer_edit_post_form_valid(self):
        '''volunteer_edit, if form not valid, should return
        to VolunteerEditForm'''
        response, context = self.edit_volunteer()
        expected_string = ("Bid Information for %s" %
                           context.conference.conference_name)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(expected_string in response.content)

    def test_volunteer_edit_get(self):
        volunteer = VolunteerFactory(
            availability='',
            unavailability='',
            b_title="title")
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Volunteer at the Expo' in response.content)
        assert_hidden_value(
            response,
            "id_b_title",
            "b_title",
            volunteer.b_title,
            128)

    def test_volunteer_edit_get_rank(self):
        volunteer = VolunteerFactory(
            availability='',
            unavailability='')
        interest = VolunteerInterestFactory(volunteer=volunteer)
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert_rank_choice_exists(response, interest, interest.rank)

    def test_volunteer_edit_get_with_stuff(self):
        volunteer = VolunteerFactory()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Volunteer at the Expo' in response.content)

    def test_volunteer_submit_make_message(self):
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_volunteer_submit_msg)

    def test_volunteer_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='SUBMIT_SUCCESS')
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_not_interested_at_all(self):
        response, context = self.edit_volunteer(rank=1)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_interest_msg)

    def test_not_interested_at_all_make_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='NO_INTERESTS_SUBMITTED')
        response, context = self.edit_volunteer(rank=1)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', msg.description)

    def test_interest_bad_data(self):
        response, context = self.edit_volunteer(rank='bad_data')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<font color="red"><ul class="errorlist">' +
            '<li>Select a valid choice. bad_data is not one of ' +
            'the available choices.</li></ul></font>')

    def test_remove_available_window_conflict(self):
        response, context = self.post_conflict(staff=False)
        assert 'Warning', "<li>%s working for %s - as %s" % (
            context.window.start_time.strftime(DATETIME_FORMAT),
            str(context.opportunity),
            context.opportunity.child(
                ).volunteer_category_description
            ) in response.content

    def test_set_uavailable_window_conflict(self):
        context = VolunteerContext()
        change_window = context.add_window()
        context.bid.available_windows.add(change_window.pk)
        form = self.get_form(context)
        form['unavailable_windows'] = [context.window.pk]
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(context.profile, self)
        response = self.client.post(
            url,
            form,
            follow=True)
        assert 'Warning', "<li>%s working for %s - as %s" % (
            context.window.start_time.strftime(DATETIME_FORMAT),
            str(context.opportunity),
            context.opportunity.child(
                ).volunteer_category_description
            ) in response.content

    def test_conflict_w_staff_lead(self):
        response, context = self.post_conflict(staff=True)
        assert 'Warning', "<li>%s working for %s - as %s" % (
            context.window.start_time.strftime(DATETIME_FORMAT),
            str(context.opportunity),
            context.opportunity.child(
                ).volunteer_category_description
            ) in response.content

    def test_volunteer_conflict_sends_update_to_user(self):
        response, context = self.post_conflict(staff=True)
        assert_right_mail_right_addresses(
            0,
            3,
            "A change has been made to your Volunteer Schedule!",
            [context.profile.contact_email])

    def test_volunteer_conflict_sends_warning_to_staff(self):
        response, context = self.post_conflict(staff=True)
        assert_right_mail_right_addresses(
            1,
            3,
            "URGENT: Volunteer Schedule Conflict Occurred",
            [self.privileged_profile.contact_email,
             context.profile.contact_email])

    def test_volunteer_conflict_sends_warning_no_staff(self):
        response, context = self.post_conflict(staff=False)
        assert_right_mail_right_addresses(
            1,
            3,
            "URGENT: Volunteer Schedule Conflict Occurred",
            [self.privileged_profile.contact_email])

    def test_volunteer_conflict_sends_notification_to_reviewers(self):
        response, context = self.post_conflict(staff=True)
        assert_right_mail_right_addresses(
            2,
            3,
            "Volunteer Update Occurred",
            [self.privileged_profile.contact_email])

    def test_volunteer_conflict_removes_volunteer_commitment(self):
        response, context = self.post_conflict(staff=True)
        assert context.opp_event.volunteer_count == 0
        assert context.opportunity.roles(
            roles=['Staff Lead', ]
            )[0]._item.contact_email == context.profile.contact_email
