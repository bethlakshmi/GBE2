from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from gbe import reporting
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^reports/?$',
        reporting.list_reports,
        name='report_list'),
    url(r'^reports/staff_area/?$',
        reporting.review_staff_area,
        name='staff_area'),
    url(r'^reports/staff_area/(\d+)/?$',
        reporting.staff_area,
        name='staff_area'),
    url(r'^reports/stuffing/(?P<conference_choice>[-\w]+)/?$',
        reporting.env_stuff,
        name='env_stuff'),
    url(r'^reports/stuffing/?$',
        reporting.env_stuff,
        name='env_stuff'),
    url(r'^reports/schedule/all/?$',
        reporting.personal_schedule,
        name='personal_schedule'),
    url(r'^reports/schedule/room/?$',
        reporting.room_schedule, name='room_schedule'),
    url(r'^reports/schedule/room/(\d+)/?$',
        reporting.room_schedule, name='room_schedule'),
    url(r'^reports/setup/room/?$',
        reporting.room_setup, name='room_setup'),
    url(r'^reports/download_tracks_for_show/(\d+)/?$',
        reporting.download_tracks_for_show,
        name='download_tracks_for_show'),

    url(r'^reports/acttechinfo/view_summary/(\d+)/?$',
        reporting.review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_summary/?$',
        reporting.review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_details/(\d+)/?$',
        reporting.export_act_techinfo,
        name='act_techinfo_download'),

    url(r'^reports/badges/print_run/(?P<conference_choice>[-\w]+)/?$',
        reporting.export_badge_report, name='badge_report'),
    url(r'^reports/badges/print_run/?$',
        reporting.export_badge_report, name='badge_report'),

    url(r'^reports/view_techinfo/?$',
        reporting.view_techinfo, name='view_techinfo'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
