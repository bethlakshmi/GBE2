from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from gbe.reporting.views import (
    review_staff_area,
    staff_area,
    volunteer_type,
)
from gbe.reporting import (
    download_tracks_for_show,
    env_stuff,
    export_act_techinfo,
    export_badge_report,
    list_reports,
    personal_schedule,
    review_act_techinfo,
    room_schedule,
    room_setup,
    view_techinfo,
)
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^reports/?$',
        list_reports,
        name='report_list'),
    url(r'^reports/staff_area/?$',
        review_staff_area,
        name='staff_area'),
    url(r'^reports/staff_area/(\d+)/?$',
        staff_area,
        name='staff_area'),
    url(r'^reports/volunteer_type/(?P<conference_choice>[-\w]+)/' +
        '(?P<eventitem_id>\d+)/?$',
        volunteer_type,
        name='volunteer_type'),
    url(r'^reports/stuffing/(?P<conference_choice>[-\w]+)/?$',
        env_stuff,
        name='env_stuff'),
    url(r'^reports/stuffing/?$',
        env_stuff,
        name='env_stuff'),
    url(r'^reports/schedule/all/?$',
        personal_schedule,
        name='personal_schedule'),
    url(r'^reports/schedule/room/?$',
        room_schedule, name='room_schedule'),
    url(r'^reports/schedule/room/(\d+)/?$',
        room_schedule, name='room_schedule'),
    url(r'^reports/setup/room/?$',
        room_setup, name='room_setup'),
    url(r'^reports/download_tracks_for_show/(\d+)/?$',
        download_tracks_for_show,
        name='download_tracks_for_show'),

    url(r'^reports/acttechinfo/view_summary/(\d+)/?$',
        review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_summary/?$',
        review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_details/(\d+)/?$',
        export_act_techinfo,
        name='act_techinfo_download'),

    url(r'^reports/badges/print_run/(?P<conference_choice>[-\w]+)/?$',
        export_badge_report, name='badge_report'),
    url(r'^reports/badges/print_run/?$',
        export_badge_report, name='badge_report'),

    url(r'^reports/view_techinfo/?$',
        view_techinfo, name='view_techinfo'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
