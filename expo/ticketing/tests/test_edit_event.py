from django.http import Http404
import gbe.models as conf
import ticketing.models as tickets
import nose.tools as nt
from django.contrib.auth.models import Group
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import bptevent_edit
import factories
import mock

def location(response):
    response_dict = dict(response.items())
    return response_dict['Location']


class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.bpt_event = factories.BrownPaperEventsFactory.create()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)

    def get_bptevent_form(self):
        return {
                'primary': True,
                'act_submission_event': True,
                'vendor_submission_event': True,
                'linked_events': [],
                'include_conference': True,
                'include_most': True,
                'badgeable': True,
                'ticket_style': 'ticket style'
        }
    
    @nt.raises(Http404)
    def test_edit_event_user_is_not_ticketing(self):
        user = factories.ProfileFactory.create().user_object
        request = self.factory.get('/ticketing/bptevent_edit/%d'%self.bpt_event.pk)
        request.user = user
        response = bptevent_edit(request, self.bpt_event.pk)

    def test_edit_event_authorized_user(self):
        request = self.factory.get('/ticketing/bptevent_edit/%d'%self.bpt_event.pk)
        request.user =  self.privileged_user
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 200)

    @nt.raises(Http404)        
    def test_edit_event_bad_bptevent(self):
        request = self.factory.get('/ticketing/bptevent_edit/200')
        request.user =  self.privileged_user
        response = bptevent_edit(request, 200)

    def test_class_edit_post_form_all_good(self):
        # bptevent_edit, if form not valid, should return to ActEditForm
        request = self.factory.post('/ticketing/bptevent_edit/%d'%self.bpt_event.pk,
                                    self.get_bptevent_form())
        request.user = self.privileged_user
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/ticketing/ticket_items')


    def test_class_edit_post_form_bad_event(self):
        # bptevent_edit, if form not valid, should return to ActEditForm
        error_form = self.get_bptevent_form()
        error_form['linked_events'] = -1
        request = self.factory.post('/ticketing/bptevent_edit/%d'%self.bpt_event.pk,
                                    error_form)
        request.user = self.privileged_user
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Ticketing' in response.content)
        nt.assert_true(error_form.get('ticket_style') in response.content)
