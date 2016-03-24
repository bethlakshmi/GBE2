import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    ClassFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import SchedEventFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)

from gbe.views import (
    review_class,
    class_changestate,
)
from scheduler.models import Event as sEvent


class TestReviewClass(TestCase):
    '''Tests for review_class view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Class Reviewers')
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def test_review_class_all_well(self):
        klass = ClassFactory()
        request = self.factory.get('class/review/%d' % klass.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_reject_class(self):
        klass = ClassFactory()
        s_event = SchedEventFactory(eventitem=klass.eventitem_ptr)
        request = self.factory.post(
            '/class/changestate/',
            data={'accepted': 1})
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        login_as(request.user, self)
        class_changestate(request, klass.pk)
        nt.assert_equal(0, sEvent.objects.filter(pk=s_event.pk).count())
