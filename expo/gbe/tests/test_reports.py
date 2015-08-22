from django.core.exceptions import PermissionDenied
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
import factories
import functions


class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.profile_factory = factories.ProfileFactory

    @nt.raises(PermissionDenied)
    def test_list_reports_succeed(self):
        '''list_reports view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = list_reports(request)


    def test_list_reports_fail(self):
        '''list_reports view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/')
        functions.login_as(profile, self)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = list_reports(request)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_review_staff_area_not_visible_without_permission(self):
        profile = self.profile_factory.create()
        request = self.factory.get('reports/review_staff_area')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = review_staff_area(request)


    def test_review_staff_area_path(self):
        '''review_staff_area view should load
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/review_staff_area')
        functions.login_as(profile, self)
        request.user = profile.user_object
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
        except PermissionDenied as e:
            pass   # expected
        functions.grant_privilege(profile, 'Act Reviewers')
        response = staff_area(request, show.eventitem_id)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_env_stuff_fail(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/stuffing')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = env_stuff(request)


    def test_env_stuff_succeed(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/stuffing')
        functions.login_as(profile, self)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Registrar')
        response = env_stuff(request)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_personal_schedule_fail(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/schedule_all')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = personal_schedule(request)


    def test_personal_schedule_succeed(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/schedule_all')
        functions.login_as(profile, self)
        request.user = profile.user_object

        functions.grant_privilege(profile, 'Act Reviewers')
        response = personal_schedule(request)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_review_act_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get('reports/review_act_techinfo')
        request.user = profile.user_object
        response = review_act_techinfo(request)


    def test_review_act_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = self.profile_factory.create()
        functions.login_as(profile, self)
        request = self.factory.get('reports/review_act_techinfo')
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Tech Crew')
        response = review_act_techinfo(request)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        response = room_schedule(request)

    def test_room_schedule_succeed(self):
        '''room_schedule view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_schedule')
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        response = room_schedule(request)
        self.assertEqual(response.status_code, 200)



    @nt.raises(PermissionDenied)
    def test_room_setup_not_visible_without_permission(self):
        '''room_setup view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        response = room_setup(request)

    def test_room_setup_visible_with_permission(self):
        '''room_setup view should load for privileged users, 
           and fail for others
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/room_setup')
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Act Reviewers')
        functions.login_as(profile, self)
        response = room_setup(request)
        self.assertEqual(response.status_code, 200)


    @nt.raises(PermissionDenied)
    def test_export_badge_report_succeed(self):
        '''export_badge_report view should load for Registrars
           and fail for other users
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/badges/print_run')
        functions.login_as(profile, self)
        request.user = profile.user_object
        response = export_badge_report(request)

    def test_export_badge_report_fail(self):
        '''export_badge_report view should load for Registrars
           and fail for other users
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('reports/badges/print_run')
        functions.login_as(profile, self)
        request.user = profile.user_object

        functions.grant_privilege(profile, 'Registrar')
        request = self.factory.get('reports/badges/print_run')
        request.user = profile.user_object
        response = export_badge_report(request)
        self.assertEqual(response.status_code, 200)
