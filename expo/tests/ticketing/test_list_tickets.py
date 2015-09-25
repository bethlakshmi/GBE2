from django.http import Http404
from django.core.exceptions import PermissionDenied
import gbe.models as conf
import ticketing.models as tickets
import nose.tools as nt
from django.contrib.auth.models import Group
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import ticket_items
from tests.factories import gbe_factories, ticketing_factories
from tests.functions.gbe_functions import location
import mock


class TestListTickets(TestCase):
    '''Tests for ticket_items view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = gbe_factories.ProfileFactory.create().\
            user_object
        self.privileged_user.groups.add(group)

    @nt.raises(PermissionDenied)
    def test_list_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = gbe_factories.ProfileFactory.create().user_object
        request = self.factory.get('/ticketing/ticket_items/')
        request.user = user
        response = ticket_items(request)

    def test_list_tickets_all_good(self):
        '''
           privileged user gets the list
        '''
        request = self.factory.get('/ticketing/ticket_items')
        request.user = self.privileged_user
        request.session = {'cms_admin_site':1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)
