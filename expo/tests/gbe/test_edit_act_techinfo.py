from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_act_techinfo
import factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestReviewProposalList(TestCase):
    '''Tests for edit_act_techinfo view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()


'''
# this is a little tricky...
    def test_edit_act_techinfo_authorized_user(self):
        act = factories.ActFactory.create()
        show = factories.ShowFactory.create()
        show.acts.add(act)
        request= self.factory.get('act/changestate/%d' %act.pk)
        request.user =  act.performer.performer_profile.user_object
        mock_get_shows = mock.MagicMock(return_value = [])
        with mock.patch ('scheduler.models.ActItem.get_scheduled_shows', mock_get_shows):
            response = edit_act_techinfo(request, act.pk)
        nt.assert_equal(response.status_code, 302)        


'''     
    


