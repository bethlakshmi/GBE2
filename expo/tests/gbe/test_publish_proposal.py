from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import publish_proposal
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestPublishProposal(TestCase):
    '''Tests for publish_proposal view'''

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

    def test_publish_proposal_not_post(self):
        proposal = factories.ClassProposalFactory.create()
        request= self.factory.get('classpropose/edit/%d' % proposal.pk)
        request.user =  self.privileged_user
        response = publish_proposal(request, proposal.pk)
        nt.assert_equal(response.status_code, 200)
        
    def test_publish_proposal_post_invalid_form(self):
        proposal = factories.ClassProposalFactory.create()
        request= self.factory.get('classpropose/edit/%d' % proposal.pk)
        request.user = self.privileged_user
        request.method = "POST"
        response = publish_proposal(request,  proposal.pk)
        nt.assert_equal(response.status_code, 200)

    def test_publish_proposal_post_valid_form(self):
        proposal = factories.ClassProposalFactory.create()
        request= self.factory.get('classpropose/edit/%d' % proposal.pk)
        request.user = self.privileged_user
        request.method = "POST"
        request.POST = self.get_class_form()
        response = publish_proposal(request, proposal.pk)
        nt.assert_equal(response.status_code, 200)
        

    
        
        


