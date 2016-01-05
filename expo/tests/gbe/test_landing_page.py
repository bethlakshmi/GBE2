import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from datetime import datetime
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from gbe.views import landing_page
from tests.factories.gbe_factories import(
    ConferenceFactory,
    ProfileFactory,
    ActFactory,
    ClassFactory,
    VendorFactory,
    PersonaFactory,
    CostumeFactory,
    VolunteerFactory
)


class TestIndex(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.current_conf = ConferenceFactory.create(accepting_bids=True)
        self.current_conf.status = 'upcoming'
        self.current_conf.save()
        self.previous_conf = ConferenceFactory.create(accepting_bids=False)
        self.previous_conf.status = 'completed'
        self.previous_conf.save()

        self.profile = ProfileFactory.create()
        self.performer = PersonaFactory.create(performer_profile=self.profile,
                                               contact=self.profile)
        self.current_act = ActFactory.create(performer=self.performer,
                                             submitted=True)
        self.current_act.conference = self.current_conf
        self.current_act.title = "Current Act"
        self.current_act.save()
        self.previous_act = ActFactory.create(performer=self.performer,
                                              submitted=True)
        self.previous_act.title = 'Previous Act'
        self.previous_act.conference = self.previous_conf
        self.previous_act.save()
        self.current_class = ClassFactory.create(teacher=self.performer,
                                                 submitted=True)
        self.current_class.title = "Current Class"
        self.current_class.conference = self.current_conf
        self.current_class.save()
        self.previous_class = ClassFactory.create(teacher=self.performer,
                                                  submitted=True)
        self.previous_class.conference = self.previous_conf
        self.previous_class.title = 'Previous Class'
        self.previous_class.save()
        self.current_vendor = VendorFactory.create(profile=self.profile,
                                                   submitted=True)
        self.current_vendor.conference = self.current_conf
        self.current_vendor.title = "Current Vendor"
        self.current_vendor.save()
        self.previous_vendor = VendorFactory.create(profile=self.profile,
                                                    submitted=True)
        self.previous_vendor.conference = self.previous_conf
        self.previous_vendor.title = 'Previous Vendor'
        self.previous_vendor.save()
        self.current_costume = CostumeFactory.create(profile=self.profile,
                                                     submitted=True)
        self.current_costume.conference = self.current_conf
        self.current_costume.title = "Current Costume"
        self.current_costume.save()
        self.previous_costume = CostumeFactory.create(profile=self.profile,
                                                      submitted=True)
        self.previous_costume.conference = self.previous_conf
        self.previous_costume.title = 'Previous Costume'
        self.previous_costume.save()
        self.current_volunteer = VolunteerFactory.create(profile=self.profile,
                                                         submitted=True)
        self.current_volunteer.conference = self.current_conf
        self.current_volunteer.save()
        self.previous_volunteer = VolunteerFactory.create(profile=self.profile,
                                                          submitted=True)
        self.previous_volunteer.conference = self.previous_conf
        self.previous_volunteer.save()

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        request = self.factory.get('/')
        request.user = self.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = landing_page(request)
        self.assertEqual(response.status_code, 200)
        content = response.content
        does_not_show_previous = (
            self.previous_act.title not in content and
            self.previous_class.title not in content and
            self.previous_vendor.title not in content and
            self.previous_costume.title not in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.previous_volunteer.id]) not in content)
        shows_all_current = (
            self.current_act.title in content and
            self.current_class.title in content and
            self.current_vendor.title in content and
            self.current_costume.title in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.current_volunteer.id]) in content)
        nt.assert_true(does_not_show_previous and
                       shows_all_current)

    def test_historical_view(self):
        request = self.factory.get('/')
        request.user = self.profile.user_object
        request.GET = {'historical': 1}
        request.session = {'cms_admin_site': 1}
        response = landing_page(request)
        content = response.content
        self.assertEqual(response.status_code, 200)
        shows_all_previous = (
            self.previous_act.title in content and
            self.previous_class.title in content and
            self.previous_vendor.title in content and
            self.previous_costume.title in content in content)
        does_not_show_current = (
            self.current_act.title not in content and
            self.current_class.title not in content and
            self.current_vendor.title not in content and
            self.current_costume.title not in content)
        nt.assert_true(shows_all_previous and
                       does_not_show_current)
