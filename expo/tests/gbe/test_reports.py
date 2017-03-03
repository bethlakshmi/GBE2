from pytz import utc
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from datetime import (
    datetime,
    time,
    date,
    timedelta,
)

import gbe.models as conf
import nose.tools as nt
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.http import Http404

from gbe.reporting import (
    list_reports,
    review_staff_area,
    staff_area,
    env_stuff,
    personal_schedule,
    review_act_techinfo,
    export_act_techinfo,
    room_schedule,
    room_setup,
    export_badge_report,
)
from gbe.models import Conference
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    VolunteerContext,
    PurchasedTicketContext,
)
import ticketing.models as tix
from tests.functions.scheduler_functions import assert_link
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


def _create_scheduled_show_with_acts(conference=None, qty=6):
    if not conference:
        conference = ConferenceFactory()
    conf_day = ConferenceDayFactory(
        conference=conference)

    show = ShowFactory(conference=conference)
    sEvent = SchedEventFactory(
        eventitem=show.eventitem_ptr,
        starttime=utc.localize(datetime.combine(conf_day.day, time(20, 0))))
    acts = [ActFactory(accepted=3) for i in range(qty)]
    for act in acts:
        ar = ActResourceFactory(_item=act.actitem_ptr)
        ResourceAllocationFactory(
            event=sEvent,
            resource=ar)
    return show, sEvent, acts


