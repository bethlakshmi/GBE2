import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from gbe.views import landing_page
from tests.factories.gbe_factories import(
    ConferenceFactory,
    ProfileFactory,
    ActFactory,
    ClassFactory,
    VendorFactory,
    PersonaFactory,
)

class TestIndex(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        profile = ProfileFactory.create()
        request = self.factory.get('/')
        request.user = profile.user_object
        request.session = {'cms_admin_site':1}
        response = landing_page(request)
        self.assertEqual(response.status_code, 200)

    def test_historical_view(self):
        current_conf = ConferenceFactory.create(accepting_bids=True)
        current_conf.status = 'upcoming'
        current_conf.save()
        previous_conf = ConferenceFactory.create(accepting_bids=False)
        previous_conf.status = 'completed'
        previous_conf.save()
        profile = ProfileFactory.create()
        performer = PersonaFactory.create(performer_profile=profile,
                                          contact=profile)
        current_act = ActFactory.create(performer=performer,
                                        submitted=True)
        current_act.conference = current_conf
        current_act.title = "Current Act"
        current_act.save()
        previous_act = ActFactory.create(performer=performer,
                                         submitted=True)
        previous_act.title = 'Previous Act'
        previous_act.conference = previous_conf
        previous_act.save()
        current_class = ClassFactory.create(teacher=performer,
                                            submitted=True)
        current_class.title = "Current Class"
        current_class.conference = current_conf
        current_class.save()
        previous_class = ClassFactory.create(teacher=performer,
                                             submitted=True)
        previous_class.conference = previous_conf
        previous_class.title = 'Previous Class'
        previous_class.save()
        current_vendor = VendorFactory.create(profile=profile,
                                              submitted=True)
        current_vendor.conference = current_conf
        current_vendor.title = "Current Vendor"
        current_vendor.save()
        previous_vendor = VendorFactory.create(profile=profile,
                                               submitted=True)
        previous_vendor.conference = previous_conf
        previous_vendor.title = 'Previous Vendor'
        previous_vendor.save()
        request = self.factory.get('/')
        request.user = profile.user_object
        request.GET = {'historical': 1}
        request.session = {'cms_admin_site':1}
        response = landing_page(request)
        content = response.content
        shows_all_previous = (previous_act.title in content and
                              previous_class.title in content and
                              previous_vendor.title in content)
        does_not_show_current = (current_act.title not in content and
                                 current_class.title not in content and
                                 current_vendor.title not in content)
        nt.assert_true(shows_all_previous and
                       does_not_show_current)
