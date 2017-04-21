from django.test import (
    Client,
    TestCase,
)
from django.core.urlresolvers import reverse
from scheduler.views import view_list

from tests.factories.gbe_factories import(
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.contexts import StaffAreaContext
from tests.factories.scheduler_factories import(
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from tests.functions.gbe_functions import grant_privilege
from scheduler.views import contact_by_role
from gbe.models import (
    Class,
    Conference,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestDeleteEvent(TestCase):
    view_name = 'contact_by_role'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def test_contact_performers_permissions_required(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Performers']))
        self.assertEqual(response.status_code, 403)

    def test_contact_performers_current_unknown_role(self):
        Conference.objects.all().delete()
        login_as(self.privileged_profile, self)
        conference = ConferenceFactory.create(status="upcoming")
        acts = ActFactory.create_batch(5, b_conference=conference)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Unknown']))
        self.assertFalse(all([str(act.performer) in response.content
                         for act in acts]))

    def test_contact_performers_current_performers_visible(self):
        Conference.objects.all().delete()
        login_as(self.privileged_profile, self)
        conference = ConferenceFactory.create(status="upcoming")
        acts = ActFactory.create_batch(5, b_conference=conference)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Performers']))
        self.assertTrue(all([str(act.performer) in response.content
                        for act in acts]))

    def test_contact_performers_former_performers_not_visible(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory.create(status="finished")
        acts = ActFactory.create_batch(5, b_conference=conference)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Performers']))
        self.assertFalse(any([str(act.performer) in response.content
                         for act in acts]))

    def test_contact_performers_inactive_performers_not_visible(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory.create(status="upcoming")
        acts = ActFactory.create_batch(5, b_conference=conference)
        inactive = ActFactory(b_conference=conference,
                              performer__contact__user_object__is_active=False)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Performers']))
        self.assertFalse(str(inactive.performer) in response.content)

    def test_contact_volunteers_current_volunteers_visible(self):
        Conference.objects.all().delete()
        context = StaffAreaContext()
        opp = context.add_volunteer_opp()
        volunteers = ProfileFactory.create_batch(5)
        opp = context.add_volunteer_opp()

        for volunteer in volunteers:
            VolunteerFactory(profile=volunteer,
                             b_conference=context.conference)

            context.book_volunteer(opp, volunteer)

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))
        self.assertContains(response, 'Registration', count=5)
        self.assertContains(response, str(opp), count=5)
        self.assertContains(response, str(context.sched_event), count=5)

    def test_contact_volunteers_inactive_volunteers_not_visible(self):
        Conference.objects.all().delete()
        context = StaffAreaContext()
        opp = context.add_volunteer_opp()
        volunteer = ProfileFactory()
        inactive = ProfileFactory(user_object__is_active=False)
        opp = context.add_volunteer_opp()

        VolunteerFactory(profile=volunteer,
                         b_conference=context.conference)
        context.book_volunteer(opp, volunteer)

        VolunteerFactory(
            profile=inactive,
            b_conference=context.conference)
        context.book_volunteer(opp, inactive)

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(volunteer.display_name in response.content)
        self.assertFalse(inactive.display_name in response.content)

    def test_contact_volunteers_current_volunteers_no_container(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory(status="upcoming")
        volunteers = ProfileFactory.create_batch(5)

        workers = [WorkerFactory.create(
            _item=volunteer.workeritem_ptr,
            role="Volunteer") for volunteer in volunteers]
        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    b_conference=conference)
        event = SchedEventFactory(
            eventitem=GenericEventFactory(
                type='VolunteerOpportunity',
                e_conference=conference))
        for worker in workers:
            ResourceAllocationFactory.create(
                event=event,
                resource=worker)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))
        self.assertContains(response, 'Registration', count=5)
        self.assertContains(response, str(event), count=10)

    def test_contact_volunteers_current_volunteers_no_interest(self):
        Conference.objects.all().delete()
        context = StaffAreaContext()
        opp = context.add_volunteer_opp()
        volunteers = ProfileFactory.create_batch(5)
        opp = context.add_volunteer_opp(
            SchedEventFactory(
                eventitem=GenericEventFactory(
                    type='VolunteerOpportunity',
                    e_conference=context.conference,
                    volunteer_type=None))
        )

        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    b_conference=context.conference)
            context.book_volunteer(opp, volunteer)

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))
        self.assertContains(response, 'Registration', count=0)
        self.assertContains(response, str(opp), count=5)
        self.assertContains(response, str(context.sched_event), count=5)

    def test_contact_volunteers_only_applications(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory()
        volunteers = ProfileFactory.create_batch(5)
        for volunteer in volunteers:
            bid = VolunteerFactory.create(
                profile=volunteer,
                b_conference=conference)
            VolunteerInterestFactory(volunteer=bid)

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))
        self.assertContains(response, 'Application', count=10)
        self.assertContains(response, 'Security/usher', count=5)

    def test_contact_volunteers_former_volunteers_not_visible(self):
        Conference.objects.all().delete()
        previous_conf = ConferenceFactory(status="finished")
        volunteers = ProfileFactory.create_batch(5)
        workers = [WorkerFactory.create(
            _item=volunteer.workeritem_ptr,
            role="Volunteer") for volunteer in volunteers]
        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    b_conference=previous_conf)
        event = SchedEventFactory(
            eventitem=GenericEventFactory(
                type='VolunteerOpportunity',
                e_conference=previous_conf))
        for worker in workers:
            ResourceAllocationFactory.create(
                event=event,
                resource=worker)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertFalse(any([volunteer.display_name in response.content
                         for volunteer in volunteers]))
        self.assertNotContains(response, 'Registration')

    def test_contact_vol_current_volunteers_past_events_not_visible(self):
        Conference.objects.all().delete()
        previous_conf = ConferenceFactory(status="finished")
        volunteers = ProfileFactory.create_batch(5)
        workers = [WorkerFactory.create(
            _item=volunteer.workeritem_ptr,
            role="Volunteer") for volunteer in volunteers]
        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer)
        event = SchedEventFactory(
            eventitem=GenericEventFactory(
                type='VolunteerOpportunity',
                e_conference=previous_conf))
        for worker in workers:
            ResourceAllocationFactory.create(
                event=event,
                resource=worker)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(any([volunteer.display_name in response.content
                        for volunteer in volunteers]))
        self.assertNotContains(response, 'Registration')

    def test_contact_vendors(self):
        Conference.objects.all().delete()
        previous_conf = ConferenceFactory(status="completed")
        current_conf = ConferenceFactory(status="upcoming")
        previous_vendor = VendorFactory(b_conference=previous_conf)
        current_vendor = VendorFactory(b_conference=current_conf)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Vendors']))
        self.assertTrue(
            current_vendor.profile.display_name in response.content)
        self.assertFalse(
            previous_vendor.profile.display_name in response.content)

    def test_contact_vendors_no_inactive(self):
        Conference.objects.all().delete()
        current_conf = ConferenceFactory(status="upcoming")
        inactive = VendorFactory(b_conference=current_conf,
                                 profile__user_object__is_active=False)
        current_vendor = VendorFactory(b_conference=current_conf)
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Vendors']))
        self.assertTrue(
            current_vendor.profile.display_name in response.content)
        self.assertFalse(
            inactive.profile.display_name in response.content)

    def test_contact_teachers(self):
        Conference.objects.all().delete()
        Class.objects.all().delete()
        previous_conf = ConferenceFactory(status="completed")
        current_conf = ConferenceFactory(status="upcoming")
        previous_class = ClassFactory(b_conference=previous_conf,
                                      e_conference=previous_conf)
        current_class = ClassFactory(b_conference=current_conf,
                                     e_conference=current_conf)

        previous_teacher = ProfileFactory()
        PersonaFactory(performer_profile=previous_teacher)
        current_teacher = ProfileFactory()
        PersonaFactory(performer_profile=current_teacher)
        previous_sEvent = SchedEventFactory(
            eventitem=previous_class.eventitem_ptr)
        current_sEvent = SchedEventFactory(
            eventitem=current_class.eventitem_ptr)
        previous_worker = WorkerFactory(
            _item=previous_teacher.workeritem_ptr)
        previous_sEvent.allocate_worker(previous_worker, 'Teacher')
        current_worker = WorkerFactory(
            _item=current_teacher)
        current_sEvent.allocate_worker(current_worker, 'Teacher')

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Teachers']))

        self.assertTrue(current_teacher.display_name in response.content)
        self.assertFalse(previous_teacher.display_name in response.content)

    def test_contact_teachers_inactive_not_shown(self):
        Conference.objects.all().delete()
        Class.objects.all().delete()
        inactive = PersonaFactory(contact__user_object__is_active=False)
        current_conf = ConferenceFactory(status="upcoming")
        current_class = ClassFactory(b_conference=current_conf,
                                     e_conference=current_conf,
                                     teacher=inactive)

        current_sEvent = SchedEventFactory(
            eventitem=current_class.eventitem_ptr)
        current_worker = WorkerFactory(
            _item=inactive)
        current_sEvent.allocate_worker(current_worker, 'Teacher')

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Teachers']))
        self.assertFalse(inactive.contact_email in response.content)

    def test_contact_teachers_only_show_alternate(self):
        Conference.objects.all().delete()
        Class.objects.all().delete()
        inactive = PersonaFactory(contact__user_object__is_active=False)
        active = PersonaFactory()
        current_conf = ConferenceFactory(status="upcoming")
        current_class = ClassFactory(b_conference=current_conf,
                                     e_conference=current_conf,
                                     teacher=inactive)

        current_sEvent = SchedEventFactory(
            eventitem=current_class.eventitem_ptr)
        current_worker = WorkerFactory(
            _item=active)
        current_sEvent.allocate_worker(current_worker, 'Teacher')

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Teachers']))
        self.assertFalse(inactive.contact_email in response.content)
        self.assertTrue(active.contact_email in response.content)

    def test_contact_bidder_not_booked_teacher(self):
        Conference.objects.all().delete()
        Class.objects.all().delete()
        inactive = PersonaFactory(contact__user_object__is_active=False)
        active = PersonaFactory()
        current_conf = ConferenceFactory(status="upcoming")
        current_class = ClassFactory(b_conference=current_conf,
                                     e_conference=current_conf,
                                     teacher=active)

        current_sEvent = SchedEventFactory(
            eventitem=current_class.eventitem_ptr)
        current_worker = WorkerFactory(
            _item=inactive)
        current_sEvent.allocate_worker(current_worker, 'Teacher')

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Teachers']))
        self.assertFalse(inactive.contact_email in response.content)
        self.assertTrue(active.contact_email in response.content)
