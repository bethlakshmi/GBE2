from pytz import utc
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from datetime import (
    datetime,
    time,
    date,
)

import gbe.models as conf
import nose.tools as nt
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.http import Http404
from gbe.report_views import (list_reports,
                              review_staff_area,
                              staff_area,
                              env_stuff,
                              review_act_techinfo,
                              export_act_techinfo,
                              room_schedule,
                              room_setup,
                              export_badge_report,
                              )
from tests.factories import gbe_factories as factories
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ShowFactory,

)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.factories.ticketing_factories import (
    TransactionFactory,
    )
import ticketing.models as tix

import tests.functions.gbe_functions as functions


def _create_scheduled_show_with_acts(conference=None, qty=6):
    if not conference:
        conference = ConferenceFactory.create()
    conf_day = ConferenceDayFactory.create(
        conference=conference)

    show = ShowFactory.create(conference=conference)
    sEvent = SchedEventFactory.create(
        eventitem=show.eventitem_ptr,
        starttime=utc.localize(datetime.combine(conf_day.day, time(20, 0))))
    acts = [ActFactory.create(accepted=3) for i in range(qty)]
    for act in acts:
        ar = ActResourceFactory.create(_item=act.actitem_ptr)
        ResourceAllocationFactory.create(
            event=sEvent,
            resource=ar)
    return show, sEvent, acts


