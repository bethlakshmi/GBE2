import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_volunteer
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    PersonaFactory, 
    ProfileFactory,
    VolunteerFactory, 
    ConferenceFactory, 
    GenericEventFactory,
)
from tests.functions.gbe_functions import login_as


class TestReviewVolunteer(TestCase):
    '''Tests for review_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Volunteer Reviewers')
        self.privileged_user.groups.add(group)

    def test_review_volunteer_all_well(self):
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/review/%d' % volunteer.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site':1}
        login_as(request.user, self)
        response = review_volunteer(request, volunteer.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def only_show_relevant_events(self):
        volunteer = VolunteerFactory.create()
        # horrible setup process. Need to fix
        current_conference = ConferenceFactory.create(
            accepting_bids=True)
        past_conference = ConferenceFactory.create(
            status='completed')
        current_opportunity = GenericEventFactory.create(
            conference=current_conf)
        past_opportunity = GenericEventFactory.create(
            conference=past_conference)
        current_opportunity.max_volunteers = 20
        past_opportunity.max_volunteers = 20
        current_opportunity.save()
        past_opportunity.save()

        request = self.factory.get('volunteer/review/%d' % volunteer.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site':1}
        login_as(request.user, self)
        response = review_volunteer(request, volunteer.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_true(current_opportunity.description in response.content)
        nt.assert_false(past_opportunity.description in response.content)
        
