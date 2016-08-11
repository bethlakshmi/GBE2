from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    location,
    login_as
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestBidClass(TestCase):
    '''Tests for edit_class view'''
    view_name = 'class_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.teacher = PersonaFactory()
        self.conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()

    def get_class_form(self,
                       submit=False,
                       invalid=False,
                       incomplete=False):
        data = {'teacher': self.teacher.pk,
                'title': 'A class',
                'description': 'a description',
                'length_minutes': 60,
                'maximum_enrollment': 20,
                'fee': 0,
                'schedule_constraints': ['0'],
                'conference': self.conference
                }
        if submit:
            data['submit'] = 1
        if invalid:
            del(data['title'])
        if incomplete:
            data['title'] = ''
        return data

    def post_class_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=True)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def post_class_draft(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=False)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_bid_class_no_personae(self):
        '''class_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(
            url,
            follow=True)
        redirect = ('http://testserver/performer/create?next=/class/create',
                    302)
        assert redirect in response.redirect_chain
        title = '<h2 class="subtitle">Tell Us About Your Stage Persona</h2>'
        assert title in response.content
        assert response.status_code == 200

    def test_class_bid_post_with_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_submit()
        self.assertEqual(response.status_code, 200)
        # stricter test required here

    def test_class_bid_post_with_submit_incomplete(self):
        '''class_bid, submit, incomplete form'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        data = self.get_class_form(submit=True, invalid=True)
        user = self.performer.performer_profile.user_object
        login_as(user, self)
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = "This field is required"
        self.assertTrue(expected_string in response.content)

    def test_class_bid_post_no_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_draft()
        self.assertEqual(200, response.status_code)
        self.assertTrue('Profile View' in response.content)

    def test_class_bid_post_invalid_form_no_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        other_performer = PersonaFactory()
        other_profile = other_performer.performer_profile
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=False, invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue('Submit a Class' in response.content)
        self.assertFalse(other_performer.name in response.content)
        current_user_selection = '<option value="%d">%s</option>'
        persona_id = self.performer.pk
        selection_string = current_user_selection % (persona_id,
                                                     self.performer.name)
        self.assertTrue(selection_string in response.content)

    def test_class_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Submit a Class' in response.content)

    def test_class_bid_verify_info_popup_text(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'We will do our best to accommodate' in response.content)

    def test_class_bid_verify_avoided_constraints(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('I Would Prefer to Avoid' in response.content)

    def test_class_submit_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_submit()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_class_submit_msg)

    def test_class_draft_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_class_draft_msg)

    def test_class_submit_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='BidClassView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_class_submit()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_class_draft_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='BidClassView',
            code='DRAFT_SUCCESS')
        response, data = self.post_class_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
