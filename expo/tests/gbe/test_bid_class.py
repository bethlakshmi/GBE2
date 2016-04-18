import nose.tools as nt
from unittest import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as
)


class TestBidClass(TestCase):
    '''Tests for edit_class view'''
    view_name = 'class_create'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.teacher = PersonaFactory()
        self.conference = ConferenceFactory(accepting_bids=True)

    def get_class_form(self, submit=False, invalid=False, incomplete=False):
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
        redirect = (('http://testserver/performer/create?next=/class/create', 302))
        nt.assert_true(redirect in response.redirect_chain)
        expected_string = "Tell Us About Your Stage Persona"
        nt.assert_true(expected_string in response.content)
        nt.assert_equal(response.status_code, 200)

    # def test_class_bid_post_form_not_valid(self):
    #     '''class_bid, if form not valid, should return to ClassEditForm'''
    #     url = reverse(self.view_name,
    #                   urlconf='gbe.urls')

    #     login_as(self.performer.performer_profile, self)
    #     request.POST = {}
    #     request.POST.update(self.get_class_form())
    #     request.session = {'cms_admin_site': 1}
    #     del(request.POST['title'])
    #     response = bid_class(request)
    #     nt.assert_equal(response.status_code, 200)
    #     nt.assert_true('Submit a Class' in response.content)

    # def test_class_bid_post_no_submit(self):
    #     '''class_bid, not submitting and no other problems,
    #     should redirect to home'''
    #     url = reverse(self.view_name,
    #                   urlconf='gbe.urls')

    #     request.user = self.performer.performer_profile.user_object
    #     login_as(request.user, self)
    #     data = self.get_class_form(submit=False)
    #     response = self.client.post(url, data=data, follow=True)
    #     nt.assert_equal(response.status_code, 302)
    #     nt.assert_equal(location(response), '/gbe')

    def test_class_bid_post_with_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=True)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_equal(response.status_code, 200)
        # stricter test required here

    def test_class_bid_post_with_submit_incomplete(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        data = self.get_class_form(submit=True, invalid=True)
        user = self.performer.performer_profile.user_object
        login_as(user, self)
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        expected_string = "This field is required"
        nt.assert_true(expected_string in response.content)

    def test_class_bid_post_no_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=False)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_equal(200, response.status_code)
        nt.assert_true('Profile View' in response.content)

    def test_class_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Submit a Class' in response.content)
