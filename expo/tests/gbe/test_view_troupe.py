import nose.tools as nt
from unittest import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_troupe
from tests.factories.gbe_factories import (
    TroupeFactory,
    PersonaFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    is_profile_update_page,
)


class TestViewTroupe(TestCase):
    '''Tests for view_troupe view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_view_troupe(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        request = self.factory.get('/troupe/view/%d' % troupe.resourceitem_id)
        request.session = {'cms_admin_site': 1}
        request.user = contact.profile.user_object
        response = view_troupe(request, troupe.resourceitem_id)
        self.assertEqual(response.status_code, 200)

    def test_no_profile(self):
        troupe = TroupeFactory()
        user = UserFactory()
        request = self.client.get(reverse(
            "troupe_view",
            args=[troupe.resourceitem_id],
            urlconf="gbe.urls"),
                               follow=True)
        request.session = {'cms_admin_site': 1}
        request.user = user
        response = view_troupe(request,
                               troupe.resourceitem_id)
        nt.assert_equal(302, response.status_code)
        # this is not ideal, we should be getting the redirect page, but
        # I'm having trouble with the follow parameter.
        # Good enough for now.
