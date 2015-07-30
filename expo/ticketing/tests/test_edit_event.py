from django.http import Http404
import gbe.models as conf
import ticketing.models as tickets
import nose.tools as nt
from unittest import TestCase
from django.contrib.auth.models import Group
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import bptevent_edit
import factories
import mock

#from gbe.tests.functions import (location)

class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.bpt_event = factories.BrownPaperEventsFactory.create()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(group)


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

'''
    def test_class_edit_post_form_not_valid(self):
        # class_edit, if form not valid, should return to ActEditForm
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_class_form())
        del(request.POST['title'])
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)

    def test_edit_bid_post_no_submit(self):
        #act_bid, not submitting and no other problems, should redirect to home
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.contact.user_object
        request.method='POST'
        request.POST = {}
        request.POST.update(self.get_class_form())
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')

    def test_edit_bid_not_post(self):
        #edit_bid, not post, should take us to edit process
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.contact.user_object
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)
'''
