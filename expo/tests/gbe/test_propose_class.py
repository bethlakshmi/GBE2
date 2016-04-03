import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestProposeClass(TestCase):
    '''Tests for propose_class view'''
    view_name='class_propose'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_propose_class(self):
        '''Basic up/down test for propose_class view -
        no login or profile required'''
        url = reverse (self.view_name, urlconf="gbe.urls")
        data = self.get_class_form()
        login_as(UserFactory(), self)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)
