import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_costume_list
from django.contrib.auth.models import Group
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import login_as
from django.core.exceptions import PermissionDenied


class TestReviewCostumeList(TestCase):
    '''Tests for review_costume_list view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Costume Reviewers')
        self.privileged_user.groups.add(group)

    def test_review_costume_all_well(self):
        request = self.factory.get('costume/review/')
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_costume_list(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    @nt.raises(PermissionDenied)
    def test_review_costume_baduser(self):
        request = self.factory.get('costume/review/')
        request.user = factories.ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_costume_list(request)

    @nt.raises(PermissionDenied)
    def test_review_costume_no_profile(self):
        request = self.factory.get('costume/review/')
        request.user = factories.UserFactory.create()
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_costume_list(request)