from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_act_techinfo
import mock
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    ActFactory,
    ShowFactory,
    PersonaFactory,
    RoomFactory,
)
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)
from scheduler.models import (
    Event as sEvent,
)

class TestEditActTechInfo(TestCase):
    '''Tests for edit_act_techinfo view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()


    def test_edit_act_techinfo_authorized_user(self):
        act = ActFactory.create()
        show = ShowFactory.create()
        room = conf.Room(name="Theater", capacity=200, overbook_size=200)
        room.save()
        show.acts.add(act)
        show_event = sEvent(eventitem=show,
                            starttime="2015-01-01 01:01Z",
                            max_volunteer=0)
        show_event.save()
        show_event.set_location(room)
        
        request= self.factory.get('/acttechinfo/edit/%d' %act.pk)
        request.user =  act.performer.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        mock_get_shows = mock.MagicMock(return_value = [show_event])
        with mock.patch ('scheduler.models.ActItem.get_scheduled_shows',
                          mock_get_shows):
            response = edit_act_techinfo(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_false('In lists of choices:' in response.content)
