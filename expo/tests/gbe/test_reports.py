import gbe.models as conf
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.http import Http404
from gbe.report_views import (list_reports,
                              review_staff_area, 
                              staff_area, 
                              env_stuff, 
                              personal_schedule, 
                              review_act_techinfo,
                              export_act_techinfo,
                              room_schedule,
                              room_setup,
                              export_badge_report,
                              )
from tests.factories import gbe_factories as factories
import tests.functions.gbe_functions as functions

class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.profile_factory = factories.ProfileFactory

    def test_list_reports_path(self):
        '''list_reports view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/')
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = list_reports(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = list_reports(request)
        self.assertEqual(response.status_code, 200)


    def test_review_staff_area_path(self):
        '''review_staff_area view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/review_staff_area')
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = review_staff_area(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        response = review_staff_area(request)
        self.assertEqual(response.status_code, 200)

    def test_staff_area_path(self):
        '''staff_area view should load
        '''
        profile = self.profile_factory.create()
        show = factories.ShowFactory.create()
        request = self.factory.get('reports/staff_area/%d' % show.eventitem_id)
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = staff_area(request, show.eventitem_id)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        response = staff_area(request, show.eventitem_id)
        self.assertEqual(response.status_code, 200)


    def test_env_stuff_path(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/stuffing')
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = env_stuff(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Registrar')
        response = env_stuff(request)
        self.assertEqual(response.status_code, 200)


    def test_personal_schedule_path(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/schedule_all')
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = personal_schedule(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)


    def test_review_act_techinfo_path(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get('reports/review_act_techinfo')
        request.user = profile.user_object
        try:
            response = review_act_techinfo(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)


    def test_room_schedule_path(self):
        '''room_schedule view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        try:
            response = room_schedule(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        response = room_schedule(request)
        self.assertEqual(response.status_code, 200)


    def test_room_setup_path(self):
        '''room_setup view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        try:
            response = room_setup(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        response = room_setup(request)
        self.assertEqual(response.status_code, 200)



    def test_export_badge_report_path(self):
        '''export_badge_report view should load for Registrars
           and fail for other users
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/badges/print_run')
        functions.login_as(profile, self)
        request.user = profile.user_object
        try:
            response = export_badge_report(request)
            assertFalse(True)  # should fail!
        except Http404 as e:
            pass   # expected
        functions.grant_privilege(profile, 'Registrar')
        request = self.factory.get('reports/badges/print_run')
        request.user = profile.user_object
        response = export_badge_report(request)
        self.assertEqual(response.status_code, 200)

