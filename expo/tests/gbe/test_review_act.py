import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_act
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    ActFactory,
)
from tests.functions.gbe_functions import login_as


class TestReviewAct(TestCase):
    '''Tests for revview_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Act Reviewers')
        self.privileged_user.groups.add(group)
        group, nil = Group.objects.get_or_create(name='Act Coordinator')
        self.privileged_user.groups.add(group)

    def test_review_act_all_well(self):
        act = ActFactory.create()
        request = self.factory.get('act/review/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
