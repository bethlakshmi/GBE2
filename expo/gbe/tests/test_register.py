from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import register
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestRegister(TestCase):
    '''Tests for register  view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        registrar, created = Group.objects.get_or_create(name='Registrar')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(registrar)


    def test_register_not_post(self):
        request= self.factory.get('accounts/register')
        request.user = factories.UserFactory.create()
        response = register(request)
        nt.assert_equal(response.status_code, 200)
        

    
        
        

