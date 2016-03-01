from django.core.files import File
from ticketing.models import (
    BrownPaperEvents,
    BrownPaperSettings,
    TicketItem,
    Transaction
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory
)
import nose.tools as nt
from unittest import TestCase
from ticketing.views import process_bpt_order_list
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory
)
from tests.functions.gbe_functions import location
from mock import patch, Mock
import urllib2
from django.shortcuts import get_object_or_404


class TestProcessBPTOrderList(TestCase):
    '''Tests processing BPT Order list (the cron job)'''

    def test_get_no_events(self):
        '''
           no events are available to process
        '''
        BrownPaperEvents.objects.all().delete()

        nt.assert_equal(process_bpt_order_list(), 0)

    @patch('urllib2.urlopen', autospec=True)
    def test_get_transaction_limbo(self, m_urlopen):
        '''
           get a transaction for the limbo user
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        ticket = TicketItemFactory(
            bpt_event=event,
            ticket_id='%s-%s' % (event.bpt_event_id, '3255985'))
        BrownPaperSettingsFactory()
        limbo = UserFactory(username='limbo')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        nt.assert_equal(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        nt.assert_equal(str(transaction.order_date),
                        "2014-08-16 00:26:56+00:00")
        nt.assert_equal(transaction.shipping_method, 'Will Call')
        nt.assert_equal(transaction.order_notes, 'None')
        nt.assert_equal(transaction.payment_source, 'Brown Paper Tickets')
        nt.assert_equal(transaction.purchaser.email, 'test@tickets.com')
        nt.assert_equal(transaction.purchaser.phone, '111-222-3333')
        nt.assert_equal(transaction.purchaser.matched_to_user, limbo)
        nt.assert_equal(transaction.purchaser.first_name, 'John')
        nt.assert_equal(transaction.purchaser.last_name, 'Smith')

    @patch('urllib2.urlopen', autospec=True)
    def test_get_transaction_user(self, m_urlopen):
        '''
           get a transaction for a real user
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        ticket = TicketItemFactory(
            bpt_event=event,
            ticket_id='%s-%s' % (event.bpt_event_id, '3255985'))
        BrownPaperSettingsFactory()
        profile = ProfileFactory(purchase_email='test@tickets.com')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        nt.assert_equal(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        nt.assert_equal(str(transaction.order_date),
                        "2014-08-16 00:26:56+00:00")
        nt.assert_equal(transaction.shipping_method, 'Will Call')
        nt.assert_equal(transaction.order_notes, 'None')
        nt.assert_equal(transaction.payment_source, 'Brown Paper Tickets')
        nt.assert_equal(transaction.purchaser.email, 'test@tickets.com')
        nt.assert_equal(transaction.purchaser.phone, '111-222-3333')
        nt.assert_equal(transaction.purchaser.matched_to_user,
                        profile.user_object)
        nt.assert_equal(transaction.purchaser.first_name, 'John')
        nt.assert_equal(transaction.purchaser.last_name, 'Smith')
        profile.user_object.delete()
