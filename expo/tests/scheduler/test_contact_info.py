from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext
)
from gbe.models import Conference


class TestContactInfo(TestCase):
    view_name = 'contact_info'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        Conference.objects.all().delete()
        self.context = ClassContext()

    def test_no_login_gives_error(self):
        url = reverse(
            self.view_name,
            urlconf="scheduler.urls",
            args=[self.context.sched_event.pk,
                  'Teachers'])
        response = self.client.get(url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(
            reverse(
                self.view_name,
                urlconf="scheduler.urls",
                args=[self.context.sched_event.pk,
                      'Teachers']))
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="scheduler.urls",
            args=[self.context.sched_event.pk+1,
                 'Teachers'])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_class_contacts(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                urlconf="scheduler.urls",
                args=[self.context.sched_event.pk,
                      'Teachers']), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.context.teacher.contact.display_name in response.content)
        self.assertTrue(
            self.context.teacher.contact.user_object.email in response.content)

    def test_good_user_get_show_contacts(self):
        Conference.objects.all().delete()
        show = ShowContext()
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                urlconf="scheduler.urls",
                args=[show.sched_event.pk,
                      'Act']), follow=True)
        self.assertEqual(response.status_code, 200)
        for act in show.acts:
            for item in act.contact_info:
                self.assertContains(
                    response,
                    str(item))

    def test_good_user_get_default_contacts(self):
        Conference.objects.all().delete()
        show = ShowContext()
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                urlconf="scheduler.urls",
                args=[show.sched_event.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        for act in show.acts:
            for item in act.contact_info:
                self.assertContains(
                    response,
                    str(item))

    def test_good_user_get_volunteer_contacts(self):
        Conference.objects.all().delete()
        context = StaffAreaContext()
        opp1 = context.add_volunteer_opp()
        opp2 = context.add_volunteer_opp()
        (volunteer1, alloc1) = context.book_volunteer(opp1)
        (volunteer2, alloc2) = context.book_volunteer(opp2)

        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                urlconf="scheduler.urls",
                args=[context.sched_event.pk, 'Worker']),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            volunteer1.display_name)
        self.assertContains(
            response,
            volunteer1.contact_email)
        self.assertContains(
            response,
            volunteer1.phone)
        self.assertContains(
            response,
            "Volunteer")
        self.assertContains(
            response,
            "Registration")
