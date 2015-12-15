from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import class_changestate
import mock
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from tests.factories.gbe_factories import (
    ClassFactory,
    ProfileFactory
)


class TestClassChangestate(TestCase):
    '''Tests for act_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.klass = ClassFactory.create()
        self.privileged_user = ProfileFactory.create().user_object
        group, nil = Group.objects.get_or_create(name='Class Coordinator')
        self.privileged_user.groups.add(group)

    def test_class_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        request = self.factory.get('class/changestate/%d' % self.klass.pk)
        request.user = self.privileged_user
        response = class_changestate(request, self.klass.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(PermissionDenied)
    def test_class_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        request = self.factory.get('class/changestate/%d' % self.klass.pk)
        request.user = ProfileFactory.create().user_object
        response = class_changestate(request, self.klass.pk)
