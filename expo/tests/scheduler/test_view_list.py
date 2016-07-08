import pytest
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

from scheduler.views import view_list
import nose.tools as nt


class TestViewList(TestCase):

    def setUp(self):
        self.client = Client()

    def test_view_list_given_slug(self):
        conf = ConferenceFactory()
        other_conf = ConferenceFactory()
        this_class = ClassFactory.create(accepted=3,
                                         e_conference=conf,
                                         b_conference=conf)
        that_class = ClassFactory.create(accepted=3,
                                         e_conference=other_conf,
                                         b_conference=other_conf)
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="scheduler.urls",
                      args=["Class"])
        response = self.client.get(
            url,
            data={"conference": conf.conference_slug})
        nt.assert_true(this_class.e_title in response.content)
        nt.assert_false(that_class.e_title in response.content)

    def test_view_list_default_view_current_conf_exists(self):
        '''
        /scheduler/view_list/ should return all events in the current
        conference, assuming a current conference exists
        '''
        clear_conferences()
        conf = ConferenceFactory()
        other_conf = ConferenceFactory(status='completed')
        show = ShowFactory(e_conference=conf)
        generic_event = GenericEventFactory(e_conference=conf)
        accepted_class = ClassFactory(accepted=3,
                                      e_conference=conf,
                                      b_conference=conf)
        previous_class = ClassFactory(accepted=3,
                                      e_conference=other_conf,
                                      b_conference=other_conf)
        rejected_class = ClassFactory(accepted=1,
                                      e_conference=conf,
                                      b_conference=conf)
        url = reverse("event_list",
                      urlconf="scheduler.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_true(generic_event.e_title in response.content)
        nt.assert_true(show.e_title in response.content)
        nt.assert_true(accepted_class.e_title in response.content)
        nt.assert_false(rejected_class.e_title in response.content)
        nt.assert_false(previous_class.e_title in response.content)

    def test_view_list_event_type_not_case_sensitive(self):
        param = 'class'
        password = "password"
        url_lower = reverse("event_list",
                            urlconf="scheduler.urls",
                            args=[param.lower()])

        url_upper = reverse("event_list",
                            urlconf="scheduler.urls",
                            args=[param.upper()])

        assert (self.client.get(url_lower).content ==
                self.client.get(url_upper).content)

    def test_view_list_event_type_not_in_list_titles(self):
        param = 'classification'
        url = reverse("event_list",
                      urlconf="scheduler.urls",
                      args=[param])
        response = self.client.get(url)
        expected_string = "Check out the full list of all shows"
        nt.assert_true(expected_string in response.content)
