from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()
from gbe import report_views as reporting

urlpatterns = patterns('',
                       url(r'^reports/?$',
                           reporting.list_reports, name = 'report_list'),
                       url(r'^reports/staff_area/?$',
                           reporting.review_staff_area, name = 'staff_area'),
                       url(r'^reports/staff_area/(\d+)/?$',
                           reporting.staff_area, name = 'staff_area'),
                       url(r'^reports/stuffing/?$', 
                           reporting.env_stuff, name = 'env_stuff'),
#                       url(r'^schedule/personal/(?<userid>[\d+])/?$',
#                           reporting.personal_schedule, name = 'personal_schedule'),
#                       url(r'^schedule/personal/(?<username>[\d\w]+)/?$',
#                           reporting.personal_schedule, name = 'personal_schedule'),
                       url(r'^reports/schedule/room/?$', 
                           reporting.room_schedule, name = 'room_schedule'),
                       url(r'^reports/schedule/room/(\d+)/?$', 
                           reporting.room_schedule, name = 'room_schedule'),
                       url(r'^reports/setup/room/?$', 
                           reporting.room_setup, name = 'room_setup'),

                        url(r'^reports/acttechinfo/view_summary/(\d+)/?$',
                            reporting.review_act_techinfo, name = 'act_techinfo_review'),
                        url(r'^reports/acttechinfo/view_summary/?$',
                            reporting.review_act_techinfo, name = 'act_techinfo_review'),
                         url(r'^reports/acttechinfo/view_details/(\d+)/?$',
                            reporting.export_act_techinfo, name = 'act_techinfo_download'),
                        

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
