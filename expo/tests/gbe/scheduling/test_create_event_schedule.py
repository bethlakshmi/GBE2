from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ClassFactory,
    GenericEventFactory,
    ProfileFactory,
    PersonaFactory,
    RoomFactory,
)
from gbe.models import (
    Room,
)
from scheduler.models import Worker
from tests.functions.gbe_functions import (
    clear_conferences,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ClassContext,
    PanelContext,
    StaffAreaContext,
)
from tests.functions.gbe_scheduling_functions import (
    assert_good_sched_event_form,
    assert_selected,
    get_sched_event_form
)
import pytz
from datetime import (
    datetime,
    time,
)


class TestCreateEventSchedule(TestCase):
    view_name = 'create_event_schedule'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.eventitem = GenericEventFactory()

    def assert_good_post(self, response, event, day, room, event_type="Class"):
        self.assertRedirects(response,
                             reverse('event_schedule',
                                     urlconf='scheduler.urls',
                                     args=[event_type]))

        self.assertNotIn('<ul class="errorlist">', response.content)
        self.assertIn('Events Information', response.content)
        sessions = event.scheduler_events.filter(max_volunteer=3)
        self.assertEqual(len(sessions), 1)
        session = sessions.first()
        self.assertEqual(session.starttime,
                         datetime.combine(day,
                                          time(12, 0, 0, tzinfo=pytz.utc)))
        self.assertIn(event.child().e_title, response.content)
        self.assertIn(str(room), response.content)
        self.assertIn('<td class="events-table">      \n\t\t\t  \n\t\t\t' +
                      '    3\n\t\t\t  \n          \t\t</td>',
                      response.content)
        return session

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=["GenericEvent", self.eventitem.eventitem_id + 1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        assert_good_sched_event_form(response, self.eventitem)

    def test_good_user_get_default_location(self):
        room = RoomFactory()
        self.eventitem.default_location = room
        self.eventitem.save()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        assert_good_sched_event_form(response, self.eventitem)
        assert_selected(response, str(room.pk), str(room))

    def test_good_user_get_class(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        context.bid.schedule_constraints = "[u'1']"
        context.bid.avoided_constraints = "[u'2']"
        context.bid.space_needs = "2"
        context.bid.type = "Panel"
        context.bid.save()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.get(url)
        assert_good_sched_event_form(response, context.bid)

    def test_good_user_get_empty_schedule_info(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        context.bid.schedule_constraints = ""
        context.bid.avoided_constraints = ""
        context.bid.space_needs = ""
        context.bid.type = ""
        context.bid.save()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.get(url)
        assert_good_sched_event_form(response, context.bid)

    def test_good_user_minimal_post(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(url,
                                    data=get_sched_event_form(context),
                                    follow=True)
        self.assert_good_post(response,
                              context.bid,
                              context.days[0].day,
                              context.room)

    def test_good_user_invalid_submit(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        form_data['event-location'] = 'bad room'
        response = self.client.post(url,
                                    data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<input id="id_event-e_title" name="event-e_title" ' +
                      'type="text" value="New Title" />',
                      response.content)
        self.assertIn("New Description",
                      response.content)
        self.assertIn('<input id="id_event-max_volunteer" min="0" ' +
                      'name="event-max_volunteer" type="number" value="3" />',
                      response.content)
        self.assertIn('<option value="12:00:00" selected="selected">' +
                      'noon</option>',
                      response.content)
        self.assertIn('<option value="' + str(context.days[0].pk) +
                      '" selected="selected">' + str(context.days[0]) +
                      '</option>',
                      response.content)
        self.assertIn('<li>Select a valid choice. That choice is not one of ' +
                      'the available choices.</li>',
                      response.content)

    def test_good_user_with_duration(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assert_good_post(response,
                              context.bid,
                              context.days[0].day,
                              context.room)
        self.assertIn('<td class="events-table">      \n            ' +
                      '\t\t03:00\n          \t\t</td>',
                      response.content)

    def test_no_duration(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        del form_data['event-duration']
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assertIn("This field is required.",
                      response.content)

    def test_good_user_with_teacher(self):
        clear_conferences()
        Room.objects.all().delete()
        context = ClassContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        form_data['event-teacher'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        session = self.assert_good_post(response,
                                        context.bid,
                                        context.days[0].day,
                                        context.room)
        teachers = session.get_direct_workers('Teacher')
        self.assertEqual(len(teachers), 1)
        self.assertEqual(teachers[0].pk, overcommitter.pk)

    def test_good_user_with_moderator(self):
        clear_conferences()
        Room.objects.all().delete()
        context = PanelContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        form_data['event-moderator'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        session = self.assert_good_post(response,
                                        context.bid,
                                        context.days[0].day,
                                        context.room)
        moderators = session.get_direct_workers('Moderator')
        self.assertEqual(len(moderators), 1)
        self.assertEqual(moderators[0].pk, overcommitter.pk)

    def test_good_user_with_staff_area_lead(self):
        clear_conferences()
        Room.objects.all().delete()
        room = RoomFactory()
        context = StaffAreaContext()
        overcommitter = ProfileFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent",
                            context.sched_event.eventitem.eventitem_id])
        form_data = get_sched_event_form(context, room)
        form_data['event-staff_lead'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        session = self.assert_good_post(response,
                                        context.sched_event.eventitem,
                                        context.days[0].day,
                                        room,
                                        "GenericEvent")
        leads = Worker.objects.filter(role="Staff Lead",
                                      allocations__event=session)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads.first().workeritem.pk, overcommitter.pk)

    def test_good_user_with_panelists(self):
        clear_conferences()
        Room.objects.all().delete()
        context = PanelContext()
        context.add_panelist()
        overcommitter1 = PersonaFactory()
        overcommitter2 = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class", context.bid.eventitem_id])
        form_data = get_sched_event_form(context)
        form_data['event-panelists'] = [overcommitter1.pk, overcommitter2.pk]
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        session = self.assert_good_post(response,
                                        context.bid,
                                        context.days[0].day,
                                        context.room)
        leads = session.get_direct_workers('Panelist')
        self.assertEqual(len(leads), 2)
        self.assertIn(leads[0].pk, [overcommitter1.pk, overcommitter2.pk])
        self.assertIn(leads[1].pk, [overcommitter1.pk, overcommitter2.pk])
