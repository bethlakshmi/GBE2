from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_event
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)


class TestCreateEvent(TestCase):
    '''Tests for create_event view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        group, created = Group.objects.get_or_create(name='Scheduling Mavens')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)

    def test_authorized_user_can_access(self):
        request= self.factory.get('create_event/Show')
        request.user = self.privileged_user
        response = create_event(request, 'Show')
        nt.assert_equal(response.status_code, 200)    

    def test_auth_user_can_create_show(self):
        request = self.factory.post('create_event/Show')
        request.user = self.privileged_user
        title = 'The Big Show'
        request.POST['title'] = title
        description = 'Really Big Show'
        request.POST['description'] = description
        duration = '2:00:00'
        request.POST['duration'] = duration
        create_event(request, 'Show')
        nt.assert_true(conf.Show.objects.filter(title=title).count() > 0)
