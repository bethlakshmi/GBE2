from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.class_context import (
    ClassContext,
)
from gbetext import (
    acceptance_states,
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from django.contrib.auth.models import User
from post_office.models import Email


class TestMailToBidder(TestCase):
    view_name = 'mail_to_bidders'
    priv_list = ['Act', 'Class', 'Costume', 'Vendor', 'Volunteer']

    def setUp(self):
        self.client = Client()
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', "mypassword")
        self.privileged_profile = ProfileFactory(
            user_object=self.privileged_user)
        for priv in self.priv_list:
            grant_privilege(
                self.privileged_profile.user_object,
                '%s Coordinator' % priv)
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")

    def reduced_login(self):
        reduced_profile = ProfileFactory()
        grant_privilege(
            reduced_profile.user_object,
            '%s Coordinator' % "Act")
        login_as(reduced_profile, self)
        return reduced_profile

    def assert_queued_email(self, to_list, subject, message, sender):
        queued_email = Email.objects.filter(
            status=2,
            subject=subject,
            html_message=message,
            from_email=sender,
            )
        for recipient in to_list:
            assert queued_email.filter(
                to=recipient).exists()

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s/?next=/email/mail_to_bidders" % (
            reverse('login', urlconf='gbe.urls'))
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="" selected="selected">All</option>',
            3)
        for priv in self.priv_list:
            self.assertContains(
                response,
                '<option value="%s">%s</option>' % (priv, priv))
        for state in acceptance_states:
            self.assertContains(
                response,
                '<option value="%s">%s</option>' % (state[0], state[1]))

    def test_reduced_login_first_get(self):
        self.reduced_login()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="" selected="selected">All</option>',
            3)
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % ("Act", "Act"))
        self.assertNotContains(
            response,
            '<option value="%s">%s</option>' % ("Class", "Class"))

    def test_full_login_first_get_2_conf(self):
        extra_conf = ConferenceFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                self.context.conference.pk,
                self.context.conference.conference_name))
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                extra_conf.pk,
                extra_conf.conference_name))

    def test_pick_conf_bidder(self):
        second_context = ClassContext()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': self.context.conference.pk,
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_context.teacher.contact.user_object.email)

    def test_pick_class_bidder(self):
        second_bid = ActFactory()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-bid_type': "Class",
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_bid.performer.contact.user_object.email)

    def test_pick_status_bidder(self):
        second_class = ClassFactory(accepted=2)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-state': 3,
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_class.teacher.contact.user_object.email)

    def test_pick_forbidden_bid_type_reduced_priv(self):
        second_bid = ActFactory()
        self.reduced_login()
        data = {
            'email-select-bid_type': "Class",
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Class is not one of the available choices.'
            )

    def test_pick_all_reduced_priv(self):
        second_bid = ActFactory()
        self.reduced_login()
        data = {
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            second_bid.performer.contact.user_object.email)

    def test_pick_no_bidders(self):
        reduced_profile = self.reduced_login()
        data = {
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', to_list_empty_msg)

    def test_pick_admin_has_sender(self):
        login_as(self.privileged_profile, self)
        data = {
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)

        self.assertContains(
            response,
            '<input id="id_sender" name="sender" type="email" ' +
            'value="%s" />' % (self.privileged_profile.user_object.email))

    def test_pick_no_admin_fixed_email(self):
        ActFactory()
        reduced_profile = self.reduced_login()
        data = {
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input id="id_sender" name="sender" type="hidden" ' +
            'value="%s" />' % (reduced_profile.user_object.email))

    def test_send_email_success_status(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-to_list': str(to_list),
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s (%s), " % (
                send_email_success_msg,
                self.context.teacher.contact.display_name,
                self.context.teacher.contact.user_object.email))

    def test_send_email_success_email_sent(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-to_list': str(to_list),
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_queued_email(
            [self.context.teacher.contact.user_object.email, ],
            data['subject'],
            data['html_message'],
            data['sender'],
            )

    def test_send_email_reduced_w_fixed_from(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory()
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_queued_email(
            [second_bid.performer.contact.user_object.email, ],
            data['subject'],
            data['html_message'],
            reduced_profile.user_object.email,
            )

    def test_send_email_reduced_no_hack(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory()
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-bid_type': "Class",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Class is not one of the available choices.'
            )

    def test_send_email_failure(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "This field is required.")

    def test_send_email_failure_preserve_to_list(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            "%s &lt;%s&gt;;" % (
                self.context.teacher.contact.display_name,
                self.context.teacher.contact.user_object.email))

    def test_send_email_failure_preserve_conference_choice(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': self.context.conference.pk,
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.context.conference.pk,
                self.context.conference.conference_name))

    def test_send_email_failure_preserve_bid_type_choice(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-bid_type': "Class",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<option value="Class" selected="selected">Class</option>')

    def test_send_email_failure_preserve_state_choice(self):
        login_as(self.privileged_profile, self)
        to_list = {}
        to_list[self.context.teacher.contact.user_object.email] = \
            self.context.teacher.contact.display_name
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-state': 3,
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                3,
                "Accepted"))

    def test_pick_no_post_action(self):
        second_class = ClassFactory(accepted=2)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-state': 3,
        }
        response = self.client.post(self.url, data=data, follow=True)
        print response.content
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)
