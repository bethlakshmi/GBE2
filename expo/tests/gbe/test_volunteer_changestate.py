from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import volunteer_changestate
from tests.factories import gbe_factories as factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface


class TestVolunteerChangestate(TestCase):
    '''Tests for volunteer_changestate view'''

    def setUp(self):
        pass

    def test_volunteer_changestate(self):
        # needs a little work to test
        pass
