from gbe.models import (
    Conference
)

from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory,
    ShowFactory,
    GenericEventFactory,
)
from django.test import (
    TestCase,
    Client
)
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from scheduler.views import view_list
import nose.tools as nt


def test_view_list_given_slug():
    conf = ConferenceFactory.create()
    other_conf = ConferenceFactory.create()
    this_class = ClassFactory.create(accepted=3)
    this_class.conference = conf
    this_class.title = "xyzzy"
    this_class.save()
    that_class = ClassFactory.create(accepted=3)
    that_class.conference = other_conf
    that_class.title = "plugh"
    that_class.save()
    request = RequestFactory().get(
        reverse("event_list",
                urlconf="scheduler.urls",
                args=["Class"]),
        data={"conference": conf.conference_slug})
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site': 1}
    response = view_list(request, "Class")
    nt.assert_true(this_class.title in response.content)
    nt.assert_false(that_class.title in response.content)


def test_view_list_default_view_current_conf_exists():
    '''
    /scheduler/view_list/ should return all events in the current
    conference, assuming a current conference exists
    '''
    Conference.objects.all().delete()
    conf = ConferenceFactory.create()
    other_conf = ConferenceFactory.create(status='completed')
    show = ShowFactory()
    show.conference = conf
    show.title = "the show"
    show.save()
    generic_event = GenericEventFactory.create()
    generic_event.conference = conf
    generic_event.title = "genericevent"
    generic_event.save()
    accepted_class = ClassFactory(accepted=3)
    accepted_class.conference = conf
    accepted_class.title = 'accepted'
    accepted_class.save()
    previous_class = ClassFactory(accepted=3)
    previous_class.conference = other_conf
    previous_class.title = 'previous'
    previous_class.save()
    rejected_class = ClassFactory(accepted=1)
    rejected_class.conference = conf
    rejected_class.title = 'reject'
    rejected_class.save()
    request = RequestFactory().get(
        reverse("event_list",
                urlconf="scheduler.urls"))
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site': 1}
    response = view_list(request)
    nt.assert_true(generic_event.title in response.content)
    nt.assert_true(show.title in response.content)
    nt.assert_true(accepted_class.title in response.content)
    nt.assert_false(rejected_class.title in response.content)
    nt.assert_false(previous_class.title in response.content)


def test_view_list_event_type_not_case_sensitive():
    param = 'class'
    request1 = RequestFactory().get(
        reverse("event_list",
                urlconf="scheduler.urls",
                args=[param]))
    request2 = RequestFactory().get(
        reverse("event_list",
                urlconf="scheduler.urls",
                args=[param.upper()]))

    request1.user = ProfileFactory.create().user_object
    request2.user = ProfileFactory.create().user_object
    request1.session = {'cms_admin_site': 1}
    request2.session = {'cms_admin_site': 1}
    nt.assert_equal(view_list(request1).content, view_list(request2).content)



def test_view_list_event_type_not_in_list_titles():
    client = Client()
    param = 'classification'
    url =reverse("event_list",
                 urlconf="scheduler.urls",
                 args=[param])
    user = ProfileFactory().user_object
    password = "password"
    user.set_password('password')
    user.save()
    client.login(username=user.username,
                  email=user.email,
                  password=password)
    response = client.get(url)
    expected_string = "Check out the full list of all shows"
    nt.assert_true(expected_string in response.content)
