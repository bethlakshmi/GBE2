from django.http import Http404
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_act
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

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_act_form(self, submit=False):
        form_dict = {'theact-teacher': 2,
                     'theact-title': 'An act',
                     'theact-description': 'a description',
                     'theact-length_minutes': 60,
                     'theact-shows_preferences': [0],
                     }
        if submit:
            form_dict['submit'] = 1
        return form_dict

    @nt.raises(Http404)
    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = ProfileFactory()
        request = self.factory.get('/act/edit/-1')
        request.user = profile.user_object
        response = edit_act(request, -1)

    @nt.raises(Http404)
    def test_edit_act_profile_is_not_contact(self):
        user = ProfileFactory().user_object
        act = ActFactory()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = user
        response = edit_act(request, act.pk)

    def test_edit_act_user_has_no_profile(self):
        user = UserFactory()
        act = ActFactory()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = user
        response = edit_act(request, act.pk)

    def test_act_edit_post_form_not_valid(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = ActFactory()
        request = self.factory.post('/act/edit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        request.POST = self.get_act_form()
        request.session = {'cms_admin_site': 1}
        del(request.POST['theact-title'])
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)

    def test_act_edit_post_form_submit(self):
        act = ActFactory()
        request = self.factory.post('/act/edit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        request.POST = self.get_act_form(submit=True)
        request.session = {'cms_admin_site': 1}
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Act Payment' in response.content)

    def test_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home
        have to solve the mocking problem to get submit paid'''
        act = ActFactory()
        request = self.factory.post('/act/edit/%d' % act.pk)
        request.user = act.performer.contact.user_object
        request.session = {'cms_admin_site': 1}
        request.POST = self.get_act_form()
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 302)

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.contact.user_object
        request.session = {'cms_admin_site': 1}
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)
