from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_event
import factories
from django.contrib.auth.models import Group


class TestCreateEvent(TestCase):
    '''Tests for create_event view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        group, created = Group.objects.get_or_create(name='Scheduling Mavens')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)

    def test_create_event_authorized_user(self):
        request = self.factory.get('create_event/Show')
        request.user = self.privileged_user
        response = create_event(request, 'Show')
        nt.assert_equal(response.status_code, 200)
