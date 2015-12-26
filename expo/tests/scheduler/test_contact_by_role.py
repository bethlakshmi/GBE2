from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from scheduler.views import view_list
import nose.tools as nt

from tests.factories.gbe_factories import(
    ActFactory,
    UserFactory,
    )

from scheduler.views import contact_by_role

@nt.raises(PermissionDenied)
def test_contact_performers_permissions_required():
    user = UserFactory()
    request = RequestFactory().get(reverse('contact_by_role',
                                           urlconf="scheduler.urls",
                                           args = ['Performer']))
    request.user = user
    response = contact_by_role(request, "Performers")
