from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory
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
    this_class.conference=conf
    this_class.title="xyzzy"
    this_class.save()
    that_class = ClassFactory.create(accepted=3)
    that_class.conference = other_conf
    that_class.title = "plugh"
    that_class.save()
    request = RequestFactory().get(
        reverse("event_list", 
                urlconf="scheduler.urls", 
                args=["Class"]),
        data={"conference":conf.conference_slug})
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site':1}
    response = view_list(request, "Class")
    nt.assert_true(this_class.title in response.content)
    nt.assert_false(that_class.title in response.content)
        
def test_view_list_default_view_current_conf_exists():
    '''/scheduler/view_list/ should return all events in the current 
    conference, assuming a current conference exists'''
    conf = ConferenceFactory.create()
    other_conf = ConferenceFactory.create(status='completed')
    accepted_class = ClassFactory(conference=conf,
                                  accepted=3)
    previous_class = ClassFactory(conference=other_conf,
                                  accepted=3)
    rejected_class = ClassFactory(conference=conf,
                                  accepted=1)
    request = RequestFactory().get(
        reverse("event_list", 
                urlconf="scheduler.urls"))
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site':1}
    response = view_list(request, "Class")
    nt.assert_true(accepted_class.title in response.content)
    nt.assert_false(rejected_class.title in response.content)
    nt.assert_false(previous_class.title in response.content)
    
