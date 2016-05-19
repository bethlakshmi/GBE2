from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.contexts import StaffAreaContext # VolunteerContext
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
import pytz
from datetime import (
    datetime,
    time,
)
from model_utils.managers import InheritanceManager

class TestAllocateWorkers(TestCase):
    view_name = "allocate_workers"

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.context = StaffAreaContext()

    def assert_good_post(self,
                         response,
                         volunteer_opp,
                         volunteer,
                         alloc,
                         role="Volunteer"):
        self.assertRedirects(response,
                             reverse('edit_event',
                                     urlconf='scheduler.urls',
                                     args=["GenericEvent", volunteer_opp.pk]))
        self.assertContains(
            response,
            '<option value="' + str(volunteer.pk) +
            '" selected="selected">' + str(volunteer) + '</option>')
        self.assertContains(
            response,
            '<option value="' + role +
            '" selected="selected">' + role +
            '</option>')
        self.assertContains(
            response,
            '<input id="id_alloc_id" name="alloc_id" type="hidden" value="' +
            str(alloc.pk) + '" />')
        self.assertContains(
            response,
            '<form method="POST" action="/scheduler/allocate/' +
            str(volunteer_opp.pk) + '"', count=2)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[1])
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[1])
        response = self.client.get(url)
        data = {'worker': 1,
                'alloc_id': 1,
                'role': 'Volunteer'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)

    def test_not_post(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      args=[1],
                      urlconf="scheduler.urls")
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_post_form_valid_make_new_allocation(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        allocations = volunteer_opp.resources_allocated.all()
        volunteer = ProfileFactory()
        url = reverse(self.view_name,
                      args=[volunteer_opp.pk],
                      urlconf="scheduler.urls")
        data = {'worker': volunteer.pk,
                'alloc_id': -1,
                'role': 'Volunteer'}

        login_as(self.privileged_profile, self)
        response = self.client.post(url, data=data, follow=True)
        alloc = volunteer_opp.resources_allocated.all().first()

        self.assertIsNotNone(alloc)
        self.assert_good_post(response,
                         volunteer_opp,
                         volunteer,
                         alloc)

    def test_post_form_edit_exiting_allocation(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        volunteer, alloc = context.book_volunteer(volunteer_opp)
        new_volunteer = ProfileFactory()

        url = reverse(self.view_name,
                      args=[volunteer_opp.pk],
                      urlconf="scheduler.urls")
        data = {'worker': new_volunteer.pk,
                'alloc_id': alloc.pk,
                'role': 'Producer'}

        login_as(self.privileged_profile, self)
        response = self.client.post(url, data=data, follow=True)
        self.assert_good_post(response,
                         volunteer_opp,
                         new_volunteer,
                         alloc,
                         "Producer")

    def test_post_form_valid_delete_allocation(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        volunteer, alloc = context.book_volunteer(volunteer_opp)
        url = reverse(self.view_name,
                      args=[volunteer_opp.pk],
                      urlconf="scheduler.urls")
        data = {'worker': volunteer.pk,
                'alloc_id': alloc.pk,
                'role': 'Producer',
                'delete': 1}
        login_as(self.privileged_profile, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response,
                             reverse('edit_event',
                                     urlconf='scheduler.urls',
                                     args=["GenericEvent", volunteer_opp.pk]))
        self.assertNotContains(
            response,
            '<option value="' + str(volunteer.pk) +
            '" selected="selected">' + str(volunteer) + '</option>')
        self.assertNotContains(
            response,
            '<input id="id_alloc_id" name="alloc_id" type="hidden" value="' +
            str(alloc.pk) + '" />')
        self.assertContains(
            response,
            '<form method="POST" action="/scheduler/allocate/' +
            str(volunteer_opp.pk) + '"', count=1)
