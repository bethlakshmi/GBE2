from django.core.exceptions import PermissionDenied
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import Group
from gbe.report_views import export_badge_report
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import login_as


class TestExportBadgeReport(TestCase):
    '''Tests for export_badge_report in report view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Registrar')
        self.privileged_user.groups.add(group)


    @nt.raises(PermissionDenied)
    def test_export_badge_report_is_not_registrar(self):
        user = factories.ProfileFactory.create().user_object
        request = self.factory.get('reports/badges/print_run/')
        request.user = user
        response = export_badge_report(request)


    def test_export_badge_report_no_conf(self):
        user = self.privileged_user
        request = self.factory.get('reports/badges/print_run/')
        request.user = user
        response = export_badge_report(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=print_badges.csv")

    def test_export_badge_report_pick_conf(self):
        user = self.privileged_user
        request = self.factory.get('reports/badges/print_run/GBE2016')
        request.user = user
        response = export_badge_report(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=print_badges.csv")
