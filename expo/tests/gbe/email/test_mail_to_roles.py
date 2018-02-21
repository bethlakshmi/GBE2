from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    GenericEventFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.functions.gbe_email_functions import assert_checkbox
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from gbetext import (
    acceptance_states,
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from django.contrib.auth.models import User
from gbe.models import Conference
from post_office.models import Email
from gbetext import role_options
from gbe_forms_text import role_option_privs


class TestMailToBidder(TestCase):
    view_name = 'mail_to_roles'
    role_list = ['Interested',
                 'Moderator',
                 "Panelist",
                 "Performer",
                 "Producer",
                 "Staff Lead",
                 "Teacher",
                 "Technical Director",
                 "Volunteer"]

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', "mypassword")
        self.privileged_profile = ProfileFactory(
            user_object=self.privileged_user)
        grant_privilege(self.privileged_profile.user_object,
                        "Schedule Mavens")
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")

    def class_coord_login(self):
        limited_profile = ProfileFactory()
        grant_privilege(limited_profile.user_object, "Class Coordinator")
        login_as(limited_profile, self)

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)
        n = 0
        for role in role_options:
            assert_checkbox(
                response,
                "roles",
                n,
                role[0],
                role[1])
            n = n + 1
        self.assertContains(response, "Email Everyone")

    def test_reduced_login_first_get(self):
        for priv, roles in role_option_privs.iteritems():
            limited_profile = ProfileFactory()
            grant_privilege(limited_profile.user_object,
                            priv)
            login_as(limited_profile, self)

            response = self.client.get(self.url, follow=True)
            assert_checkbox(
                response,
                "conference",
                0,
                self.context.conference.pk,
                self.context.conference.conference_slug)
            n = 0
            for role in sorted(roles):
                assert_checkbox(
                    response,
                    "roles",
                    n,
                    role,
                    role)
                n = n + 1
        self.assertNotContains(response, "Email Everyone")
    def test_full_login_first_get_2_conf(self):
        extra_conf = ConferenceFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)
        assert_checkbox(
            response,
            "conference",
            1,
            extra_conf.pk,
            extra_conf.conference_slug)

    def test_pick_conf_teacher(self):
        second_context = ClassContext()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': self.role_list,
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_context.teacher.contact.user_object.email)


    def test_pick_class_teacher(self):
        interested = self.context.set_interest()
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher"],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            interested.user_object.email)
        print response.content
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Conference",
            "All Conference Classes",
            checked=False,
            prefix="event-select")

    def test_pick_all_conf_class(self):
        interested = self.context.set_interest()
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher"],
            'event-select-event_collections': "Conference",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            interested.user_object.email)
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Conference",
            "All Conference Classes",
            prefix="event-select")

    def test_pick_forbidden_role_reduced_priv(self):
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher", "Performer"],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Performer is not one of the available choices.'
            )

    def test_pick_forbidden_collection_reduced_priv(self):
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher", ],
            'event-select-event_collections': "Volunteer",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Volunteer is not one of the available choices.'
            )

    def test_pick_performer_reduced_priv(self):
        showcontext = ShowContext()
        producer = showcontext.set_producer()
        anothershowcontext = ShowContext(
            conference=showcontext.conference,
        )
        login_as(producer, self)
        data = {
            'email-select-conference': [showcontext.conference.pk,
                                        self.context.conference.pk],
            'email-select-roles': ['Performer', ],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            showcontext.performer.contact.user_object.email)
        self.assertContains(
            response,
            anothershowcontext.performer.contact.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            showcontext.show.pk,
            showcontext.show.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "events",
            1,
            anothershowcontext.show.pk,
            anothershowcontext.show.e_title,
            checked=False,
            prefix="event-select")

    def test_pick_performer_specific_show(self):
        showcontext = ShowContext()
        anothershowcontext = ShowContext(
            conference=showcontext.conference,
        )
        producer = showcontext.set_producer()
        login_as(producer, self)
        data = {
            'email-select-conference': [showcontext.conference.pk,
                                        self.context.conference.pk],
            'email-select-roles': ['Performer', ],
            'event-select-events': showcontext.show.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            anothershowcontext.performer.contact.user_object.email)
        self.assertContains(
            response,
            showcontext.performer.contact.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            showcontext.show.pk,
            showcontext.show.e_title,
            prefix="event-select")
        assert_checkbox(
            response,
            "events",
            1,
            anothershowcontext.show.pk,
            anothershowcontext.show.e_title,
            checked=False,
            prefix="event-select")
    
    def test_pick_performer_mismatch_show(self):
        showcontext = ShowContext()
        anothershowcontext = ShowContext()
        producer = showcontext.set_producer()
        login_as(producer, self)
        data = {
            'email-select-conference': [anothershowcontext.conference.pk],
            'email-select-roles': ['Performer', ],
            'event-select-events': showcontext.show.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            "%d is not one of the available choices." % showcontext.show.pk)

    def test_pick_staff_area_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk,],
            'email-select-roles': ['Volunteer', ],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_special_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk,],
            'email-select-roles': ['Volunteer', ],
            'event-select-events': special.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_area_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk,],
            'email-select-roles': ['Volunteer', ],
            'event-select-staff_areas': staffcontext.area.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertNotContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_all_vol_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk,],
            'email-select-roles': ['Volunteer', ],
            'event-select-event_collections': "Volunteer",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            prefix="event-select")

