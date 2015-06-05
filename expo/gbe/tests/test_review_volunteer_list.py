from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_volunteer_list
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestReviewVolunteerList(TestCase):
    '''Tests for review_volunteer_list view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        volunteer_reviewers = get_object_or_404(Group, name='Volunteer Reviewers')
        self.privileged_user.groups.add(volunteer_reviewers)

    def test_review_volunteer_all_well(self):
        request = self.factory.get('volunteer/review/')
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_volunteer_list(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