class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_list_reports_by_conference(self):
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        profile = ProfileFactory()
        request = self.factory.get(
            'reports/',
            data={"conf_slug": conf.conference_slug})
        login_as(profile, self)
        request.user = profile.user_object
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        response = list_reports(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_list_reports_fail(self):
        '''list_reports view should fail because user
           is not in one of the privileged groups
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/')
        login_as(profile, self)
        request.user = profile.user_object
        response = list_reports(request)

    def test_list_reports_succeed(self):
        '''list_reports view should load, user has proper
           privileges
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/')
        login_as(profile, self)
        request.user = profile.user_object
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        response = list_reports(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_review_staff_area_not_visible_without_permission(self):
        profile = ProfileFactory()
        request = self.factory.get('reports/review_staff_area')
        login_as(profile, self)
        request.user = profile.user_object
        current_conference = ConferenceFactory()
        response = review_staff_area(request)

    def test_review_staff_area_path(self):
        '''review_staff_area view should load
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/review_staff_area')
        login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Act Reviewers')
        current_conference = ConferenceFactory()
        response = review_staff_area(request)
        self.assertEqual(response.status_code, 200)

    def test_review_staff_area_by_conference(self):
        '''review_staff_area view should load
        '''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        profile = ProfileFactory()
        request = self.factory.get(
            'reports/review_staff_area',
            data={'conf_slug': conf.conference_slug})
        login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Act Reviewers')
        current_conference = ConferenceFactory()
        response = review_staff_area(request)
        self.assertEqual(response.status_code, 200)

    def test_staff_area_path(self):
        '''staff_area view should load
        '''
        profile = ProfileFactory()
        show = ShowFactory()
        context = VolunteerContext(event=show)
        request = self.factory.get('reports/staff_area/%d' % show.eventitem_id)
        login_as(profile, self)
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Act Reviewers')
        response = staff_area(request, show.eventitem_id)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_staff_area_path_fail(self):
        '''staff_area view should fail for non-authenticated users
        '''
        profile = ProfileFactory()
        show = ShowFactory()
        request = self.factory.get('reports/staff_area/%d' % show.eventitem_id)
        login_as(profile, self)
        request.user = profile.user_object
        current_conference = ConferenceFactory()
        response = staff_area(request, show.eventitem_id)

    @nt.raises(PermissionDenied)
    def test_env_stuff_fail(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/stuffing')
        login_as(profile, self)
        request.user = profile.user_object
        response = env_stuff(request)

    def test_env_stuff_succeed(self):
        '''env_stuff view should load with no conf choice
        '''
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction
        request = self.factory.get('reports/stuffing')
        login_as(profile, self)
        request.user = profile.user_object
        grant_privilege(profile, 'Registrar')
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
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction
        request = self.factory.get(
            'reports/stuffing/%s/'
            % transaction.ticket_item.bpt_event.conference.conference_slug)

        login_as(profile, self)
        request.user = profile.user_object
        grant_privilege(profile, 'Registrar')
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
        profile = ProfileFactory()
        login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        request.user = profile.user_object
        response = review_act_techinfo(request)

    def test_review_act_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        profile = ProfileFactory()
        login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        request.GET = {'conf_slug': curr_conf.conference_slug}
        grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request, curr_show.eventitem_id)
        nt.assert_true(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        nt.assert_true(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_has_link_for_scheduler(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        profile = ProfileFactory()
        login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        request.GET = {'conf_slug': curr_conf.conference_slug}
        grant_privilege(profile, 'Tech Crew')
        grant_privilege(profile, 'Scheduling Mavens')
        response = review_act_techinfo(request, curr_show.eventitem_id)
        assert_link(response, reverse(
            'schedule_acts',
            urlconf='scheduler.urls',
            args=[curr_show.pk]))
        self.assertContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_with_conference_slug(self):
        '''review_act_techinfo view show correct events for slug
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        old_conf = ConferenceFactory(status='completed')
        old_show, _, old_acts = _create_scheduled_show_with_acts(old_conf)

        profile = ProfileFactory()
        login_as(profile, self)
        request = self.factory.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        request.GET = {'conf_slug': curr_conf.conference_slug}
        grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(curr_show.title in response.content)

    @nt.raises(PermissionDenied)
    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        current_conference = ConferenceFactory()
        response = room_schedule(request)

    def test_room_schedule_succeed(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        profile = ProfileFactory()
        context = ClassContext()
        one_day = timedelta(1)
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        ConferenceDayFactory(
            conference=context.conference,
            day=context.sched_event.starttime.date()+one_day)
        context.schedule_instance(
            starttime=context.sched_event.starttime + one_day)
        request = self.factory.get('reports/room_schedule',
                                   args=[context.room.pk])
        request.user = profile.user_object
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        current_conference = context.conference
        response = room_schedule(request, context.room.pk)
        self.assertEqual(response.status_code, 200)

    def test_room_schedule_by_conference(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        profile = ProfileFactory()
        request = self.factory.get(
            'reports/room_schedule',
            data={'conf_slug': conf.conference_slug})
        request.user = profile.user_object
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        response = room_schedule(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_room_setup_not_visible_without_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        current_conference = ConferenceFactory()
        response = room_setup(request)

    def test_room_setup_visible_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        current_conference = ConferenceFactory()
        response = room_setup(request)
        self.assertEqual(response.status_code, 200)

    def test_room_setup_by_conference_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        context = ClassContext()
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        profile = ProfileFactory()
        request = self.factory.get(
            'reports/room_setup',
            data={'conf_slug': context.conference.conference_slug})
        request.user = profile.user_object
        request.session = {'cms_admin_site': 1}
        grant_privilege(profile, 'Act Reviewers')
        login_as(profile, self)
        current_conference = ConferenceFactory()
        response = room_setup(request)
        self.assertEqual(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_export_badge_report_fail(self):
        '''export_badge_report view should fail for users w/out
        Registrar role
        '''
        profile = ProfileFactory()
        request = self.factory.get('reports/badges/print_run')
        login_as(profile, self)
        request.user = profile.user_object
        response = export_badge_report(request)

    def test_export_badge_report_succeed_w_conf(self):
        '''get badges w a specific conference
        '''
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction
        grant_privilege(profile, 'Registrar')
        request = self.factory.get(
            'reports/badges/print_run/%s'
            % transaction.ticket_item.bpt_event.conference.conference_slug)
        login_as(profile, self)
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
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction

        request = self.factory.get('reports/badges/print_run')
        login_as(profile, self)
        request.user = profile.user_object

        grant_privilege(profile, 'Registrar')
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

    def test_export_act_techinfo(self):
        context = ActTechInfoContext()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, "Tech Crew")
        login_as(reviewer, self)
        request = self.factory.get(reverse(
            'act_techinfo_download',
            urlconf='gbe.reporting.urls',
            args=[context.show.eventitem_id]))
        request.user = reviewer.user_object
        response = export_act_techinfo(request, context.show.eventitem_id)
        nt.assert_true(context.audio.notes in response.content)
        nt.assert_false('Center Spot' in response.content)

    def test_export_act_techinfo_theater(self):
        context = ActTechInfoContext(room_name="Theater")
        context.show.scheduler_events.first()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, "Tech Crew")
        login_as(reviewer, self)
        request = self.factory.get(reverse(
            'act_techinfo_download',
            urlconf='gbe.reporting.urls',
            args=[context.show.eventitem_id]))
        request.user = reviewer.user_object
        response = export_act_techinfo(request, context.show.eventitem_id)
        nt.assert_true(context.audio.notes in response.content)
        nt.assert_true('Center Spot' in response.content)

    def test_download_tracks_for_show(self):
        context = ActTechInfoContext(room_name="Theater")
        context.show.scheduler_events.first()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, "Tech Crew")
        login_as(reviewer, self)
        url = reverse(
            'download_tracks_for_show',
            urlconf='gbe.reporting.urls',
            args=[context.show.eventitem_id])
        response = self.client.get(url)
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                context.conference.conference_slug,
                context.show.title.replace(' ', '_'))))
