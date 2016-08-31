import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)
from gbe.models import (
    Class,
    GenericEvent,
    Show,
)
from django.core.urlresolvers import reverse


class TestCreateEvent(TestCase):
    '''Tests for create_event view'''
    view_name = 'create_event'

    def setUp(self):
        self.url = reverse(
            self.view_name,
            args=['Show'],
            urlconf='gbe.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        current_conference()
        Show.objects.all().delete()
        GenericEvent.objects.all().delete()
        Class.objects.all().delete()

    def post_data(self, event_type='Show'):
        data = {
            'title': 'The Big %s' % event_type,
            'description': 'This is a description',
            'duration': '2:00:00'
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        nt.assert_equal(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        nt.assert_equal(response.status_code, 200)

    def test_auth_user_can_create_show(self):
        login_as(self.privileged_user, self)
        data = self.post_data()
        response = self.client.post(
            self.url,
            data=data)
        nt.assert_true(Show.objects.filter(title=data['title']).count() > 0)

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        data = self.post_data()
        del data['duration']
        response = self.client.post(
            self.url,
            data=data)
        nt.assert_false(Show.objects.filter(title=data['title']).exists())

    def test_event_w_location(self):
        url = reverse(
            self.view_name,
            args=['GenericEvent'],
            urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.post_data('GenericEvent')
        room = RoomFactory()
        data['default_location'] = room.pk
        data['type'] = 'Special'
        response = self.client.post(
            url,
            data=data,
            follow=True)
        assert "Events Information" in response.content
        assert str(room) in response.content
        nt.assert_true(GenericEvent.objects.filter(
            title=data['title'],
            default_location=room).count() > 0)

    def test_event_w_no_location(self):
        url = reverse(
            self.view_name,
            args=['GenericEvent'],
            urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.post_data('GenericEvent')
        data['type'] = 'Special'
        data['room'] = ''
        response = self.client.post(
            url,
            data=data,
            follow=True)
        assert "Events Information" in response.content
        nt.assert_true(GenericEvent.objects.filter(
            title=data['title'],
            default_location__isnull=True).count() > 0)

    def test_create_class(self):
        url = reverse(
            self.view_name,
            args=['Class'],
            urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.post_data('Class')
        data['accepted'] = '3'
        data['teacher'] = self.performer.pk
        response = self.client.post(
            url,
            data=data,
            follow=True)
        assert "Events Information" in response.content
        nt.assert_true(Class.objects.filter(
            title=data['title']).count() > 0)
