from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ProfileFactory,
    PersonaFactory,
    RoomFactory,
    VolunteerFactory,
)
from gbe.models import (Event, Room)
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
    VolunteerContext,
)
from tests.functions.gbe_scheduling_functions import (
    assert_good_sched_event_form,
    get_sched_event_form,
)
import pytz
from datetime import (
    date,
    time,
    timedelta,
)
from tests.factories.scheduler_factories import EventLabelFactory
from scheduler.models import EventLabel


class TestEditOccurrence(TestCase):
    view_name = 'edit_event_schedule'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        Room.objects.all().delete()
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.scheduling.urls",
                           args=["Class",
                                 self.context.bid.eventitem_id,
                                 self.context.sched_event.pk])

    def assert_good_post(self,
                         response,
                         form_data,
                         sched_event,
                         day,
                         room,
                         event_type="Class"):
        self.assertRedirects(response, reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[event_type,
                  sched_event.eventitem.eventitem_id,
                  sched_event.pk]))

        self.assertNotIn('<ul class="errorlist">', response.content)
        # check title
        self.assertIn(('<H1 class="sched_detail_title">%s</H1>' %
                       form_data['event-e_title']),
                      response.content)
        # check day
        self.assertIn('<option value="' +
                      str(day.pk) +
                      '" selected="selected">',
                      response.content)
        # check time
        self.assertIn('<option value="12:00:00" selected="selected">',
                      response.content)
        # check location
        self.assertIn('<option value="' +
                      str(room.pk) +
                      '" selected="selected">' +
                      str(room),
                      response.content)
        # check volunteers
        self.assertIn('<input id="id_event-max_volunteer" ' +
                      'name="event-max_volunteer" type="number" value="3" />',
                      response.content)
        # check description
        self.assertIn(form_data['event-e_description'], response.content)

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login', urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class",
                            self.context.bid.eventitem_id,
                            self.context.sched_event.pk+1])
        response = self.client.get(url, follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1))
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))

    def test_good_user_post_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class",
                            self.context.bid.eventitem_id,
                            self.context.sched_event.pk+1])
        form_data = get_sched_event_form(self.context)
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1))
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        bid = self.context.bid
        bid.schedule_constraints = "[u'1']"
        bid.avoided_constraints = "[u'2']"
        bid.space_needs = "2"
        bid.type = "Panel"
        bid.save()
        response = self.client.get(self.url)
        assert_good_sched_event_form(response, self.context.bid)

    def test_good_user_get_success_teacher_as_profile(self):
        login_as(self.privileged_profile, self)
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        teacher = ProfileFactory()
        teacher, alloc = staff_context.book_volunteer(
            volunteer_sched_event=volunteer_sched_event,
            volunteer=teacher,
            role="Teacher")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent",
                            volunteer_sched_event.eventitem.eventitem_id,
                            volunteer_sched_event.pk])
        response = self.client.get(url)
        assert_good_sched_event_form(response, volunteer_sched_event.eventitem)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                teacher.pk,
                teacher.display_name))

    def test_good_user_get_volunteer_w_teacher_as_persona(self):
        login_as(self.privileged_profile, self)
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        teacher = PersonaFactory()
        teacher, alloc = staff_context.book_volunteer(
            volunteer_sched_event=volunteer_sched_event,
            volunteer=teacher,
            role="Teacher")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent",
                            volunteer_sched_event.eventitem.eventitem_id,
                            volunteer_sched_event.pk])
        response = self.client.get(url)
        assert_good_sched_event_form(response, volunteer_sched_event.eventitem)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                teacher.pk,
                teacher.name))

    def test_vol_opp_new_interest(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        context = VolunteerContext()
        new_interest = AvailableInterestFactory()
        context.opportunity.volunteer_type = new_interest
        context.opportunity.save()
        url = reverse(self.view_name,
                      args=["GenericEvent",
                            context.opportunity.eventitem_id,
                            context.opp_event.pk],
                      urlconf="gbe.scheduling.urls")
        login_as(self.privileged_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Allocation")
        self.assertContains(response, context.bid.profile.badge_name)
        self.assertContains(response, context.opportunity.e_title)

    def test_vol_opp_pk_v_eventitem_id(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        context = VolunteerContext()
        context.opp_event.eventitem.eventitem_id = (
            context.opportunity.pk + 1000)
        context.opp_event.eventitem.save()
        url = reverse(self.view_name,
                      args=["Show",
                            context.event.eventitem_id,
                            context.sched_event.pk],
                      urlconf="gbe.scheduling.urls")
        login_as(self.privileged_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Management")
        self.assertContains(response, context.opportunity.e_title)

    def test_good_user_minimal_post(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)
        self.assert_good_post(response,
                              form_data,
                              self.context.sched_event,
                              self.context.days[0],
                              self.context.room)

    def test_good_user_set_max_volunteer_to_zero(self):
        login_as(self.privileged_profile, self)
        self.context.sched_event.max_volunteer = 5
        self.context.sched_event.save()
        form_data = get_sched_event_form(self.context)
        form_data['event-max_volunteer'] = 0
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)
        self.assertIn('<input id="id_event-max_volunteer" ' +
                      'name="event-max_volunteer" type="number" value="0" />',
                      response.content)

    def test_good_user_invalid_submit(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        form_data['event-location'] = 'bad room'
        response = self.client.post(
            self.url,
            data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<input id="id_event-e_title" name="event-e_title" ' +
                      'size="79" type="text" value="New Title" />',
                      response.content)
        self.assertIn("New Description",
                      response.content)
        self.assertIn('<input id="id_event-max_volunteer" ' +
                      'name="event-max_volunteer" type="number" value="3" />',
                      response.content)
        self.assertIn('<option value="12:00:00" selected="selected">',
                      response.content)
        self.assertIn(
            '<option value="%s" selected="selected">%s</option>' % (
                str(self.context.days[0].pk),
                str(self.context.days[0])),
            response.content)
        self.assertIn('<li>Select a valid choice. That choice is not one of ' +
                      'the available choices.</li>',
                      response.content)

    def test_good_user_with_duration(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              self.context.sched_event,
                              self.context.days[0],
                              self.context.room)
        self.assertIn('<input id="id_event-duration" name="event-duration" ' +
                      'type="text" value="03:00:00" />',
                      response.content)

    def test_no_duration(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        del form_data['event-duration']
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)
        self.assertIn("This field is required.",
                      response.content)

    def test_good_user_change_room(self):
        login_as(self.privileged_profile, self)
        new_room = RoomFactory()
        form_data = get_sched_event_form(self.context, new_room)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              self.context.sched_event,
                              self.context.days[0],
                              new_room)

    def test_good_user_with_teacher(self):
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        form_data['event-teacher'] = overcommitter.pk

        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              self.context.sched_event,
                              self.context.days[0],
                              self.context.room)
        teachers = self.context.sched_event.get_direct_workers('Teacher')
        self.assertEqual(len(teachers), 1)
        self.assertEqual(teachers[0].pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

    def test_good_user_remove_teacher(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        form_data['event-teacher'] = ""
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              self.context.sched_event,
                              self.context.days[0],
                              self.context.room)
        teachers = self.context.sched_event.get_direct_workers('Teacher')
        self.assertEqual(len(teachers), 0)
        self.assertIn(
            '<select id="id_event-teacher" name="event-teacher">\n' +
            '<option value="" selected="selected">---------</option>',
            response.content)

    def test_good_user_with_moderator(self):
        clear_conferences()
        Room.objects.all().delete()
        context = PanelContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["Class",
                            context.bid.eventitem_id,
                            context.sched_event.pk])
        form_data = get_sched_event_form(context)
        form_data['event-moderator'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              context.sched_event,
                              context.days[0],
                              context.room)
        moderators = context.sched_event.get_direct_workers('Moderator')
        self.assertEqual(len(moderators), 1)
        self.assertEqual(moderators[0].pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

    def test_good_user_with_staff_area_lead(self):
        clear_conferences()
        Room.objects.all().delete()
        room = RoomFactory()
        staff_context = StaffAreaContext()
        context = ClassContext(conference=staff_context.conference)
        overcommitter = ProfileFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent",
                            context.bid.eventitem_id,
                            context.sched_event.pk])
        form_data = get_sched_event_form(context, room=room)
        form_data['event-staff_lead'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assert_good_post(response,
                              form_data,
                              context.sched_event,
                              context.days[0],
                              room,
                              "GenericEvent")
        leads = Worker.objects.filter(
            role="Staff Lead",
            allocations__event=context.sched_event)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads.first().workeritem.pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

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
                      args=["Class",
                            context.bid.eventitem_id,
                            context.sched_event.pk])
        form_data = get_sched_event_form(context)
        form_data['event-panelists'] = [overcommitter1.pk, overcommitter2.pk]
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              form_data,
                              context.sched_event,
                              context.days[0],
                              context.room)
        leads = context.sched_event.get_direct_workers('Panelist')
        self.assertEqual(len(leads), 2)
        self.assertIn(leads[0].pk, [overcommitter1.pk, overcommitter2.pk])
        self.assertIn(leads[1].pk, [overcommitter1.pk, overcommitter2.pk])
        self.assertIn('<option value="' + str(overcommitter1.pk) +
                      '" selected="selected">' + str(overcommitter1) +
                      '</option>',
                      response.content)
        self.assertIn('<option value="' + str(overcommitter2.pk) +
                      '" selected="selected">' + str(overcommitter2) +
                      '</option>',
                      response.content)

    def test_inactive_user_not_listed(self):
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        inactive_persona = PersonaFactory(
            contact__user_object__is_active=False)
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=["GenericEvent",
                            volunteer_sched_event.eventitem.eventitem_id,
                            volunteer_sched_event.pk])
        response = self.client.get(url)
        self.assertNotIn(str(inactive_persona), response.content)
        self.assertNotIn(str(inactive_persona.contact), response.content)

    def test_no_change_to_labels(self):
        login_as(self.privileged_profile, self)
        form_data = get_sched_event_form(self.context)
        label = EventLabelFactory(text="Label test no change",
                                  event=self.context.sched_event)
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True)
        test = EventLabel.objects.get(pk=label.pk)
        self.assertEqual(test.text, "Label test no change")
