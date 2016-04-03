import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import(
    PersonaFactory,
    UserFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as
)


class TestEditCostume(TestCase):
    '''Tests for edit_costume view'''
    view_name = 'costume_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_costume_form(self, submit=False, invalid=False):
        picture = SimpleUploadedFile("file.jpg",
                                     "file_content",
                                     content_type="image/jpg")
        form = {'title': 'A costume',
                'creator': 'A creator',
                'description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }
        if submit:
            form['submit'] = 1
        if invalid:
            del(form['title'])

    def test_bid_costume_no_profile(self):
        '''costume_bid, when profile has no personae,
        should redirect to persona_create'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    # def test_costume_bid_post_form_not_valid(self):
    #     '''costume_bid, if form not valid, should return to CostumeEditForm'''
    #     url = reverse(self.view_name,
    #                   urlconf="gbe.urls")
    #     login_as(ProfileFactory(), self)
    #     data = self.get_costume_form(invalid=True)
    #     response = self.client.get(url)
    #     nt.assert_equal(response.status_code, 200)
    #     nt.assert_true('Displaying a Costume' in response.content)

    # def test_costume_bid_post_no_submit(self):
    #     '''costume_bid, not submitting and no other problems,
    #     should redirect to home'''
    #     url = reverse(self.view_name,
    #                   urlconf="gbe.urls")
    #     login_as(self.performer.performer_profile, self)
    #     response = self.client.get(url)
    #     nt.assert_equal(response.status_code, 302)
    #     nt.assert_equal(location(response), '/gbe')

    # def test_costume_bid_post_with_submit(self):
    #     '''costume_bid, not submitting and no other problems,
    #     should redirect to home'''
    #     url = reverse(self.view_name,
    #                   urlconf="gbe.urls")
    #     login_as(ProfileFactory(), self)
    #     data = self.get_costume_form(submit=True)
    #     response = self.client.get(url, data=data)
    #     nt.assert_equal(response.status_code, 200)
    #     nt.assert_true("Displaying a Costume" in response.content)

    def test_costume_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        nt.assert_equal(200, response.status_code)
        nt.assert_true('Displaying a Costume' in response.content)

    def test_costume_bid_no_persona(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(302, response.status_code)
