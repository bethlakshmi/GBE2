from django.contrib.auth.models import Group
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from scheduler.views import view_list
import nose.tools as nt

from tests.factories.gbe_factories import(
    ActFactory,
    ProfileFactory,
    VolunteerFactory,
    )

from tests.factories.scheduler_factories import(
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from scheduler.views import contact_by_role

@nt.raises(PermissionDenied)
def test_contact_performers_permissions_required():
    user = ProfileFactory.create().user_object
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args = ['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")
    
def test_contact_performers_success():
    user = ProfileFactory.create().user_object
    group, _ = Group.objects.get_or_create(name='Class Coordinator')
    user.groups.add(group)
    acts = ActFactory.create_batch(5)
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args=['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")
    nt.assert_true(all([str(act.performer) in response.content
                        for act in acts]))


def test_contact_volunteers_success():
    user = ProfileFactory.create().user_object
    group, _ = Group.objects.get_or_create(name='Volunteer Coordinator')
    user.groups.add(group)
    volunteers = ProfileFactory.create_batch(5)

    workers = [WorkerFactory.create(
        _item=volunteer.workeritem_ptr,
        role="Volunteer")
               for volunteer in volunteers]
    for volunteer in volunteers:
        VolunteerFactory.create(profile=volunteer,
                                interests="['VA1']")
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
