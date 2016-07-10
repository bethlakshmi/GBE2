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
)
from tests.contexts import VolunteerContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    clear_conferences,
    login_as,
    grant_privilege,
)
from gbetext import default_volunteer_edit_msg
from gbe.models import UserMessage


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

    def get_form(self, conference, submit=False, invalid=False):
        form = {'profile': 1,
                'number_shifts': 2,
                'availability': ('SH0',),
                'interests': ('VA0',),
                'available_windows': [conference.windows().first().pk]
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['number_shifts'])
        return form

    def edit_volunteer(self):
        clear_conferences()
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            self.get_form(context.conference),
            follow=True)
        return response, context

    def test_edit_volunteer_no_volunteer(self):
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[0])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_edit_volunteer_profile_is_not_coordinator(self):
        user = ProfileFactory().user_object
        volunteer = VolunteerFactory()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

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
            self.get_form(context.conference,
                          invalid=True))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('Edit Volunteer Bid' in response.content)

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
            interests='')
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Edit Volunteer Bid' in response.content)

    def test_volunteer_submit_make_message(self):
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_volunteer_edit_msg)

    def test_volunteer_submit_has_message(self):
        msg = UserMessageFactory(
            view='EditVolunteerView',
            code='SUBMIT_SUCCESS')
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
