import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)


class TestProposeClass(TestCase):
    '''Tests for propose_class view'''
    view_name = 'class_propose'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def get_class_form(self, valid=True):
        data = {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description',
                'type': 'Class',
                }
        if not valid:
            del(data['type'])
        return data


    def test_propose_invalid_class(self):
        current_conference()
        url = reverse(self.view_name, urlconf="gbe.urls")
        data = self.get_class_form(valid=False)
        login_as(UserFactory(), self)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)

    def test_propose_valid_class(self):
        current_conference()
        url = reverse(self.view_name, urlconf="gbe.urls")
        data = self.get_class_form(valid=True)
        login_as(UserFactory(), self)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Profile View" in response.content)

    def test_propose_class_get(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("I've Got An Idea!" in response.content)