class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.profile_factory = factories.ProfileFactory
        self.client = Client()

    def create_transaction(self):
        transaction = TransactionFactory.create()
        transaction.ticket_item.bpt_event.badgeable = True
        transaction.save()
        transaction.ticket_item.bpt_event.save()
        profile_buyer = self.profile_factory.create()
        profile_buyer.user_object = transaction.purchaser.matched_to_user
        profile_buyer.save()

        return transaction

    @nt.raises(PermissionDenied)
    def test_list_reports_fail(self):
        '''list_reports view should fail because user
           is not in one of the privileged groups
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = list_reports(request)

    def test_list_reports_succeed(self):
        '''list_reports view should load, user has proper
           privileges
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/')
        functions.login_as(profile, self)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        response = list_reports(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_review_staff_area_not_visible_without_permission(self):
        profile = self.profile_factory.create()
        request = self.factory.get('reports/review_staff_area')
        functions.login_as(profile, self)
        request.user = profile.user_object
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = review_staff_area(request)

    def test_review_staff_area_path(self):
        '''review_staff_area view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/review_staff_area')
        functions.login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        functions.grant_privilege(profile, 'Act Reviewers')
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = review_staff_area(request)
        self.assertEqual(response.status_code, 200)

    def test_staff_area_path(self):
        '''staff_area view should load
        '''
        nt.assert_true(date.today() < date (2016, 3, 1),
                       msg="Time to fix test_staff_area!")
        
        profile = self.profile_factory.create()
        show = factories.ShowFactory.create()
        request = self.factory.get('reports/staff_area/%d' % show.eventitem_id)
        functions.login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        functions.grant_privilege(profile, 'Act Reviewers')
        response = staff_area(request, show.eventitem_id)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_staff_area_path_fail(self):
        '''staff_area view should fail for non-authenticated users
        '''
        profile = self.profile_factory.create()
        show = factories.ShowFactory.create()
        request = self.factory.get('reports/staff_area/%d' % show.eventitem_id)
        functions.login_as(profile, self)
        request.user = profile.user_object
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = staff_area(request, show.eventitem_id)

    @nt.raises(PermissionDenied)
    def test_env_stuff_fail(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/stuffing')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = env_stuff(request)

    def test_env_stuff_succeed(self):
        '''env_stuff view should load with no conf choice
        '''
        profile = self.profile_factory.create()
        transaction = self.create_transaction()
        request = self.factory.get('reports/stuffing')
        functions.login_as(profile, self)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Registrar')
        response = env_stuff(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertIn(
            "Badge Name,First,Last,Tickets,Ticket format,Personae," +
            "Staff Lead,Volunteering,Presenter,Show",
            response.content)
        self.assertIn(
            transaction.purchaser.matched_to_user.first_name,
            response.content)
        self.assertIn(
            transaction.ticket_item.title,
            response.content)

    def test_env_stuff_succeed_w_conf(self):
        '''env_stuff view should load for a selected conference slug
        '''
        profile = self.profile_factory.create()
        transaction = self.create_transaction()
        request = self.factory.get(
            'reports/stuffing/%s/'
            % transaction.ticket_item.bpt_event.conference.conference_slug)

        functions.login_as(profile, self)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Registrar')
        response = env_stuff(
            request,
            transaction.ticket_item.bpt_event.conference.conference_slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertIn(
            "Badge Name,First,Last,Tickets,Ticket format,Personae," +
            "Staff Lead,Volunteering,Presenter,Show",
            response.content)
        self.assertIn(
            transaction.purchaser.matched_to_user.first_name,
            response.content)
        self.assertIn(
            transaction.ticket_item.title,
            response.content)

    @nt.raises(PermissionDenied)
    def test_review_act_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.report_urls'))
        request.user = profile.user_object
        response = review_act_techinfo(request)

    def test_review_act_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.report_urls'))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        functions.grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)

    def test_review_act_techinfo_has_datatable(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        curr_conf = ConferenceFactory.create()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.report_urls',
                    args=[curr_show.eventitem_id]))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        request.GET = {'conf_slug': curr_conf.conference_slug}
        functions.grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request, curr_show.eventitem_id)
        nt.assert_true(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        nt.assert_true(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")

    def test_review_act_techinfo_with_conference_slug(self):
        '''review_act_techinfo view show correct events for slug
        '''
        curr_conf = ConferenceFactory.create()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        old_conf = ConferenceFactory.create(status='completed')
        old_show, _, old_acts = _create_scheduled_show_with_acts(old_conf)

        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.report_urls'))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        request.GET = {'conf_slug': curr_conf.conference_slug}
        functions.grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(curr_show.title in response.content)

    @nt.raises(PermissionDenied)
    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = room_schedule(request)

    def test_room_schedule_succeed(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = room_schedule(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_room_setup_not_visible_without_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = room_setup(request)

    def test_room_setup_visible_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        current_conference = factories.ConferenceFactory.create()
        current_conference.save()
        response = room_setup(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_export_badge_report_fail(self):
        '''export_badge_report view should fail for users w/out
        Registrar role
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/badges/print_run')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = export_badge_report(request)

    def test_export_badge_report_succeed_w_conf(self):
        '''get badges w a specific conference
        '''
        profile = self.profile_factory.create()
        transaction = self.create_transaction()
        functions.grant_privilege(profile, 'Registrar')
        request = self.factory.get(
            'reports/badges/print_run/%s'
            % transaction.ticket_item.bpt_event.conference.conference_slug)
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = export_badge_report(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=print_badges.csv")
        self.assertIn(
            "First,Last,username,Badge Name,Badge Type,Date,State",
            response.content)
        self.assertIn(
            transaction.purchaser.matched_to_user.username,
            response.content)
        self.assertIn(
            transaction.ticket_item.title,
            response.content)

    def test_export_badge_report_succeed(self):
        '''loads with the default conference selection.
        '''
        profile = self.profile_factory.create()
        transaction = self.create_transaction()

        request = self.factory.get('reports/badges/print_run')
        functions.login_as(profile, self)
        request.user = profile.user_object

        functions.grant_privilege(profile, 'Registrar')
        request = self.factory.get('reports/badges/print_run')
        request.user = profile.user_object
        response = export_badge_report(
            request,
            transaction.ticket_item.bpt_event.conference.conference_slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=print_badges.csv")
        self.assertIn(
            "First,Last,username,Badge Name,Badge Type,Date,State",
            response.content)
        self.assertIn(
            transaction.purchaser.matched_to_user.username,
            response.content)
        self.assertIn(
            transaction.ticket_item.title,
            response.content)
