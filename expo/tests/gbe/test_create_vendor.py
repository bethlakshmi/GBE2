from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    TransactionFactory,
    TicketItemFactory,
    PurchaserFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    login_as,
    location,
    assert_alert_exists
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
)
from gbe.models import UserMessage


class TestCreateVendor(TestCase):
    '''Tests for create_vendor view'''
    view_name = 'vendor_create'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.conference = current_conference()
        UserMessage.objects.all().delete()

    def get_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'title': 'title here',
                'description': 'description here',
                'physical_address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['description'])
        return form

    def test_create_vendor_no_profile(self):
        url = reverse('vendor_create', urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Update Your Profile' in response.content)

    def test_create_vendor_post_form_valid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data = self.get_form()
        data['profile'] = profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Profile View' in response.content)

    def test_create_vendor_post_form_valid_submit(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data = self.get_form(submit=True)
        data['profile'] = profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Vendor Payment' in response.content)

    def test_create_vendor_post_form_invalid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        data = self.get_form(invalid=True)
        response = self.client.post(
            url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_create_vendor_no_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_create_vendor_with_get_request(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Vendor Application', response.content)

    def test_create_vendor_post_with_vendor_app_paid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        username = profile.user_object.username
        bpt_event = BrownPaperEventsFactory(conference=self.conference,
                                            vendor_submission_event=True)
        purchaser = PurchaserFactory(matched_to_user=profile.user_object)
        ticket_id = "%s-1111" % (bpt_event.bpt_event_id)
        ticket = TicketItemFactory(ticket_id=ticket_id)
        transaction = TransactionFactory(ticket_item=ticket,
                                         purchaser=purchaser)
        login_as(profile, self)
        data = self.get_form(submit=True)
        data['profile'] = profile.pk
        data['username'] = username
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Profile View", response.content)

    def test_vendor_submit_make_message(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        username = profile.user_object.username
        bpt_event = BrownPaperEventsFactory(conference=self.conference,
                                            vendor_submission_event=True)
        purchaser = PurchaserFactory(matched_to_user=profile.user_object)
        ticket_id = "%s-1111" % (bpt_event.bpt_event_id)
        ticket = TicketItemFactory(ticket_id=ticket_id)
        transaction = TransactionFactory(ticket_item=ticket,
                                         purchaser=purchaser)
        login_as(profile, self)
        data = self.get_form(submit=True)
        data['profile'] = profile.pk
        data['username'] = username
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_submit_msg)

    def test_vendor_draft_make_message(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data = self.get_form()
        data['profile'] = profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_draft_msg)

    def test_vendor_submit_has_message(self):
        msg = UserMessageFactory(
            view='CreateVendorView',
            code='SUBMIT_SUCCESS')
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        username = profile.user_object.username
        bpt_event = BrownPaperEventsFactory(conference=self.conference,
                                            vendor_submission_event=True)
        purchaser = PurchaserFactory(matched_to_user=profile.user_object)
        ticket_id = "%s-1111" % (bpt_event.bpt_event_id)
        ticket = TicketItemFactory(ticket_id=ticket_id)
        transaction = TransactionFactory(ticket_item=ticket,
                                         purchaser=purchaser)
        login_as(profile, self)
        data = self.get_form(submit=True)
        data['profile'] = profile.pk
        data['username'] = username
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_vendor_draft_has_message(self):
        msg = UserMessageFactory(
            view='CreateVendorView',
            code='DRAFT_SUCCESS')
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data = self.get_form()
        data['profile'] = profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
