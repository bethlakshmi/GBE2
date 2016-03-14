import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import propose_class
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

        request = self.factory.post('class/propose/')
        request.POST = self.get_class_form()
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = propose_class(request)
        nt.assert_equal(response.status_code, 200)
