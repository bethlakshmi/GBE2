import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from gbe.views import bid_costume
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (
    location,
    login_as
)


class TestEditCostume(TestCase):
    '''Tests for edit_costume view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_costume_form(self):
        picture = SimpleUploadedFile("file.jpg", "file_content", content_type="image/jpg")
        return {'title': 'A costume',
                'description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }

    def test_bid_costume_no_profile(self):
        '''costume_bid, when profile has no personae,
        should redirect to persona_create'''
        request = self.factory.get('costume/create/')
        request.user = factories.UserFactory.create()
        response = bid_costume(request)
        nt.assert_equal(response.status_code, 302)


    def test_costume_bid_post_form_not_valid(self):
        '''costume_bid, if form not valid, should return to CostumeEditForm'''
        request = self.factory.get('/costume/create')
        request.user = self.performer.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_costume_form())
        request.session = {'cms_admin_site':1}
        del(request.POST['title'])
        response = bid_costume(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Displaying a Costume' in response.content)

    def test_costume_bid_post_no_submit(self):
        '''costume_bid, not submitting and no other problems,
        should redirect to home'''
        request = self.factory.get('/costume/create')
        request.user = self.performer.performer_profile.user_object
        login_as(request.user, self)
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_costume_form())
        request.session = {'cms_admin_site':1}
        response = bid_costume(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')

    def test_costume_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        request = self.factory.get('/act/create')
        request.user = self.performer.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        response = bid_costume(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Displaying a Costume' in response.content)
