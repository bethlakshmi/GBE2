from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_proposal_list
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestReviewProposalList(TestCase):
    '''Tests for review_proposal_list view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        class_coordinator, created = Group.objects.get_or_create(name='Class Coordinator')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(class_coordinator)

    def get_class_form(self):
        return { 'name': 'someone@host.com',
                 'title': 'some class name', 
                 'proposal': 'some class description'
                 }

    def test_review_proposal_list_authorized_user(self):
        proposal = factories.ClassProposalFactory.create()
        request= self.factory.get('classpropose/reviewlist/')
        request.user =  self.privileged_user
        response = review_proposal_list(request)
        nt.assert_equal(response.status_code, 200)    
        
        


