import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    PersonaFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditClass(TestCase):
    '''Tests for edit_class view'''
    view_name = 'class_edit'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.teacher = PersonaFactory()

    def get_form(self, submit=True, invalid=False):
        data = {"teacher": self.teacher.pk,
                "title": 'A class',
                "description": 'a description',
                "length_minutes": 60,
                'maximum_enrollment': 20,
                'fee': 0,
                'schedule_constraints': ['0'],
                }
        if submit:
            data['submit'] = 1
        if invalid:
            del(data['title'])
        return data

    def test_edit_class_no_class(self):
        '''Should get 404 if no valid class ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_edit_class_profile_is_not_contact(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_class_edit_post_form_not_valid(self):
        '''class_edit, if form not valid, should return to ActEditForm'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)

    def test_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        data = self.get_form(submit=False)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), 'http://testserver/gbe')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)

    def test_edit_class_post_with_submit(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        data = self.get_form()
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), 'http://testserver/gbe')
        # should test some change to class

    def test_edit_bid_verify_info_popup_text(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('We will do our best to accommodate' in response.content)

    def test_edit_bid_verify_avoided_constraints(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('I Would Prefer to Avoid' in response.content)
