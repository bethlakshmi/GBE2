import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_costume
from tests.factories.gbe_factories import (
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReviewCostume(TestCase):
    '''Tests for review_costume view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Costume Reviewers')

    def test_review_costume_all_well(self):
        costume = CostumeFactory()
        request = self.factory.get('costume/review/%d' % costume.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_costume(request, costume.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
