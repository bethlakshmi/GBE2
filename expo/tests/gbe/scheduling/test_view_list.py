from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.functions.gbe_functions import (
    clear_conferences,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory,
    ShowFactory,
    GenericEventFactory,
)
import nose.tools as nt


class TestViewList(TestCase):

    def setUp(self):
        clear_conferences()
        self.client = Client()
        self.conf = ConferenceFactory()

    def test_view_list_given_slug(self):
        other_conf = ConferenceFactory()
        this_class = ClassFactory.create(accepted=3,
                                         e_conference=self.conf,
                                         b_conference=self.conf)
        that_class = ClassFactory.create(accepted=3,
                                         e_conference=other_conf,
                                         b_conference=other_conf)
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Class"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        nt.assert_true(this_class.e_title in response.content)
        nt.assert_false(that_class.e_title in response.content)

    def test_view_list_default_view_current_conf_exists(self):
        '''
        /scheduler/view_list/ should return all events in the current
        conference, assuming a current conference exists
        '''
        other_conf = ConferenceFactory(status='completed')
        show = ShowFactory(e_conference=self.conf)
        generic_event = GenericEventFactory(e_conference=self.conf)
        accepted_class = ClassFactory(accepted=3,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        previous_class = ClassFactory(accepted=3,
                                      e_conference=other_conf,
                                      b_conference=other_conf)
        rejected_class = ClassFactory(accepted=1,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_true(generic_event.e_title in response.content)
        nt.assert_true(show.e_title in response.content)
        nt.assert_true(accepted_class.e_title in response.content)
        nt.assert_false(rejected_class.e_title in response.content)
        nt.assert_false(previous_class.e_title in response.content)

    def test_no_avail_conf(self):
        clear_conferences()
        login_as(ProfileFactory(), self)
        response = self.client.get(
            reverse("event_list",
                    urlconf="gbe.scheduling.urls"))
        self.assertEqual(404, response.status_code)

    def test_view_list_event_type_not_case_sensitive(self):
        param = 'class'
        url_lower = reverse("event_list",
                            urlconf="gbe.scheduling.urls",
                            args=[param.lower()])

        url_upper = reverse("event_list",
                            urlconf="gbe.scheduling.urls",
                            args=[param.upper()])

        assert (self.client.get(url_lower).content ==
                self.client.get(url_upper).content)

    def test_view_list_event_type_not_in_list_titles(self):
        param = 'classification'
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=[param])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_view_list_only_classes(self):
        '''
        /scheduler/view_list/ should return all events in the current
        conference, assuming a current conference exists
        '''
        show = ShowFactory(e_conference=self.conf)
        generic_event = GenericEventFactory(e_conference=self.conf)
        accepted_class = ClassFactory(accepted=3,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_false(show.e_title in response.content)
        nt.assert_true(accepted_class.e_title in response.content)
