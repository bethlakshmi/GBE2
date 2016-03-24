from django.core.exceptions import PermissionDenied

import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from gbe.report_views import personal_schedule
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TransactionFactory,
    TicketingEligibilityConditionFactory
)
from tests.functions.scheduler_functions import book_worker_item_for_role
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as
)


class TestPersonalSchedule(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.priv_profile = ProfileFactory()
        grant_privilege(self.priv_profile, 'Act Reviewers')

    @nt.raises(PermissionDenied)
    def test_personal_schedule_fail(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/schedule_all')
        login_as(profile, self)
        request.user = profile.user_object
        response = personal_schedule(request)

    def test_personal_schedule_succeed(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        request = self.factory.get('reports/schedule_all')
        login_as(self.priv_profile, self)
        request.user = self.priv_profile.user_object

        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)

    def test_personal_schedule_teacher_checklist(self):
        '''a teacher booked into a class, with an active role condition
           should get a checklist item
        '''
        role_condition = RoleEligibilityConditionFactory()
        teacher = PersonaFactory()
        booking = book_worker_item_for_role(teacher,
                                            role_condition.role)
        conference = booking.event.eventitem.get_conference()

        request = self.factory.get('reports/schedule_all')
        login_as(self.priv_profile, self)
        request.user = self.priv_profile.user_object

        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(
            str(role_condition.checklistitem) in response.content,
            msg="Role condition for teacher was not found")
        nt.assert_true(
            str(teacher.performer_profile) in response.content,
            msg="Teacher is not in the list")

    def test_personal_schedule_teacher_booking(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        teacher = PersonaFactory()
        booking = book_worker_item_for_role(teacher,
                                            role_condition.role)
        conference = booking.event.eventitem.get_conference()

        request = self.factory.get(
            'reports/schedule_all?conf_slug='+conference.conference_slug)
        login_as(self.priv_profile, self)
        request.user = self.priv_profile.user_object

        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(
            str(teacher.performer_profile) in response.content,
            msg="Teacher is not in the list")
        nt.assert_true(
            str(booking.event) in response.content)
        nt.assert_true(
            str(booking.event.location) in response.content)

    def test_ticket_purchase(self):
        '''a ticket purchaser gets a checklist item
        '''
        transaction = TransactionFactory()
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.bpt_event.conference
        ticket_condition = TicketingEligibilityConditionFactory(
            tickets=[transaction.ticket_item]
        )

        request = self.factory.get(
            'reports/schedule_all?conf_slug='+conference.conference_slug)
        login_as(self.priv_profile, self)
        request.user = self.priv_profile.user_object

        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(
            str(purchaser) in response.content,
            msg="Buyer is not in the list")
        nt.assert_true(
            str(ticket_condition.checklistitem) in response.content)

    def test_one_person(self):
        '''placeholder for the day when I can make that work
        '''
        request = self.factory.get(
            'reports/schedule_all')
        login_as(self.priv_profile, self)
        request.user = self.priv_profile.user_object

        response = personal_schedule(request, self.priv_profile.pk)
        self.assertEqual(response.status_code, 200)
