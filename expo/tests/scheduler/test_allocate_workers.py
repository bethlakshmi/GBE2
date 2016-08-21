from django.core import mail
from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import ProfileFactory
from tests.contexts import StaffAreaContext
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)


class TestAllocateWorkers(TestCase):
    view_name = "allocate_workers"

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        context = StaffAreaContext()
        self.volunteer_opp = context.add_volunteer_opp()
        self.volunteer, self.alloc = context.book_volunteer(
            self.volunteer_opp)
        self.url = reverse(
            self.view_name,
            args=[self.volunteer_opp.pk],
            urlconf="scheduler.urls")

    def get_edit_data(self):
        data = self.get_either_data()
        data['alloc_id'] = self.alloc.pk
        return data

    def get_create_data(self):
        data = self.get_either_data()
        data['alloc_id'] = -1
        return data

    def get_either_data(self):
        data = {'worker': self.volunteer.pk,
                'role': 'Volunteer',
                'label': 'Do these notes work?'}
        return data

    def assert_post_contents(self,
                             response,
                             volunteer_opp,
                             volunteer,
                             alloc,
                             notes,
                             role="Volunteer"):
        if volunteer == -1:
            self.assertContains(
                response,
                '<option value="" selected="selected">---------</option>')
        else:
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
            '<input id="id_label" maxlength="100" name="label" type="text" ' +
            'value="' + notes + '" />')
        self.assertContains(
            response,
            '<form method="POST" action="/scheduler/allocate/' +
            str(volunteer_opp.pk) + '"', count=2)

    def assert_good_post(self,
                         response,
                         volunteer_opp,
                         volunteer,
                         alloc,
                         notes,
                         role="Volunteer"):
        self.assertRedirects(response,
                             reverse('edit_event',
                                     urlconf='scheduler.urls',
                                     args=["GenericEvent", volunteer_opp.pk]))
        self.assert_post_contents(response,
                                  volunteer_opp,
                                  volunteer,
                                  alloc,
                                  notes,
                                  role)
        self.assertNotContains(response, '<ul class="errorlist">')

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.post(self.url, data=self.get_create_data())
        self.assertEqual(response.status_code, 403)

    def test_not_post(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(404, response.status_code)

    def test_post_form_valid_make_new_allocation(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        allocations = volunteer_opp.resources_allocated.all()
        volunteer = ProfileFactory()
        url = reverse(self.view_name,
                      args=[volunteer_opp.pk],
                      urlconf="scheduler.urls")
        data = self.get_create_data()
        data['worker'] = volunteer.pk,

        login_as(self.privileged_profile, self)
        response = self.client.post(url, data=data, follow=True)
        alloc = volunteer_opp.resources_allocated.all().first()

        self.assertIsNotNone(alloc)
        self.assert_good_post(
            response,
            volunteer_opp,
            volunteer,
            alloc,
            'Do these notes work?')

    def test_post_form_edit_exiting_allocation(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_good_post(
            response,
            self.volunteer_opp,
            new_volunteer,
            self.alloc,
            'Do these notes work?',
            "Producer")

    def test_post_form_edit_bad_label(self):
        big_label = 'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?'
        data = self.get_edit_data()
        data['label'] = big_label

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            big_label)
        self.assertContains(
            response,
            '<li>Ensure this value has at most 100 characters ' +
            '(it has ' + str(len(big_label)) + ').</li>')

    def test_post_form_edit_bad_role(self):
        data = self.get_edit_data()
        data['role'] = ''

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            'Do these notes work?')
        self.assertContains(
            response,
            '<li>This field is required.</li>')

    def test_post_form_create_bad_role(self):
        data = self.get_create_data()
        data['role'] = '',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            'Do these notes work?')
        self.assertContains(
            response,
            '<li>This field is required.</li>')
        self.assertContains(
            response,
            "Delete Allocation",
            count=1)
        self.assertContains(
            response,
            "Edit/Create Allocation",
            count=2)

    def test_post_form_valid_delete_allocation(self):
        data = self.get_edit_data()
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'edit_event',
                urlconf='scheduler.urls',
                args=["GenericEvent", self.volunteer_opp.pk]))
        self.assertNotContains(
            response,
            '<option value="' + str(self.volunteer.pk) +
            '" selected="selected">' + str(self.volunteer) + '</option>')
        self.assertNotContains(
            response,
            '<input id="id_alloc_id" name="alloc_id" type="hidden" value="' +
            str(self.alloc.pk) + '" />')
        self.assertContains(
            response,
            '<form method="POST" action="/scheduler/allocate/' +
            str(self.volunteer_opp.pk) + '"', count=1)

    def test_post_form_valid_delete_allocation_sends_notification(self):
        data = self.get_edit_data()
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'edit_event',
                urlconf='scheduler.urls',
                args=["GenericEvent", self.volunteer_opp.pk]))
        assert 1 == len(mail.outbox)
        msg = mail.outbox[0]
        expected_subject = "A change has been made to your Volunteer Schedule!"
        assert msg.subject == expected_subject



    def test_post_form_valid_delete_allocation_w_bad_data(self):
        data = self.get_edit_data()
        data['role'] = ''
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'edit_event',
                urlconf='scheduler.urls',
                args=["GenericEvent", self.volunteer_opp.pk]))
        self.assertNotContains(
            response,
            '<option value="' + str(self.volunteer.pk) +
            '" selected="selected">' + str(self.volunteer) + '</option>')
        self.assertNotContains(
            response,
            '<input id="id_alloc_id" name="alloc_id" type="hidden" value="' +
            str(self.alloc.pk) + '" />')
        self.assertContains(
            response,
            '<form method="POST" action="/scheduler/allocate/' +
            str(self.volunteer_opp.pk) + '"', count=1)

    def test_post_form_edit_exiting_allocation(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert 1 == len(mail.outbox)
        msg = mail.outbox[0]
        expected_subject = "A change has been made to your Volunteer Schedule!"
        assert msg.subject == expected_subject
