from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import act_changestate
import factories
import mock
from django.contrib.auth.models import Group
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)


class TestClassChangestate(TestCase):
    '''Tests for act_changestate view'''

    def setUp(self):
        pass

    def test_class_changestate(self):
        # needs a little work to test
        pass
