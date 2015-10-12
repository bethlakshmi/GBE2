import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_class
from tests.factories import gbe_factories as factories


class TestViewClass(TestCase):
    '''Tests for view_class view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.class_string = 'Tell Us About Your Class'

    def test_view_class(self):
        '''view_class view, success
        '''
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/view/%d' % klass.pk)
        request.user = klass.teacher.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        response = view_class(request, klass.pk)
        self.assertEqual(response.status_code, 200)
