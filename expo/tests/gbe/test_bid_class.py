import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import bid_class
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as
)


class TestEditClass(TestCase):
    '''Tests for edit_class view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.teacher = PersonaFactory.create()
        self.conference = ConferenceFactory(accepting_bids=True)

    def get_class_form(self):
        return {'teacher': self.teacher.pk,
                'title': 'A class',
                'description': 'a description',
                'length_minutes': 60,
                'maximum_enrollment': 20,
                'fee': 0,
                'schedule_constraints': ['0'],
                'conference': self.conference
                }

    def test_bid_class_no_personae(self):
        '''class_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory.create()
        request = self.factory.get('/class/create')
        request.user = profile.user_object
        response = bid_class(request)
        nt.assert_equal(response.status_code, 302)

    def test_class_bid_post_form_not_valid(self):
        '''class_bid, if form not valid, should return to ClassEditForm'''
        request = self.factory.get('/class/create')
        request.user = self.performer.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_class_form())
        request.session = {'cms_admin_site':1}
        del(request.POST['title'])
        response = bid_class(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Submit a Class' in response.content)

    def test_class_bid_post_no_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        request = self.factory.get('/class/create')
        request.user = self.performer.performer_profile.user_object
        login_as(request.user, self)
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_class_form())
        request.session = {'cms_admin_site':1}
        response = bid_class(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')


    def test_class_bid_post_with_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        request = self.client.get('/class/create',
                                  follow=True)
        request.user = self.performer.performer_profile.user_object
        login_as(request.user, self)
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_class_form())
        request.POST.update({'submit':1})
        request.session = {'cms_admin_site':1}
        response = bid_class(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')


    def test_class_bid_post_invalid(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        request = self.client.get('/class/create',
                                  follow=True)
        request.user = self.performer.performer_profile.user_object
        login_as(request.user, self)
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_class_form())
        request.session = {'cms_admin_site':1}
        response = bid_class(request)

        nt.assert_true(True)



    def test_class_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        request = self.factory.get('/act/create')
        request.user = self.performer.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        response = bid_class(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Submit a Class' in response.content)
