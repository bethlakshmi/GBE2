from pytz import utc
from django.core.urlresolvers import reverse
from datetime import (
    datetime,
    time,
    date,
    timedelta,
)
from django.test import TestCase, Client
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

    show = ShowFactory(e_conference=conference)
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
        self.client = Client()
        self.profile = ProfileFactory()

    def test_list_reports_by_conference(self):
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"),
            data={"conf_slug": conf.conference_slug})
        self.assertEqual(response.status_code, 200)

    def test_list_reports_fail(self):
        '''list_reports view should fail because user
           is not in one of the privileged groups
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 403)

    def test_list_reports_succeed(self):
        '''list_reports view should load, user has proper
           privileges
        '''
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 200)

    def test_env_stuff_fail(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 403)

    def test_env_stuff_succeed(self):
        '''env_stuff view should load with no conf choice
        '''
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction
        grant_privilege(profile, 'Registrar')
        login_as(profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

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

    def test_env_stuff_w_inactive_purchaser(self):
        '''env_stuff view should load with no conf choice
        '''
        Conference.objects.all().delete()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        ticket_context = PurchasedTicketContext(profile=inactive)
        transaction = ticket_context.transaction
        grant_privilege(self.profile, 'Registrar')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertIn(
            "Badge Name,First,Last,Tickets,Ticket format,Personae," +
            "Staff Lead,Volunteering,Presenter,Show",
            response.content)
        self.assertNotIn(
            inactive.display_name,
            response.content)

    def test_env_stuff_succeed_w_conf(self):
        '''env_stuff view should load for a selected conference slug
        '''
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        grant_privilege(profile, 'Registrar')
        transaction = ticket_context.transaction
        login_as(profile, self)
        response = self.client.get(reverse(
            'env_stuff',
            urlconf="gbe.reporting.urls",
            args=[
                transaction.ticket_item.bpt_event.conference.conference_slug]))
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

    def test_review_act_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_review_act_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        grant_privilege(self.profile, 'Tech Crew')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        grant_privilege(self.profile, 'Tech Crew')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        self.assertTrue(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        self.assertTrue(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_show_inactive(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        curr_acts[0].performer.contact.user_object.is_active = False
        curr_acts[0].performer.contact.user_object.save()

        grant_privilege(self.profile, 'Tech Crew')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        self.assertTrue(
            "- INACTIVE" in response.content,
            msg="Can't find inactive user")

    def test_review_act_techinfo_has_link_for_scheduler(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        grant_privilege(self.profile, 'Tech Crew')
        grant_privilege(self.profile, 'Scheduling Mavens')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]),
            data={'conf_slug': curr_conf.conference_slug})
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

        grant_privilege(self.profile, 'Tech Crew')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': curr_conf.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(curr_show.e_title in response.content)

    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_room_schedule_succeed(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        context = ClassContext()
        one_day = timedelta(1)
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        ConferenceDayFactory(
            conference=context.conference,
            day=context.sched_event.starttime.date()+one_day)
        context.schedule_instance(
            starttime=context.sched_event.starttime + one_day)
        current_conference = context.conference
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls',
                    args=[context.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_room_schedule_by_conference(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': conf.conference_slug})
        self.assertEqual(response.status_code, 200)

    def test_room_setup_not_visible_without_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_room_setup_visible_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)

    def test_room_setup_by_conference_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        context = ClassContext()
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        current_conference = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup',
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)

    def test_export_badge_report_fail(self):
        '''export_badge_report view should fail for users w/out
        Registrar role
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse('badge_report',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_export_badge_report_succeed_w_conf(self):
        '''get badges w a specific conference
        '''
        ticket_context = PurchasedTicketContext()
        profile = ticket_context.profile
        transaction = ticket_context.transaction
        grant_privilege(profile, 'Registrar')
        login_as(profile, self)
        response = self.client.get(reverse(
            'badge_report',
            urlconf='gbe.reporting.urls',
            args=[
                transaction.ticket_item.bpt_event.conference.conference_slug]))

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

        grant_privilege(profile, 'Registrar')
        login_as(profile, self)
        response = self.client.get(reverse('badge_report',
                                           urlconf='gbe.reporting.urls'))
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

    def test_export_badge_report_inactive_user(self):
        '''loads with the default conference selection.
        '''
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        ticket_context = PurchasedTicketContext(profile=inactive)
        transaction = ticket_context.transaction

        grant_privilege(self.profile, 'Registrar')
        login_as(self.profile, self)
        response = self.client.get(reverse('badge_report',
                                           urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            transaction.purchaser.first_name,
            response.content)
        self.assertNotIn(
            inactive.display_name,
            response.content)

    def test_export_act_techinfo(self):
        context = ActTechInfoContext()
        grant_privilege(self.profile, "Tech Crew")
        login_as(self.profile, self)
        response = self.client.get(reverse('act_techinfo_download',
                                           urlconf='gbe.reporting.urls',
                                           args=[context.show.eventitem_id]))
        self.assertTrue(context.audio.notes in response.content)
        self.assertFalse('Center Spot' in response.content)

    def test_export_act_techinfo_theater(self):
        context = ActTechInfoContext(room_name="Theater")
        context.show.scheduler_events.first()
        grant_privilege(self.profile, "Tech Crew")
        login_as(self.profile, self)
        response = self.client.get(reverse('act_techinfo_download',
                                           urlconf='gbe.reporting.urls',
                                           args=[context.show.eventitem_id]))
        self.assertTrue(context.audio.notes in response.content)
        self.assertTrue('Center Spot' in response.content)

    def test_download_tracks_for_show(self):
        context = ActTechInfoContext(room_name="Theater")
        context.show.scheduler_events.first()
        grant_privilege(self.profile, "Tech Crew")
        login_as(self.profile, self)
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[context.show.pk]))
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                context.conference.conference_slug,
                context.show.e_title.replace(' ', '_'))))
