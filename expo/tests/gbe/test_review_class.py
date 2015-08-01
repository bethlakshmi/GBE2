import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_class
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestReviewClass(TestCase):
    '''Tests for review_class view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        class_reviewers = Group(name='Class Reviewers')
        class_reviewers.save()
        self.privileged_user.groups.add(class_reviewers)

    def test_review_act_all_well(self):
        klass = factories.ClassFactory.create()
        request = self.factory.get('class/review/%d' % klass.pk)
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
