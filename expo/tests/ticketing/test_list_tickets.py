from django.http import Http404
from django.core.files import File
from django.core.exceptions import PermissionDenied
from ticketing.models import (
    BrownPaperEvents
)
import nose.tools as nt
from django.contrib.auth.models import Group
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import ticket_items
from tests.factories.gbe_factories import (
    ProfileFactory
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory
)
from tests.functions.gbe_functions import location
from mock import patch, Mock

class TestListTickets(TestCase):
    '''Tests for ticket_items view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = ProfileFactory.create().\
            user_object
        self.privileged_user.groups.add(group)

    @nt.raises(PermissionDenied)
    def test_list_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = ProfileFactory.create().user_object
        request = self.factory.get('/ticketing/ticket_items/')
        request.user = user
        response = ticket_items(request)

    def test_list_tickets_all_good(self):
        '''
           privileged user gets the list
        '''
        request = self.factory.get('/ticketing/ticket_items')
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)
        
    @patch('urllib2.urlopen', autospec=True)
    def test_get_inventory(self, m_urlopen):
        '''
           privileged user gets the inventory of tickets from (fake) BPT
        '''
        BrownPaperEvents.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml",'r')
        date_filename = open("tests/ticketing/datelist.xml",'r')
        price_filename = open("tests/ticketing/pricelist.xml",'r')
        a.read.side_effect = [File(event_filename).read(),
                              File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a
        
        request = self.factory.post('/ticketing/ticket_items',
                                    {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    def test_get_no_inventory(self):
        '''
           privileged user gets the inventory of tickets with no tickets
        '''
        BrownPaperEvents.objects.all().delete()

        request = self.factory.post('/ticketing/ticket_items',
                                    {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)
