from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditAct(TestCase):
    '''Tests for edit_act view'''

    # this test case should be unnecessary, since edit_act should go away
    # for now, test it.
    view_name = 'act_edit'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_act_form(self, submit=False, invalid=False):
        form_dict = {'theact-teacher': 2,
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

    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 404)

    def test_edit_act_profile_is_not_contact(self):
        user = ProfileFactory().user_object
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 404)

    def test_edit_act_user_has_no_profile(self):
        user = UserFactory()
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(user, self)
        response = self.client.get(url, follow=True)
        nt.assert_true(('http://testserver/profile', 302)
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
            self.get_act_form(invalid=True))
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)

    def test_act_edit_post_form_submit(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            data=self.get_act_form(submit=True))
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Act Payment' in response.content)

    def test_edit_bid_post_no_submit(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        response = self.client.post(url,
                                    self.get_act_form(),
                                    follow=True)
        redirect_tuple = ('http://testserver/gbe', 302)
        nt.assert_true(redirect_tuple in response.redirect_chain)
        nt.assert_true('Profile View' in response.content)

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)
