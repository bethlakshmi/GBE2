from django.http import Http404
from django.core.exceptions import PermissionDenied
from ticketing.models import *
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.ticketing_factories import (
    TicketingExclusionFactory,
    RoleExclusionFactory,
    TicketItemFactory,
    NoEventRoleExclusionFactory
)
from tests.factories.gbe_factories import (
    ClassFactory
)
from gbe.models import Class
from scheduler.models import(
    Worker,
    Event as sEvent,
    ResourceAllocation
)
from datetime import datetime
import pytz


class TestIsExcluded(TestCase):
    '''Tests for exclusions in all Exclusion subclasses'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.ticketingexclusion = TicketingExclusionFactory.create()
        self.roleexclusion = RoleExclusionFactory.create()
        # Class Factory not working here - event not created and attached
        self.this_class = Class.objects.all().first()
        self.this_class.save()
        current_sched = sEvent(
            eventitem=self.this_class,
            starttime=datetime(2016, 2, 5, 12, 0, 0, 0, pytz.utc))
        current_sched.save()
        worker = Worker(_item=self.this_class.teacher,
                              role='Teacher')
        worker.save()
        teacher_assignment = ResourceAllocation(
            event=current_sched,
            resource=worker
        )
        teacher_assignment.save()
        self.roleexclusion.event = self.this_class
        self.roleexclusion.event.save()


    def test_no_ticket_excluded(self):
        '''
            the ticket is not in the excluded set
        '''
        diff_ticket = TicketItemFactory.create()
        nt.assert_false(self.ticketingexclusion.is_excluded([diff_ticket]))

    def test_ticket_is_excluded(self):
        '''
           a ticket in the held tickets matches the exclusion set
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        nt.assert_true(
            self.ticketingexclusion.is_excluded([problem_ticket]))

    def test_role_is_excluded(self):
        '''
           role matches, no event is present, exclusion happens
        '''
        no_event = NoEventRoleExclusionFactory.create()
        nt.assert_true(no_event.is_excluded(
            self.this_class.teacher.performer_profile,
            self.this_class.conference))

    def test_role_not_event(self):
        '''
           role matches but event does not, not excluded
           Fix after Expo
        '''
        new_exclude = RoleExclusionFactory.create()

        '''
        nt.assert_false(new_exclude.is_excluded(
            self.this_class.teacher.performer_profile,
            self.this_class.conference))
        '''

    def test_no_role_match(self):
        '''
            role does not match, not excluded
        '''
        no_event = NoEventRoleExclusionFactory.create(role="Vendor")
        nt.assert_false(no_event.is_excluded(
            self.this_class.teacher.performer_profile,
            self.this_class.conference))

    def test_role_and_event_match(self):
        '''
            role and event match the exclusion

            Fix after expo
        '''
        '''

        nt.assert_true(self.roleexclusion.is_excluded(
            self.this_class.teacher.performer_profile,
            self.this_class.conference))
        '''
