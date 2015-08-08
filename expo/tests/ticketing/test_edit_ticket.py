from django.http import Http404
import gbe.models as conf
import ticketing.models as tickets
import nose.tools as nt
from django.contrib.auth.models import Group
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import ticket_item_edit
from tests.factories import gbe_factories, ticketing_factories
from tests.functions.gbe_functions import location
import mock
import gbe.tests as gbe_tests



class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.ticketitem = ticketing_factories.TicketItemFactory.create()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = gbe_factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)

    def get_ticketitem_form(self):
        return {
                'ticket_id': "333333-444444",
                'title': "Title from Form",
                'description': "Description from Form",
                'active': False,
                'cost': 1.01,
                'bpt_event': self.ticketitem.bpt_event.pk
        }
    
    @nt.raises(Http404)
    def test_edit_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Fail with a 404
        '''
        user = gbe_factories.ProfileFactory.create().user_object
        request = self.factory.get('/ticketing/ticket_item_edit/%d'%self.ticketitem.pk)
        request.user = user
        response = ticket_item_edit(request, self.ticketitem.pk)

    @nt.raises(Http404)        
    def test_edit_ticket_bad_ticketitem(self):
        '''
           Unknown ticket item submitted by valid user, should have an error
           and resend same form (status 200)
        '''
        request = self.factory.get('/ticketing/ticket_item_edit/200')
        request.user =  self.privileged_user
        response = ticket_item_edit(request, 200)

    def test_ticket_edit_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        request = self.factory.post('/ticketing/ticket_item_edit/%d'%self.ticketitem.pk,
                                    self.get_ticketitem_form())
        request.user = self.privileged_user
        response = ticket_item_edit(request, self.ticketitem.pk)
        print(response)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/ticketing/ticket_items')


    def test_ticket_edit_post_form_bad_bptevent(self):
        '''
            Invalid form data submitted, fail with error and return form
        '''
        error_form = self.get_ticketitem_form()
        error_form['bpt_event'] = -1
        request = self.factory.post('/ticketing/ticket_item_edit/%d'%self.ticketitem.pk,
                                    error_form)
        request.user = self.privileged_user
        response = ticket_item_edit(request, self.ticketitem.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Ticketing' in response.content)
        nt.assert_true(error_form.get('title') in response.content)
