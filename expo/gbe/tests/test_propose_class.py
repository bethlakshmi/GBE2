from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import propose_class
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestProposeClass(TestCase):
    '''Tests for propose_class view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        registrar, created = Group.objects.get_or_create(name='Registrar')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(registrar)


    def get_class_form(self):
        return { 'name': 'someone@host.com',
                 'title': 'some class name', 
                 'proposal': 'some class description'
                 }
                 

    def test_propose_class(self):
        '''Basic up/down test for propose_class view - no login or profile required'''
        request= self.factory.get('class/propose/')
        request.method = "POST"
        request.POST = self.get_class_form()
        request.user = factories.UserFactory.create()
        response = propose_class(request)
        nt.assert_equal(response.status_code, 200)
        

    
        
        

