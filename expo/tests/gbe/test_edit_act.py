from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_act
import mock
from tests.factories import gbe_factories as factories
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
        self.performer = factories.PersonaFactory.create()

    def get_act_form(self):
        return {'teacher': 2,
                'title': 'A act',
                'description': 'a description',
                'length_minutes': 60,
                'maximum_enrollment': 20,
                'fee': 0,
                }

    @nt.raises(Http404)
    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/edit/-1')
        request.user = profile.user_object
        response = edit_act(request, -1)

    @nt.raises(Http404)
    def test_edit_act_profile_is_not_contact(self):
        user = factories.ProfileFactory.create().user_object
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = user
        response = edit_act(request, act.pk)

    def test_act_edit_post_form_not_valid(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.session = {'cms_admin_site':1}
        del(request.POST['title'])
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)

    def t_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home
        have to solve the mocking problem to get submit paid'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.contact.user_object
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.contact.user_object
        request.session = {'cms_admin_site':1}
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)
