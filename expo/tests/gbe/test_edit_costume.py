import nose.tools as nt
from unittest import TestCase
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditCostume(TestCase):
    '''Tests for edit_costume view'''
    view_name = 'costume_edit'

    # this test case should be unnecessary, since edit_costume should go away
    # for now, test it.

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_costume_form(self, submit=False, invalid=False):
        picture = SimpleUploadedFile("file.jpg",
                                     "file_content",
                                     content_type="image/jpg")
        data = {'title': 'A costume',
                'creator': 'A creator',
                'description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }
        if invalid:
            del(data['title'])
        if submit:
            data['submit'] = 1

        return data

    def test_edit_costume_no_costume(self):
        '''Should get 404 if no valid costume ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 404)

    def test_edit_costume_profile_is_not_contact(self):
        ''' Should get an error if the costume was not proposed by this user'''
        costume = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("You don&#39;t own that bid." in response.content)

    def test_edit_costume_no_profile(self):
        costume = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_costume_edit_post_form_not_valid(self):
        '''costume_edit, if form not valid, should return to ActEditForm'''
        costume = CostumeFactory()
        PersonaFactory(performer_profile=costume.profile,
                       contact=costume.profile)
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(invalid=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        error_string = "This bid is not one of your stage names"
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(error_string in response.content)

    def test_edit_bid_post_no_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(submit=False)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        'http://testserver/gbe')

    def test_edit_bid_post_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(submit=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        'http://testserver/gbe')

    def test_edit_bid_post_invalid(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(invalid=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        expected_string = "Costume Information"
        nt.assert_true(expected_string in response.content)
        nt.assert_equal(response.status_code, 200)

    def test_edit_bid_not_post(self):
        '''edit_costume, not post, should take us to edit process'''
        costume = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form()
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        error_text = "Great Burlesque Exposition: Error!"
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(error_text in response.content)
