from django.http import Http404
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client

from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory
)
from tests.functions.scheduler_functions import (
    book_act_item_for_show,
    book_worker_item_for_role)


class TestGetRoles(TestCase):
    '''Tests that a profile will return all the possible roles'''

    def setUp(self):
        self.conference = ConferenceFactory.create()

    def test_basic_profile(self):
        '''
           Simplest user - just has a profile, doesn't have any role
        '''
        profile = ProfileFactory.create()
        result = profile.get_roles(self.conference)
        nt.assert_equal(len(result), 0)

    def test_basic_persona(self):
        '''
           Has a performer/teacher identity, but no commitment so no role
        '''
        persona = PersonaFactory.create()
        result = persona.performer_profile.get_roles(self.conference)
        nt.assert_equal(len(result), 0)

    def test_unbooked_performer(self):
        '''
            Submitted an act, didn't make it to a show
        '''
        act = ActFactory.create(conference=self.conference)
        profile = act.performer.performer_profile
        result = profile.get_roles(self.conference)
        nt.assert_equal(len(result), 0)

    def test_booked_performer(self):
        '''
           has the role of performer from being booked in a show
        '''
        act = ActFactory.create(conference=self.conference,
                                accepted=3)
        show = ShowFactory.create(conference=self.conference)
        booking = book_act_item_for_show(
            act,
            show)
        profile = act.performer.performer_profile
        result = profile.get_roles(self.conference)
        nt.assert_equal(result, ["Performer"])

    def test_teacher(self):
        '''
           has the role of a teacher, persona is booked for a class
        '''
        persona = PersonaFactory.create()
        booking = book_worker_item_for_role(
            persona,
            "Teacher")
        result = persona.performer_profile.get_roles(
            booking.event.eventitem.conference)
        nt.assert_equal(result, ["Teacher"])

    def test_overcommitment_addict(self):
        '''
           1 of every permutation possible to link people to roles
        '''
        persona = PersonaFactory.create()
        this_class = GenericEventFactory.create(
            conference=self.conference)
        book_worker_item_for_role(
            persona,
            "Teacher",
            this_class)
        event = GenericEventFactory.create(
            conference=self.conference)
        book_worker_item_for_role(
            persona.performer_profile,
            "Staff Lead",
            event)
        act = ActFactory.create(conference=self.conference,
                                accepted=3,
                                performer=persona)
        show = ShowFactory.create(conference=self.conference)
        booking = book_act_item_for_show(act, show)

        result = persona.performer_profile.get_roles(
            self.conference)
        nt.assert_equal(sorted(result),
                        ["Performer", "Staff Lead", "Teacher"])