'''
    def test_pick_no_bidders(self):
        reduced_profile = self.reduced_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', to_list_empty_msg)

    def test_pick_admin_has_sender(self):
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': "Filter",
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input id="id_sender" name="sender" type="email" ' +
            'value="%s" />' % (self.privileged_profile.user_object.email))

    def test_pick_no_admin_fixed_email(self):
        act_bid = ActFactory(submitted=True)
        reduced_profile = self.reduced_login()
        data = {
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'email-select-bid_type': ['Act'],
            'email-select-conference': [act_bid.b_conference.pk],
            'filter': "Filter",
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input id="id_sender" name="sender" type="hidden" ' +
            'value="%s" />' % (reduced_profile.user_object.email))

    def test_send_email_success_status(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
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
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [self.context.teacher.contact.user_object.email, ],
            data['subject'],
            data['html_message'],
            data['sender'],
            )

    def test_send_email_reduced_w_fixed_from(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory(submitted=True)
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
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
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': "Class",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Class is not one of the available choices.'
            )

    def test_send_email_failure(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "This field is required.")

    def test_send_email_failure_preserve_to_list(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
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
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)

    def test_send_email_failure_preserve_bid_type_choice(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': "Class",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_checkbox(
            response,
            "bid_type",
            1,
            "Class",
            "Class")

    def test_send_email_failure_preserve_state_choice(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [3, ],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input checked="checked" id="id_email-select-state_4" ' +
            'name="email-select-state" type="checkbox" value="3" />')

    def test_pick_no_post_action(self):
        second_class = ClassFactory(accepted=2)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)

    def test_send_everyone_success_email_sent(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        for user in User.objects.exclude(username="limbo"):
            assert_queued_email(
                [user.email, ],
                data['subject'],
                data['html_message'],
                data['sender'],
                )

    def test_send_everyone_reduced(self):
        reduced_profile = self.reduced_login()
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)

    def test_send_everyone_success_alert_displayed(self):
        User.objects.exclude(
            username=self.privileged_profile.user_object.username).delete()
        second_super = User.objects.create_superuser(
            'secondsuper', 'secondsuper@test.com', "mypassword")
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s (%s), %s (%s), " % (
                send_email_success_msg,
                self.privileged_profile.display_name,
                self.privileged_profile.user_object.email,
                second_super.username,
                second_super.email))
'''
