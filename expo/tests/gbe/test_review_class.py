import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
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

from scheduler.models import Event as sEvent


class TestReviewClass(TestCase):
    '''Tests for review_class view'''
    view_name = 'class_review'

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
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)


    def test_review_class_post_form_invalid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data = {'accepted': 1})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)


    def test_review_class_post_form_valid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        profile = self.privileged_user.profile
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    {'vote': 3,
                                     'notes': "blah blah",
                                     'evaluator': profile.pk,
                                     'bid': klass.pk},
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
