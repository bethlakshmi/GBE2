from django.http import Http404
from django.core.files import File
from django.core.exceptions import PermissionDenied
from ticketing.models import (
    BrownPaperEvents,
    BrownPaperSettings,
    TicketItem
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory
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
from tests.functions.gbe_functions import location
from mock import patch, Mock
import urllib2
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.core.urlresolvers import reverse


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
        request = self.factory.get(
            reverse('ticket_items', urlconf='ticketing.urls'),
        )
        request.user = user
        response = ticket_items(request)

    def test_list_tickets_all_good(self):
        '''
           privileged user gets the list
        '''
        request = self.factory.get(
            reverse('ticket_items', urlconf='ticketing.urls'),)
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
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        price_filename = open("tests/ticketing/pricelist.xml", 'r')
        a.read.side_effect = [File(event_filename).read(),
                              File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)
        ticket = get_object_or_404(
            TicketItem,
            ticket_id='%s-4513068' % (event.bpt_event_id))
        nt.assert_equal(response.status_code, 200)
        nt.assert_equal(ticket.cost, Decimal('125.00'))
        nt.assert_in(
            "The Great Burlesque Exposition of 2016 takes place Feb. 5-7",
            ticket.description)

    def test_get_no_inventory(self):
        '''
           privileged user gets the inventory of tickets with no tickets
        '''
        BrownPaperEvents.objects.all().delete()

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_no_event_list(self, m_urlopen):
        '''
           not event list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = []
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_no_date_list(self, m_urlopen):
        '''
           not date list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_no_price_list(self, m_urlopen):
        '''
           not price list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        a.read.side_effect = [File(event_filename).read(),
                              File(date_filename).read()]
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_urlerror(self, m_urlopen):
        '''
           first read from BPT has a URL read error
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = urllib2.URLError("test url error")
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_no_settings(self, m_urlopen):
        '''
           not date list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        request = self.factory.post(
            reverse('ticket_items', urlconf='ticketing.urls'),
            {'Import': 'Import'})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(request)
        nt.assert_equal(response.status_code, 200)

    def test_list_tickets_for_conf(self):
        '''
           privileged user gets the list for a conference
        '''
        ticket = TicketItemFactory()
        request = self.factory.get(
            reverse('ticket_items',
                    urlconf='ticketing.urls',
                    args=[str(ticket.bpt_event.conference.conference_slug)]))
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = ticket_items(
            request,
            ticket.bpt_event.conference.conference_slug)
        nt.assert_equal(response.status_code, 200)
