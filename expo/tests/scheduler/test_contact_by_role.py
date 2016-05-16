import pytest
from django.contrib.auth.models import Group
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from scheduler.views import view_list
import nose.tools as nt

from tests.factories.gbe_factories import(
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
    VolunteerFactory,
    )

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


@pytest.mark.django_db
@nt.raises(PermissionDenied)
def test_contact_performers_permissions_required():
    user = ProfileFactory.create().user_object
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")


@pytest.mark.django_db
def test_contact_performers_current_performers_visible():
    Conference.objects.all().delete()
    user = ProfileFactory.create().user_object
    group, _ = Group.objects.get_or_create(name='Class Coordinator')
    user.groups.add(group)
    conference = ConferenceFactory.create(status="upcoming")
    acts = ActFactory.create_batch(5, conference=conference)
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")
    nt.assert_true(all([str(act.performer) in response.content
                        for act in acts]))


@pytest.mark.django_db
def test_contact_performers_former_performers_not_visible():
    Conference.objects.all().delete()
    user = ProfileFactory.create().user_object
    group, _ = Group.objects.get_or_create(name='Class Coordinator')
    user.groups.add(group)
    conference = ConferenceFactory.create(status="finished")
    acts = ActFactory.create_batch(5, conference=conference)
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")
    nt.assert_false(any([str(act.performer) in response.content
                        for act in acts]))


@pytest.mark.django_db
def test_contact_volunteers_current_volunteers_visible():
    Conference.objects.all().delete()
    conference = ConferenceFactory(status="upcoming")
    user = ProfileFactory.create().user_object
    grant_privilege(user, 'Volunteer Coordinator')
    # group, _ = Group.objects.get_or_create(name='Volunteer Coordinator')
    # user.groups.add(group)
    volunteers = ProfileFactory.create_batch(5)

    workers = [WorkerFactory.create(
        _item=volunteer.workeritem_ptr,
        role="Volunteer")
               for volunteer in volunteers]
    for volunteer in volunteers:
        VolunteerFactory.create(profile=volunteer,
                                interests="['VA1']",
                                conference=conference)
    event = SchedEventFactory()
    for worker in workers:
        ResourceAllocationFactory.create(
            event=event,
            resource=worker)
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Volunteers")
    nt.assert_true(all([volunteer.display_name in response.content
                        for volunteer in volunteers]))


@pytest.mark.django_db
def test_contact_volunteers_former_volunteers_not_visible():
    Conference.objects.all().delete()
    previous_conf = ConferenceFactory(status="finished")
    user = ProfileFactory.create().user_object
    grant_privilege(user, 'Volunteer Coordinator')
    volunteers = ProfileFactory.create_batch(5)

    workers = [WorkerFactory.create(
        _item=volunteer.workeritem_ptr,
        role="Volunteer")
               for volunteer in volunteers]
    for volunteer in volunteers:
        VolunteerFactory.create(profile=volunteer,
                                interests="['VA1']",
                                conference=previous_conf)
    event = SchedEventFactory()
    for worker in workers:
        ResourceAllocationFactory.create(
            event=event,
            resource=worker)
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Volunteers")
    nt.assert_false(any([volunteer.display_name in response.content
                        for volunteer in volunteers]))


@pytest.mark.django_db
def test_contact_vendors():
    Conference.objects.all().delete()
    previous_conf = ConferenceFactory(status="completed")
    current_conf = ConferenceFactory(status="upcoming")
    previous_vendor = VendorFactory(conference=previous_conf)
    current_vendor = VendorFactory(conference=current_conf)
    user = ProfileFactory.create().user_object
    grant_privilege(user, 'Volunteer Coordinator')

    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Vendors']))
    request.user = user
    response = contact_by_role(request, "Vendors")

    nt.assert_true(current_vendor.profile.display_name in response.content)
    nt.assert_false(previous_vendor.profile.display_name in response.content)


@pytest.mark.django_db
def test_contact_teachers():
    Conference.objects.all().delete()
    Class.objects.all().delete()
    previous_conf = ConferenceFactory(status="completed")
    current_conf = ConferenceFactory(status="upcoming")
    previous_class = ClassFactory(conference=previous_conf)
    current_class = ClassFactory(conference=current_conf)
    previous_class.conference = previous_conf
    previous_class.save()
    # something broken about the factory here.
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

    user = ProfileFactory.create().user_object
    grant_privilege(user, 'Volunteer Coordinator')

    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Teachers']))
    request.user = user

    response = contact_by_role(request, "Teachers")

    nt.assert_true(current_teacher.display_name in response.content)
    nt.assert_false(previous_teacher.display_name in response.content)
