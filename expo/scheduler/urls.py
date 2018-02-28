from django.conf.urls import patterns, include, url

from django.contrib.auth.views import *
from scheduler import views

urlpatterns = patterns(
    '',
    url(r'^scheduler/acts/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/acts/(?P<show_id>\d+)/?$',
        views.schedule_acts, name='schedule_acts'),
    url(r'^scheduler/contactinfo/(\d+)/?$',
        views.contact_info, name='contact_info'),
    url(r'^scheduler/contactinfo/(\d+)/([-\w]+)/?$',
        views.contact_info, name='contact_info'),
    url(r'^scheduler/contact_by_role/([-\w]+)/?$',
        views.contact_by_role, name='contact_by_role'),
    url(r'^scheduler/export_calendar/?$',
        views.export_calendar, name='export_calendar'),
)
