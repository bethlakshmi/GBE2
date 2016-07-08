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
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
    VolunteerFactory,
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

    def test_contact_volunteers_current_volunteers_visible(self):
        Conference.objects.all().delete()
        context = StaffAreaContext()
        opp = context.add_volunteer_opp()
        volunteers = ProfileFactory.create_batch(5)
        opp = context.add_volunteer_opp()

        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    interests="['VA1']",
                                    b_conference=context.conference)
            context.book_volunteer(opp, volunteer)

        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=['Volunteers']))
        self.assertTrue(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))

    def test_contact_volunteers_current_volunteers_no_container(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory(status="upcoming")
        volunteers = ProfileFactory.create_batch(5)

        workers = [WorkerFactory.create(
            _item=volunteer.workeritem_ptr,
            role="Volunteer")
                for volunteer in volunteers]
        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    interests="['VA1']",
                                    b_conference=conference)
        event = SchedEventFactory()
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

    def test_contact_volunteers_former_volunteers_not_visible(self):
        Conference.objects.all().delete()
        previous_conf = ConferenceFactory(status="finished")
        volunteers = ProfileFactory.create_batch(5)
        workers = [WorkerFactory.create(
            _item=volunteer.workeritem_ptr,
            role="Volunteer")
                   for volunteer in volunteers]
        for volunteer in volunteers:
            VolunteerFactory.create(profile=volunteer,
                                    interests="['VA1']",
                                    b_conference=previous_conf)
        event = SchedEventFactory()
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

    def test_contact_teachers(self):
        Conference.objects.all().delete()
        Class.objects.all().delete()
        previous_conf = ConferenceFactory(status="completed")
        current_conf = ConferenceFactory(status="upcoming")
        previous_class = ClassFactory(b_conference=previous_conf,
                                      e_conference=previous_conf)
        current_class = ClassFactory(b_conference=current_conf,
                                     e_conference=previous_conf)

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
