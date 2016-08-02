from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
    make_act_app_purchase
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg
)
from gbe.models import UserMessage


class TestEditAct(TestCase):
    '''Tests for edit_act view'''

    # this test case should be unnecessary, since edit_act should go away
    # for now, test it.
    view_name = 'act_edit'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()

    def get_act_form(self, act, submit=False, invalid=False):
        form_dict = {'theact-performer': act.performer.pk,
                     'theact-title': 'An act',
                     'theact-description': 'a description',
                     'theact-length_minutes': 60,
                     'theact-shows_preferences': [0],
                     }
        if submit:
            form_dict['submit'] = 1
        if invalid:
            del(form_dict['theact-title'])
        return form_dict

    def post_edit_paid_act_submission(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        make_act_app_purchase(act.performer.performer_profile.user_object)
        response = self.client.post(
            url,
            data=self.get_act_form(act, submit=True),
            follow=True)
        return response

    def post_edit_paid_act_draft(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        response = self.client.post(url,
                                    self.get_act_form(act),
                                    follow=True)
        return response

    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_profile_is_not_contact(self):
        user = ProfileFactory().user_object
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_user_has_no_profile(self):
        user = UserFactory()
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(user, self)
        response = self.client.get(url, follow=True)
        self.assertTrue(('http://testserver/profile', 302)
                        in response.redirect_chain)

    def test_act_edit_post_form_not_valid(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            self.get_act_form(act, invalid=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Edit Your Act Proposal' in response.content)

    def test_act_edit_post_form_submit_unpaid(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            data=self.get_act_form(act, submit=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Act Payment' in response.content)

    def test_edit_bid_post_no_submit(self):
        response = self.post_edit_paid_act_draft()
        redirect_tuple = ('http://testserver/gbe', 302)
        self.assertTrue(redirect_tuple in response.redirect_chain)
        self.assertTrue('Profile View' in response.content)

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Edit Your Act Proposal' in response.content)

    def test_edit_act_submit_make_message(self):
        response = self.post_edit_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

    def test_edit_act_draft_make_message(self):
        response = self.post_edit_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_edit_act_submit_has_message(self):
        msg = UserMessageFactory(
            view='EditActView',
            code='SUBMIT_SUCCESS')
        response = self.post_edit_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_edit_act_draft_has_message(self):
        msg = UserMessageFactory(
            view='EditActView',
            code='DRAFT_SUCCESS')
        response = self.post_edit_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
