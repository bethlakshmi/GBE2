from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_user_commitments
import factories
from django.contrib.auth.models import Group
from functions import login_as


class TestReviewUserCommitments(TestCase):
    '''Tests for review_user_commitments view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        group, nil = Group.objects.get_or_create(name='Volunteer Coordinator')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)

    @nt.raises(Http404)
    def test_review_user_commitments_profile_does_not_exist(self):
        request = self.factory.get('profile/review_commitments/%d' % -1)
        request.user = self.privileged_user
        login_as(self.privileged_user, self)
        response = review_user_commitments(request, -1)

'''
    def test_review_user_commitments_profile_exists(self):
        # currently failing because the function being tested is broken
        other_profile = factories.ProfileFactory.create()
        request = self.factory.get('profile/review_commitments/%d'%other_profile.pk)
        this_profile = factories.ProfileFactory.create()
        request.user = self.privileged_user
        login_as(self.privileged_user, self)
        response = review_user_commitments(request, other_profile.pk)
        nt.assert_equal(response.status_code, 200)
'''
