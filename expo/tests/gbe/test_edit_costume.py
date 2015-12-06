from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from gbe.views import edit_costume
from gbetext import not_yours
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditCostume(TestCase):
    '''Tests for edit_costume view'''

    # this test case should be unnecessary, since edit_costume should go away
    # for now, test it.

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_costume_form(self):
        picture = SimpleUploadedFile("file.jpg",
                                     "file_content",
                                     content_type="image/jpg")
        return {'title': 'A costume',
                'creator': 'A creator',
                'description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }

    @nt.raises(Http404)
    def test_edit_costume_no_costume(self):
        '''Should get 404 if no valid costume ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/costume/edit/-1')
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        response = edit_costume(request, -1)

    def test_edit_costume_profile_is_not_contact(self):
        ''' Should get an error if the costume was not proposed by this user'''
        user = factories.ProfileFactory.create().user_object
        costume = factories.CostumeFactory.create()
        request = self.factory.get('/costume/edit/%d' % costume.pk)
        request.user = user
        request.session = {'cms_admin_site': 1}
        response = edit_costume(request, costume.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("You don&#39;t own that bid." in response.content)

    def test_costume_edit_post_form_not_valid(self):
        '''costume_edit, if form not valid, should return to ActEditForm'''
        costume = factories.CostumeFactory.create()
        request = self.factory.get('/costume/edit/%d' % costume.pk)
        request.user = costume.profile.user_object
        request.POST = {}
        request.POST.update(self.get_costume_form())
        request.session = {'cms_admin_site': 1}
        del(request.POST['title'])
        response = edit_costume(request, costume.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Displaying a Costume" in response.content)

    def test_edit_bid_post_no_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        costume = factories.CostumeFactory.create()
        request = self.factory.get('/costume/edit/%d' % costume.pk)
        request.user = costume.profile.user_object
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_costume_form())
        request.session = {'cms_admin_site': 1}
        response = edit_costume(request, costume.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')

    def test_edit_bid_not_post(self):
        '''edit_costume, not post, should take us to edit process'''
        costume = factories.CostumeFactory.create()
        request = self.factory.get('/costume/edit/%d' % costume.pk)
        request.user = costume.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = edit_costume(request, costume.pk)
        nt.assert_equal(response.status_code, 200)
        print(response.content)
        nt.assert_true('Displaying a Costume' in response.content)
